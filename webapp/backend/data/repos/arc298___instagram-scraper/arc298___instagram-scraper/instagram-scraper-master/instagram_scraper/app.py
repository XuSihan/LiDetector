#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import codecs
import configparser
import errno
import glob
from operator import itemgetter
import json
import logging.config
import hashlib
import os
import pickle
import re
import socket
import sys
import textwrap
import time

from urllib.parse import urlparse

import warnings
import threading
import concurrent.futures
import requests
import requests.packages.urllib3.util.connection as urllib3_connection
import tqdm

from instagram_scraper.constants import *

warnings.filterwarnings('ignore')

input_lock = threading.RLock()


class LockedStream(object):
    file = None
    def __init__(self, file):
        self.file = file

    def write(self, x):
        with input_lock:
            self.file.write(x)

    def flush(self):
        return getattr(self.file, 'flush', lambda: None)()

    def fileno(self):
        return self.file.fileno()

def allowed_gai_family():
    family = socket.AF_INET  # force IPv4
    return family

original_stdout, original_stderr = sys.stdout, sys.stderr
sys.stdout, sys.stderr = map(LockedStream, (sys.stdout, sys.stderr))
# Force using IPv4 connections, when the machine where this code runs uses IPv6
urllib3_connection.allowed_gai_family = allowed_gai_family

def threaded_input(prompt):
    with input_lock:
        try:
            with tqdm.external_write_mode():
                original_stdout.write(prompt)
                original_stdout.flush()
                return sys.stdin.readline()
        except AttributeError:
            original_stdout.write('\n')
            original_stdout.write(prompt)
            original_stdout.flush()
            return sys.stdin.readline()

input = threaded_input

class PartialContentException(Exception):
    pass

class InstagramScraper(object):
    """InstagramScraper scrapes and downloads an instagram user's photos and videos"""

    def __init__(self, **kwargs):
        default_attr = dict(username='', usernames=[], filename=None,
                            login_user=None, login_pass=None,
                            followings_input=False, followings_output='profiles.txt',
                            destination='./', logger=None, retain_username=False, interactive=False,
                            quiet=False, maximum=0, media_metadata=False, profile_metadata=False, latest=False,
                            latest_stamps=False, cookiejar=None, filter_location=None, filter_locations=None,
                            media_types=['image', 'video', 'story-image', 'story-video'],
                            tag=False, location=False, search_location=False, comments=False,
                            verbose=0, include_location=False, filter=None, proxies={}, no_check_certificate=False,
                                                        template='{urlname}', log_destination='')

        allowed_attr = list(default_attr.keys())
        default_attr.update(kwargs)

        for key in default_attr:
            if key in allowed_attr:
                self.__dict__[key] = default_attr.get(key)

        # story media type means story-image & story-video
        if 'story' in self.media_types:
            self.media_types.remove('story')
            if 'story-image' not in self.media_types:
                self.media_types.append('story-image')
            if 'story-video' not in self.media_types:
                self.media_types.append('story-video')

        # Read latest_stamps file with ConfigParser
        self.latest_stamps_parser = None
        if self.latest_stamps:
            parser = configparser.ConfigParser()
            parser.read(self.latest_stamps)
            self.latest_stamps_parser = parser
            # If we have a latest_stamps file, latest must be true as it's the common flag
            self.latest = True

        # Set up a logger
        if self.logger is None:
            self.logger = InstagramScraper.get_logger(level=logging.DEBUG, dest=default_attr.get('log_destination'), verbose=default_attr.get('verbose'))

        self.posts = []
        self.stories = []

        self.session = requests.Session()
        if self.no_check_certificate:
            self.session.verify = False

        try:
            if self.proxies and type(self.proxies) == str:
                self.session.proxies = self._get_json(self.proxies)
        except ValueError:
            self.logger.error("Check is valid json type.")
            raise

        self.session.headers = {'user-agent': CHROME_WIN_UA}
        if self.cookiejar and os.path.exists(self.cookiejar):
            with open(self.cookiejar, 'rb') as f:
                self.session.cookies.update(pickle.load(f))
        self.session.cookies.set('ig_pr', '1')
        self.rhx_gis = ""

        self.cookies = None
        self.authenticated = False
        self.logged_in = False
        self.last_scraped_filemtime = 0
        self.initial_scraped_filemtime = 0
        if default_attr['filter']:
            self.filter = list(self.filter)
        self.quit = False

    def _get_json(self, text):
        try:
            return json.loads(text)
        except json.JSONDecodeError as error:
            self.logger.error('Text is not json: ' + text)
            raise

    def sleep(self, secs):
        min_delay = 1
        for _ in range(secs // min_delay):
            time.sleep(min_delay)
            if self.quit:
                return
        time.sleep(secs % min_delay)

    def _retry_prompt(self, url, exception_message):
        """Show prompt and return True: retry, False: ignore, None: abort"""
        answer = input( 'Repeated error {0}\n(A)bort, (I)gnore, (R)etry or retry (F)orever?'.format(exception_message) )
        if answer:
            answer = answer[0].upper()
            if answer == 'I':
                self.logger.info( 'The user has chosen to ignore {0}'.format(url) )
                return False
            elif answer == 'R':
                return True
            elif answer == 'F':
                self.logger.info( 'The user has chosen to retry forever' )
                global MAX_RETRIES
                MAX_RETRIES = sys.maxsize
                return True
            else:
                self.logger.info( 'The user has chosen to abort' )
                return None

    def safe_get(self, *args, **kwargs):
        # out of the box solution
        # session.mount('https://', HTTPAdapter(max_retries=...))
        # only covers failed DNS lookups, socket connections and connection timeouts
        # It doesnt work when server terminate connection while response is downloaded
        retry = 0
        retry_delay = RETRY_DELAY
        while True:
            if self.quit:
                return
            try:
                response = self.session.get(timeout=CONNECT_TIMEOUT, cookies=self.cookies, *args, **kwargs)
                if response.status_code == 404:
                    return
                response.raise_for_status()
                content_length = response.headers.get('Content-Length')
                if content_length is not None and len(response.content) != int(content_length):
                    #if content_length is None we repeat anyway to get size and be confident
                    raise PartialContentException('Partial response')
                return response
            except (KeyboardInterrupt):
                raise
            except (requests.exceptions.RequestException, PartialContentException) as e:
                if 'url' in kwargs:
                    url = kwargs['url']
                elif len(args) > 0:
                    url = args[0]
                if retry < MAX_RETRIES:
                    self.logger.warning('Retry after exception {0} on {1}'.format(repr(e), url))
                    self.sleep(retry_delay)
                    retry_delay = min( 2 * retry_delay, MAX_RETRY_DELAY )
                    retry = retry + 1
                    continue
                else:
                    keep_trying = self._retry_prompt(url, repr(e))
                    if keep_trying == True:
                        retry = 0
                        continue
                    elif keep_trying == False:
                        return
                raise

    def get_json(self, *args, **kwargs):
        """Retrieve text from url. Return text as string or None if no data present """
        resp = self.safe_get(*args, **kwargs)

        if resp is not None:
            text = resp.text
            try:
                j = json.loads(text)
                if isinstance(j, list):
                    j = j[0]
                if isinstance(j, str):
                    j = json.loads(j)
                if j['status'] == 'fail':
                    self.logger.error(j['message'])
                    return None
            except:
                pass
            return text

    def authenticate_as_guest(self):
        """Authenticate as a guest/non-signed in user"""
        self.session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        self.session.headers.update({'user-agent': CHROME_WIN_UA})
        self.rhx_gis = ""
        self.authenticated = True

    def authenticate_with_login(self):
        """Logs in to instagram."""
        self.session.headers.update({'Referer': BASE_URL, 'user-agent': STORIES_UA})
        req = self.session.get(BASE_URL)

        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken']})

        login_data = {'username': self.login_user, 'password': self.login_pass}
        login = self.session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        self.cookies = login.cookies
        login_text = self._get_json(login.text)

        if login_text.get('authenticated') and login.status_code == 200:
            self.authenticated = True
            self.logged_in = True
            self.session.headers.update({'user-agent': CHROME_WIN_UA})
            self.rhx_gis = ""
        else:
            self.logger.error('Login failed for ' + self.login_user)

            if 'checkpoint_url' in login_text:
                checkpoint_url = login_text.get('checkpoint_url')
                self.logger.error('Please verify your account at ' + BASE_URL[0:-1] + checkpoint_url)

                if self.interactive is True:
                    self.login_challenge(checkpoint_url)
            elif 'errors' in login_text:
                for count, error in enumerate(login_text['errors'].get('error')):
                    count += 1
                    self.logger.debug('Session error %(count)s: "%(error)s"' % locals())
            elif 'status' in login_text and login_text['status'] == 'fail' and 'message' in login_text:
                self.logger.error(login_text['message'])
            else:
                self.logger.error(json.dumps(login_text))
            sys.exit(1)

    def login_challenge(self, checkpoint_url):
        self.session.headers.update({'Referer': BASE_URL})
        req = self.session.get(BASE_URL[:-1] + checkpoint_url)
        self.session.headers.update({'X-CSRFToken': req.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})

        self.session.headers.update({'Referer': BASE_URL[:-1] + checkpoint_url})
        mode = int(input('Choose a challenge mode (0 - SMS, 1 - Email): '))
        challenge_data = {'choice': mode}
        challenge = self.session.post(BASE_URL[:-1] + checkpoint_url, data=challenge_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': challenge.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})

        code = int(input('Enter code received: '))
        code_data = {'security_code': code}
        code = self.session.post(BASE_URL[:-1] + checkpoint_url, data=code_data, allow_redirects=True)
        self.session.headers.update({'X-CSRFToken': code.cookies['csrftoken']})
        self.cookies = code.cookies
        code_text = self._get_json(code.text)

        if code_text.get('status') == 'ok':
            self.authenticated = True
            self.logged_in = True
        elif 'errors' in code.text:
            for count, error in enumerate(code_text['challenge']['errors']):
                count += 1
                self.logger.error('Session error %(count)s: "%(error)s"' % locals())
        else:
            self.logger.error(json.dumps(code_text))

    def logout(self):
        """Logs out of instagram."""
        if self.logged_in:
            try:
                logout_data = {'csrfmiddlewaretoken': self.cookies['csrftoken']}
                self.session.post(LOGOUT_URL, data=logout_data)
                self.authenticated = False
                self.logged_in = False
            except requests.exceptions.RequestException:
                self.logger.warning('Failed to log out ' + self.login_user)

    def get_dst_dir(self, username):
        """Gets the destination directory and last scraped file time."""
        if self.destination == './':
            dst = './' + username
        else:
            if self.retain_username:
                dst = self.destination + '/' + username
            else:
                dst = self.destination

        # Resolve last scraped filetime
        if self.latest_stamps_parser:
            self.last_scraped_filemtime = self.get_last_scraped_timestamp(username)
            self.initial_scraped_filemtime = self.last_scraped_filemtime
        elif os.path.isdir(dst):
            self.last_scraped_filemtime = self.get_last_scraped_filemtime(dst)

        return dst

    def make_dir(self, dst):
        try:
            os.makedirs(dst)
        except OSError as err:
            if err.errno == errno.EEXIST and os.path.isdir(dst):
                # Directory already exists
                pass
            else:
                # Target dir exists as a file, or a different error
                raise

    def get_last_scraped_timestamp(self, username):
        if self.latest_stamps_parser:
            try:
                return self.latest_stamps_parser.getint(LATEST_STAMPS_USER_SECTION, username)
            except configparser.Error:
                pass
        return 0

    def set_last_scraped_timestamp(self, username, timestamp):
        if self.latest_stamps_parser:
            if not self.latest_stamps_parser.has_section(LATEST_STAMPS_USER_SECTION):
                self.latest_stamps_parser.add_section(LATEST_STAMPS_USER_SECTION)
            self.latest_stamps_parser.set(LATEST_STAMPS_USER_SECTION, username, str(timestamp))
            with open(self.latest_stamps, 'w') as f:
                self.latest_stamps_parser.write(f)

    def get_last_scraped_filemtime(self, dst):
        """Stores the last modified time of newest file in a directory."""
        list_of_files = []
        file_types = ('*.jpg', '*.mp4')

        for type in file_types:
            list_of_files.extend(glob.glob(dst + '/' + type))

        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getmtime)
            return int(os.path.getmtime(latest_file))
        return 0

    def query_followings_gen(self, username, end_cursor=''):
        """Generator for followings."""
        user = self.get_shared_data_userinfo(username)
        id = user['id']
        followings, end_cursor = self.__query_followings(id, end_cursor)


        if followings:
            while True:
                for following in followings:
                    yield following
                if end_cursor:
                    followings, end_cursor = self.__query_followings(id, end_cursor)
                else:
                    return

    def __query_followings(self, id, end_cursor=''):
        params = QUERY_FOLLOWINGS_VARS.format(id, end_cursor)
        resp = self.get_json(QUERY_FOLLOWINGS.format(params))

        if resp is not None:
            payload = self._get_json(resp)['data']['user']['edge_follow']
            if payload:
                end_cursor = payload['page_info']['end_cursor']
                followings = []
                for node in payload['edges']:
                    followings.append(node['node']['username'])
                return followings, end_cursor
        return None, None

    def query_comments_gen(self, shortcode, end_cursor=''):
        """Generator for comments."""
        comments, end_cursor = self.__query_comments(shortcode, end_cursor)

        if comments:
            try:
                while True:
                    for item in comments:
                        yield item

                    if end_cursor:
                        comments, end_cursor = self.__query_comments(shortcode, end_cursor)
                    else:
                        return
            except ValueError:
                self.logger.exception('Failed to query comments for shortcode ' + shortcode)

    def __query_comments(self, shortcode, end_cursor=''):
        params = QUERY_COMMENTS_VARS.format(shortcode, end_cursor)
        self.update_ig_gis_header(params)

        resp = self.get_json(QUERY_COMMENTS.format(params))

        if resp is not None:
            payload = self._get_json(resp)['data']['shortcode_media']

            if payload:
                container = payload['edge_media_to_comment']
                comments = [node['node'] for node in container['edges']]
                end_cursor = container['page_info']['end_cursor']
                return comments, end_cursor

        return None, None

    def scrape_hashtag(self):
        self.__scrape_query(self.query_hashtag_gen)

    def scrape_location(self):
        self.__scrape_query(self.query_location_gen)

    def worker_wrapper(self, fn, *args, **kwargs):
        try:
            if self.quit:
                return
            return fn(*args, **kwargs)
        except:
            self.logger.debug("Exception in worker thread", exc_info=sys.exc_info())
            raise

    def __scrape_query(self, media_generator, executor=concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS)):
        """Scrapes the specified value for posted media."""
        self.quit = False
        try:
            for value in self.usernames:
                self.posts = []
                self.stories = []
                self.last_scraped_filemtime = 0
                greatest_timestamp = 0
                future_to_item = {}

                dst = self.get_dst_dir(value)

                if self.include_location:
                    media_exec = concurrent.futures.ThreadPoolExecutor(max_workers=5)

                iter = 0
                for item in tqdm.tqdm(media_generator(value), desc='Searching {0} for posts'.format(value), unit=" media",
                                      disable=self.quiet):

                    if self.filter_locations:
                        if item.get("location") is None or self.get_key_from_value(self.filter_locations, item["location"].get("id")) is None:
                            continue
                    if ((item['is_video'] is False and 'image' in self.media_types) or \
                                (item['is_video'] is True and 'video' in self.media_types)
                        ) and self.is_new_media(item):
                        future = executor.submit(self.worker_wrapper, self.download, item, dst)
                        future_to_item[future] = item

                    if self.include_location and 'location' not in item:
                        media_exec.submit(self.worker_wrapper, self.__get_location, item)

                    if self.comments:
                        item['edge_media_to_comment']['data'] = list(self.query_comments_gen(item['shortcode']))

                    if self.media_metadata or self.comments or self.include_location:
                        if self.latest_stamps_parser and self.initial_scraped_filemtime > self.__get_timestamp(item):
                            pass
                        else:
                            self.posts.append(item)

                    iter = iter + 1
                    if self.maximum != 0 and iter >= self.maximum:
                        break

                if future_to_item:
                    for future in tqdm.tqdm(concurrent.futures.as_completed(future_to_item),
                                            total=len(future_to_item),
                                            desc='Downloading', disable=self.quiet):
                        item = future_to_item[future]

                        if future.exception() is not None:
                            self.logger.warning(
                                'Media for {0} at {1} generated an exception: {2}'.format(value, item['urls'],
                                                                                          future.exception()))
                        else:
                            timestamp = self.__get_timestamp(item)
                            if timestamp > greatest_timestamp:
                                greatest_timestamp = timestamp
                # Even bother saving it?
                if greatest_timestamp > self.last_scraped_filemtime:
                    self.set_last_scraped_timestamp(value, greatest_timestamp)

                self._persist_metadata(dst, value)

        finally:
            self.quit = True

    def query_hashtag_gen(self, hashtag):
        return self.__query_gen(QUERY_HASHTAG, QUERY_HASHTAG_VARS, 'hashtag', hashtag)

    def query_location_gen(self, location):
        return self.__query_gen(QUERY_LOCATION, QUERY_LOCATION_VARS, 'location', location)

    def __query_gen(self, url, variables, entity_name, query, end_cursor=''):
        """Generator for hashtag and location."""
        nodes, end_cursor = self.__query(url, variables, entity_name, query, end_cursor)

        if nodes:
            try:
                while True:
                    for node in nodes:
                        yield node

                    if end_cursor:
                        nodes, end_cursor = self.__query(url, variables, entity_name, query, end_cursor)
                    else:
                        return
            except ValueError:
                self.logger.exception('Failed to query ' + query)

    def __query(self, url, variables, entity_name, query, end_cursor):
        params = variables.format(query, end_cursor)
        self.update_ig_gis_header(params)

        resp = self.get_json(url.format(params))

        if resp is not None:
            payload = self._get_json(resp)['data'][entity_name]

            if payload:
                nodes = []

                if end_cursor == '':
                    top_posts = payload['edge_' + entity_name + '_to_top_posts']
                    nodes.extend(self._get_nodes(top_posts))

                posts = payload['edge_' + entity_name + '_to_media']

                nodes.extend(self._get_nodes(posts))
                end_cursor = posts['page_info']['end_cursor']
                return nodes, end_cursor

        return None, None

    def _get_nodes(self, container):
        return [self.augment_node(node['node']) for node in container['edges']]

    def augment_node(self, node):
        self.extract_tags(node)

        details = None
        if self.include_location and 'location' not in node:
            details = self.__get_media_details(node['shortcode'])
            node['location'] = details.get('location') if details else None

        if 'urls' not in node:
            node['urls'] = []

        if node['is_video'] and 'video_url' in node:
            node['urls'] = [node['video_url']]
        elif '__typename' in node and node['__typename'] == 'GraphImage':
            node['urls'] = [self.get_original_image(node['display_url'])]
        else:
            if details is None:
                details = self.__get_media_details(node['shortcode'])

            if details:
                if '__typename' in details and details['__typename'] == 'GraphVideo':
                    node['urls'] = [details['video_url']]
                elif '__typename' in details and details['__typename'] == 'GraphSidecar':
                    urls = []
                    for carousel_item in details['edge_sidecar_to_children']['edges']:
                        urls += self.augment_node(carousel_item['node'])['urls']
                    node['urls'] = urls
                elif 'display_url' in details:
                    node['urls'] = [self.get_original_image(details['display_url'])]
                else:
                    for media in (details['carousel_media'] if 'carousel_media' in details else [details]):
                        if media['media_type'] == 2:
                            media_versions = media['video_versions']
                        else:
                            media_versions = media['image_versions2']['candidates']

                            if media['media_type'] != 1:
                                self.logger.warning('Unknown media type: %d for %s' % (media['media_type'], node['shortcode']))

                        best_candidate = media_versions[0]

                        for version in media_versions:
                            if version['height'] > best_candidate['height']:
                                best_candidate = version

                        if best_candidate != media_versions[0]:
                            self.logger.warning('First media version is not the best candidate for ' + node['shortcode'])

                        node['urls'].append(best_candidate['url'])

        return node

    def __get_media_details(self, shortcode):
        resp = self.get_json(VIEW_MEDIA_URL.format(shortcode))

        if resp is not None:
            try:
                return self._get_json(resp)['graphql']['shortcode_media']
            except ValueError:
                # Response wasn't JSON, so maybe it was an HTML page.
                data = resp.split("window.__additionalDataLoaded(")[1].split("});</script>")[0].split('{"graphql":')[1]
                try:
                    return self._get_json(data)['shortcode_media']
                except ValueError:
                    self.logger.error('Failed to get media details for ' + shortcode)
            except KeyError:
                return self._get_json(resp)['items'][0]
        else:
            self.logger.error('Failed to get media details for ' + shortcode)

    def __get_location(self, item):
        code = item.get('shortcode', item.get('code'))

        if code:
            details = self.__get_media_details(code)
            item['location'] = details.get('location') if details else None

    def scrape(self, executor=concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CONCURRENT_DOWNLOADS)):
        """Crawls through and downloads user's media"""
        self.session.headers.update({'user-agent': STORIES_UA})
        try:
            for username in self.usernames:
                self.posts = []
                self.stories = []
                self.last_scraped_filemtime = 0
                greatest_timestamp = 0
                future_to_item = {}

                dst = self.get_dst_dir(username)

                # Get the user metadata.
                user = self.get_shared_data_userinfo(username)

                if not user:
                    self.logger.error(
                        'Error getting user details for {0}. Please verify that the user exists.'.format(username))
                    continue
                elif user and user['is_private']:
                    self.logger.info('User {0} is private'.format(username))

                self.rhx_gis = ""

                self.get_profile_pic(dst, executor, future_to_item, user, username)
                self.get_profile_info(dst, username)

                if self.logged_in:
                    self.get_stories(dst, executor, future_to_item, user, username)

                # Crawls the media and sends it to the executor.
                try:

                    self.get_media(dst, executor, future_to_item, user)

                    # Displays the progress bar of completed downloads. Might not even pop up if all media is downloaded while
                    # the above loop finishes.
                    if future_to_item:
                        for future in tqdm.tqdm(concurrent.futures.as_completed(future_to_item), total=len(future_to_item),
                                                desc='Downloading', disable=self.quiet):
                            item = future_to_item[future]

                            if future.exception() is not None:
                                self.logger.error(
                                    'Media at {0} generated an exception: {1}'.format(item['urls'], future.exception()))
                            else:
                                timestamp = self.__get_timestamp(item)
                                if timestamp > greatest_timestamp:
                                    greatest_timestamp = timestamp
                    # Even bother saving it?
                    if greatest_timestamp > self.last_scraped_filemtime:
                        self.set_last_scraped_timestamp(username, greatest_timestamp)

                    self._persist_metadata(dst, username)

                except ValueError:
                    self.logger.error("Unable to scrape user - %s" % username)
        finally:
            self.quit = True
            self.logout()

    def get_profile_pic(self, dst, executor, future_to_item, user, username):
        if 'image' not in self.media_types:
            return

        if self.logged_in:
            # Try Get the High-Resolution profile picture
            url = USER_INFO.format(user['id'])
            resp = self.get_json(url)

            if resp is None:
                self.logger.error('Error getting user info for {0}'.format(username))
                return

            user_info = self._get_json(resp)['user']

            if 'has_anonymous_profile_picture' in user_info and user_info['has_anonymous_profile_picture']:
                return

            try:
                profile_pic_urls = [
                    user_info['hd_profile_pic_url_info']['url'],
                    user_info['hd_profile_pic_versions'][-1]['url'],
                ]

                profile_pic_url = next(url for url in profile_pic_urls if url is not None)
            except (KeyError, IndexError, StopIteration):
                self.logger.warning('Failed to get high resolution profile picture for {0}'.format(username))
                profile_pic_url = user['profile_pic_url_hd']
        else:
                # If not logged_in take the Low-Resolution profile picture
                profile_pic_url = user['profile_pic_url_hd']

        item = {'urls': [profile_pic_url], 'username': username, 'shortcode':'', 'created_time': 1286323200, '__typename': 'GraphProfilePic'}

        if self.latest is False or os.path.isfile(dst + '/' + item['urls'][0].split('/')[-1]) is False:
            for item in tqdm.tqdm([item], desc='Searching {0} for profile pic'.format(username), unit=" images",
                                  ncols=0, disable=self.quiet):
                future = executor.submit(self.worker_wrapper, self.download, item, dst)
                future_to_item[future] = item

    def get_profile_info(self, dst, username):
        if self.profile_metadata is False:
            return
        url = USER_URL.format(username)
        resp = self.get_json(url)

        if resp is None:
            self.logger.error('Error getting user info for {0}'.format(username))
            return

        self.logger.info( 'Saving metadata general information on {0}.json'.format(username) )

        user_info = self._get_json(resp)['graphql']['user']

        try:
            profile_info = {
                'biography': user_info['biography'],
                'followers_count': user_info['edge_followed_by']['count'],
                'following_count': user_info['edge_follow']['count'],
                'full_name': user_info['full_name'],
                'id': user_info['id'],
                'is_business_account': user_info['is_business_account'],
                'is_joined_recently': user_info['is_joined_recently'],
                'is_private': user_info['is_private'],
                'posts_count': user_info['edge_owner_to_timeline_media']['count'],
                'profile_pic_url': user_info['profile_pic_url'],
                'external_url': user_info['external_url'],
                'business_email': user_info['business_email'],
                'business_phone_number': user_info['business_phone_number'],
                'business_category_name': user_info['business_category_name']
            }
        except (KeyError, IndexError, StopIteration):
            self.logger.warning('Failed to build {0} profile info'.format(username))
            return

        item = {
            'GraphProfileInfo': {
                'info': profile_info,
                'username': username,
                'created_time': 1286323200
            }
        }
        self.save_json(item, '{0}/{1}.json'.format(dst, username))

    def get_stories(self, dst, executor, future_to_item, user, username):
        """Scrapes the user's stories."""
        if self.logged_in and \
                ('story-image' in self.media_types or 'story-video' in self.media_types or 'none' in self.media_types):
            # Get the user's stories.
            all_stories = []
            all_stories.extend(self.fetch_main_stories(user['id']))
            all_stories.extend(self.fetch_highlight_stories(user['id']))

            # Downloads the user's stories and sends it to the executor.
            iter = 0
            for item in tqdm.tqdm(all_stories, desc='Searching {0} for stories'.format(username), unit=" media",
                                  disable=self.quiet):
                if self.story_has_selected_media_types(item) and self.is_new_media(item):
                    item['username'] = username
                    item['shortcode'] = ''
                    future = executor.submit(self.worker_wrapper, self.download, item, dst)
                    future_to_item[future] = item

                iter = iter + 1
                if self.maximum != 0 and iter >= self.maximum:
                    break

    def get_media(self, dst, executor, future_to_item, user):
        """Scrapes the user's posts for media."""
        if 'image' not in self.media_types and 'video' not in self.media_types and 'none' not in self.media_types:
            return

        username = user['username']

        if self.include_location:
            media_exec = concurrent.futures.ThreadPoolExecutor(max_workers=5)

        iter = 0
        for item in tqdm.tqdm(self.query_media_gen(user), desc='Searching {0} for posts'.format(username),
                              unit=' media', disable=self.quiet):
            # -Filter command line
            if self.filter:
                if 'tags' in item:
                    filtered = any(x in item['tags'] for x in self.filter)
                    if self.has_selected_media_types(item) and self.is_new_media(item) and filtered:
                        item['username']=username
                        future = executor.submit(self.worker_wrapper, self.download, item, dst)
                        future_to_item[future] = item
                else:
                    # For when filter is on but media doesnt contain tags
                    pass
            # --------------#
            else:
                if self.has_selected_media_types(item) and self.is_new_media(item):
                    item['username']=username
                    future = executor.submit(self.worker_wrapper, self.download, item, dst)
                    future_to_item[future] = item

            if self.include_location:
                item['username']=username
                media_exec.submit(self.worker_wrapper, self.__get_location, item)

            if self.comments:
                item['username']=username
                item['comments'] = {'data': list(self.query_comments_gen(item['shortcode']))}

            if self.media_metadata or self.comments or self.include_location:
                item['username']=username
                self.posts.append(item)

            iter = iter + 1
            if self.maximum != 0 and iter >= self.maximum:
                break

    def get_shared_data_userinfo(self, username=''):
        """Fetches the user's metadata."""
        resp = self.get_json(BASE_URL + username)

        userinfo = None

        if resp is not None:
            try:
                if "window._sharedData = " in resp:
                    shared_data = resp.split("window._sharedData = ")[1].split(";</script>")[0]
                    if shared_data:
                        userinfo = self.deep_get(self._get_json(shared_data), 'entry_data.ProfilePage[0].graphql.user')

                if "window.__additionalDataLoaded(" in resp and not userinfo:
                    parameters = resp.split("window.__additionalDataLoaded(")[1].split(");</script>")[0]
                    if parameters and "," in parameters:
                        shared_data = parameters.split(",", 1)[1]
                        if shared_data:
                            userinfo = self.deep_get(self._get_json(shared_data), 'graphql.user')
            except (TypeError, KeyError, IndexError):
                pass

        return userinfo

    def __fetch_stories(self, url, fetching_highlights_metadata=False):
        resp = self.get_json(url)

        if resp is not None:
            retval = self._get_json(resp)
            if retval['data'] and 'reels_media' in retval['data'] and len(retval['data']['reels_media']) > 0 and len(retval['data']['reels_media'][0]['items']) > 0:
                items = []

                for reel_media in retval['data']['reels_media']:
                    items.extend([self.set_story_url(item) for item in reel_media['items']])
                    for item in reel_media['items']:
                        item['highlight'] = fetching_highlights_metadata
                        self.stories.append(item)

                return items

        return []

    def fetch_main_stories(self, user_id):
        """Fetches the user's main stories."""
        return self.__fetch_stories(MAIN_STORIES_URL.format(user_id))

    def fetch_highlight_stories(self, user_id):
        """Fetches the user's highlight stories."""

        resp = self.get_json(HIGHLIGHT_STORIES_USER_ID_URL.format(user_id))

        if resp is not None:
            retval = self._get_json(resp)

            if retval['data'] and 'user' in retval['data'] and 'edge_highlight_reels' in retval['data']['user'] and \
                    'edges' in retval['data']['user']['edge_highlight_reels']:
                highlight_stories_ids = [item['node']['id'] for item in
                                         retval['data']['user']['edge_highlight_reels']['edges']]

                # Workaround for issue https://github.com/arc298/instagram-scraper/issues/488
                # __fetch_stories with count of ids more than 20 some times returns "Bad gateway" error.
                # Instagram web site fetches by 3.
                ids_chunks = [highlight_stories_ids[i:i + 3] for i in range(0, len(highlight_stories_ids), 3)]

                stories = []

                for ids_chunk in ids_chunks:
                    stories.extend(self.__fetch_stories(HIGHLIGHT_STORIES_REEL_ID_URL.format('%22%2C%22'.join(str(x) for x in ids_chunk)), fetching_highlights_metadata=True))

                return stories

        return []

    def query_media_gen(self, user, end_cursor=''):
        """Generator for media."""
        media, end_cursor = self.__query_media(user['id'], end_cursor)

        if media:
            try:
                while True:
                    for item in media:
                        if not self.is_new_media(item):
                            return
                        yield item

                    if end_cursor:
                        media, end_cursor = self.__query_media(user['id'], end_cursor)
                    else:
                        return
            except ValueError:
                self.logger.exception('Failed to query media for user ' + user['username'])

    def __query_media(self, id, end_cursor=''):
        params = QUERY_MEDIA_VARS.format(id, end_cursor)
        self.update_ig_gis_header(params)

        resp = self.get_json(QUERY_MEDIA.format(params))

        if resp is not None:
            payload = self._get_json(resp)['data']['user']

            if payload:
                container = payload['edge_owner_to_timeline_media']
                nodes = self._get_nodes(container)
                end_cursor = container['page_info']['end_cursor']
                return nodes, end_cursor

        return None, None

    def get_ig_gis(self, rhx_gis, params):
        data = rhx_gis + ":" + params
        if sys.version_info.major >= 3:
            return hashlib.md5(data.encode('utf-8')).hexdigest()
        else:
            return hashlib.md5(data).hexdigest()

    def update_ig_gis_header(self, params):
        self.session.headers.update({
            'x-instagram-gis': self.get_ig_gis(
                self.rhx_gis,
                params
            )
        })

    def has_selected_media_types(self, item):
        filetypes = {'jpg': 0, 'mp4': 0, 'webp': 0}

        for url in item['urls']:
            ext = self.__get_file_ext(url)
            if ext not in filetypes:
                filetypes[ext] = 0
            filetypes[ext] += 1

        if ('image' in self.media_types and (filetypes['jpg'] > 0 or filetypes['webp'] > 0)) or \
                ('video' in self.media_types and filetypes['mp4'] > 0):
            return True

        return False

    def story_has_selected_media_types(self, item):
        # media_type 1 is image, 2 is video
        if item['__typename'] == 'GraphStoryImage' and 'story-image' in self.media_types:
            return True
        if item['__typename'] == 'GraphStoryVideo' and 'story-video' in self.media_types:
            return True

        return False

    def extract_tags(self, item):
        """Extracts the hashtags from the caption text."""
        caption_text = ''
        if 'caption' in item and item['caption']:
            if isinstance(item['caption'], dict):
                caption_text = item['caption']['text']
            else:
                caption_text = item['caption']

        elif 'edge_media_to_caption' in item and item['edge_media_to_caption'] and item['edge_media_to_caption'][
            'edges']:
            caption_text = item['edge_media_to_caption']['edges'][0]['node']['text']

        if caption_text:
            # include words and emojis
            item['tags'] = re.findall(
                r"(?<!&)#(\w+|(?:[\xA9\xAE\u203C\u2049\u2122\u2139\u2194-\u2199\u21A9\u21AA\u231A\u231B\u2328\u2388\u23CF\u23E9-\u23F3\u23F8-\u23FA\u24C2\u25AA\u25AB\u25B6\u25C0\u25FB-\u25FE\u2600-\u2604\u260E\u2611\u2614\u2615\u2618\u261D\u2620\u2622\u2623\u2626\u262A\u262E\u262F\u2638-\u263A\u2648-\u2653\u2660\u2663\u2665\u2666\u2668\u267B\u267F\u2692-\u2694\u2696\u2697\u2699\u269B\u269C\u26A0\u26A1\u26AA\u26AB\u26B0\u26B1\u26BD\u26BE\u26C4\u26C5\u26C8\u26CE\u26CF\u26D1\u26D3\u26D4\u26E9\u26EA\u26F0-\u26F5\u26F7-\u26FA\u26FD\u2702\u2705\u2708-\u270D\u270F\u2712\u2714\u2716\u271D\u2721\u2728\u2733\u2734\u2744\u2747\u274C\u274E\u2753-\u2755\u2757\u2763\u2764\u2795-\u2797\u27A1\u27B0\u27BF\u2934\u2935\u2B05-\u2B07\u2B1B\u2B1C\u2B50\u2B55\u3030\u303D\u3297\u3299]|\uD83C[\uDC04\uDCCF\uDD70\uDD71\uDD7E\uDD7F\uDD8E\uDD91-\uDD9A\uDE01\uDE02\uDE1A\uDE2F\uDE32-\uDE3A\uDE50\uDE51\uDF00-\uDF21\uDF24-\uDF93\uDF96\uDF97\uDF99-\uDF9B\uDF9E-\uDFF0\uDFF3-\uDFF5\uDFF7-\uDFFF]|\uD83D[\uDC00-\uDCFD\uDCFF-\uDD3D\uDD49-\uDD4E\uDD50-\uDD67\uDD6F\uDD70\uDD73-\uDD79\uDD87\uDD8A-\uDD8D\uDD90\uDD95\uDD96\uDDA5\uDDA8\uDDB1\uDDB2\uDDBC\uDDC2-\uDDC4\uDDD1-\uDDD3\uDDDC-\uDDDE\uDDE1\uDDE3\uDDEF\uDDF3\uDDFA-\uDE4F\uDE80-\uDEC5\uDECB-\uDED0\uDEE0-\uDEE5\uDEE9\uDEEB\uDEEC\uDEF0\uDEF3]|\uD83E[\uDD10-\uDD18\uDD80-\uDD84\uDDC0]|(?:0\u20E3|1\u20E3|2\u20E3|3\u20E3|4\u20E3|5\u20E3|6\u20E3|7\u20E3|8\u20E3|9\u20E3|#\u20E3|\\*\u20E3|\uD83C(?:\uDDE6\uD83C(?:\uDDEB|\uDDFD|\uDDF1|\uDDF8|\uDDE9|\uDDF4|\uDDEE|\uDDF6|\uDDEC|\uDDF7|\uDDF2|\uDDFC|\uDDE8|\uDDFA|\uDDF9|\uDDFF|\uDDEA)|\uDDE7\uD83C(?:\uDDF8|\uDDED|\uDDE9|\uDDE7|\uDDFE|\uDDEA|\uDDFF|\uDDEF|\uDDF2|\uDDF9|\uDDF4|\uDDE6|\uDDFC|\uDDFB|\uDDF7|\uDDF3|\uDDEC|\uDDEB|\uDDEE|\uDDF6|\uDDF1)|\uDDE8\uD83C(?:\uDDF2|\uDDE6|\uDDFB|\uDDEB|\uDDF1|\uDDF3|\uDDFD|\uDDF5|\uDDE8|\uDDF4|\uDDEC|\uDDE9|\uDDF0|\uDDF7|\uDDEE|\uDDFA|\uDDFC|\uDDFE|\uDDFF|\uDDED)|\uDDE9\uD83C(?:\uDDFF|\uDDF0|\uDDEC|\uDDEF|\uDDF2|\uDDF4|\uDDEA)|\uDDEA\uD83C(?:\uDDE6|\uDDE8|\uDDEC|\uDDF7|\uDDEA|\uDDF9|\uDDFA|\uDDF8|\uDDED)|\uDDEB\uD83C(?:\uDDF0|\uDDF4|\uDDEF|\uDDEE|\uDDF7|\uDDF2)|\uDDEC\uD83C(?:\uDDF6|\uDDEB|\uDDE6|\uDDF2|\uDDEA|\uDDED|\uDDEE|\uDDF7|\uDDF1|\uDDE9|\uDDF5|\uDDFA|\uDDF9|\uDDEC|\uDDF3|\uDDFC|\uDDFE|\uDDF8|\uDDE7)|\uDDED\uD83C(?:\uDDF7|\uDDF9|\uDDF2|\uDDF3|\uDDF0|\uDDFA)|\uDDEE\uD83C(?:\uDDF4|\uDDE8|\uDDF8|\uDDF3|\uDDE9|\uDDF7|\uDDF6|\uDDEA|\uDDF2|\uDDF1|\uDDF9)|\uDDEF\uD83C(?:\uDDF2|\uDDF5|\uDDEA|\uDDF4)|\uDDF0\uD83C(?:\uDDED|\uDDFE|\uDDF2|\uDDFF|\uDDEA|\uDDEE|\uDDFC|\uDDEC|\uDDF5|\uDDF7|\uDDF3)|\uDDF1\uD83C(?:\uDDE6|\uDDFB|\uDDE7|\uDDF8|\uDDF7|\uDDFE|\uDDEE|\uDDF9|\uDDFA|\uDDF0|\uDDE8)|\uDDF2\uD83C(?:\uDDF4|\uDDF0|\uDDEC|\uDDFC|\uDDFE|\uDDFB|\uDDF1|\uDDF9|\uDDED|\uDDF6|\uDDF7|\uDDFA|\uDDFD|\uDDE9|\uDDE8|\uDDF3|\uDDEA|\uDDF8|\uDDE6|\uDDFF|\uDDF2|\uDDF5|\uDDEB)|\uDDF3\uD83C(?:\uDDE6|\uDDF7|\uDDF5|\uDDF1|\uDDE8|\uDDFF|\uDDEE|\uDDEA|\uDDEC|\uDDFA|\uDDEB|\uDDF4)|\uDDF4\uD83C\uDDF2|\uDDF5\uD83C(?:\uDDEB|\uDDF0|\uDDFC|\uDDF8|\uDDE6|\uDDEC|\uDDFE|\uDDEA|\uDDED|\uDDF3|\uDDF1|\uDDF9|\uDDF7|\uDDF2)|\uDDF6\uD83C\uDDE6|\uDDF7\uD83C(?:\uDDEA|\uDDF4|\uDDFA|\uDDFC|\uDDF8)|\uDDF8\uD83C(?:\uDDFB|\uDDF2|\uDDF9|\uDDE6|\uDDF3|\uDDE8|\uDDF1|\uDDEC|\uDDFD|\uDDF0|\uDDEE|\uDDE7|\uDDF4|\uDDF8|\uDDED|\uDDE9|\uDDF7|\uDDEF|\uDDFF|\uDDEA|\uDDFE)|\uDDF9\uD83C(?:\uDDE9|\uDDEB|\uDDFC|\uDDEF|\uDDFF|\uDDED|\uDDF1|\uDDEC|\uDDF0|\uDDF4|\uDDF9|\uDDE6|\uDDF3|\uDDF7|\uDDF2|\uDDE8|\uDDFB)|\uDDFA\uD83C(?:\uDDEC|\uDDE6|\uDDF8|\uDDFE|\uDDF2|\uDDFF)|\uDDFB\uD83C(?:\uDDEC|\uDDE8|\uDDEE|\uDDFA|\uDDE6|\uDDEA|\uDDF3)|\uDDFC\uD83C(?:\uDDF8|\uDDEB)|\uDDFD\uD83C\uDDF0|\uDDFE\uD83C(?:\uDDF9|\uDDEA)|\uDDFF\uD83C(?:\uDDE6|\uDDF2|\uDDFC))))[\ufe00-\ufe0f\u200d]?)+",
                caption_text, re.UNICODE)
            item['tags'] = list(set(item['tags']))

        return item

    def get_original_image(self, url):
        """Gets the full-size image from the specified url."""
        # these path parts somehow prevent us from changing the rest of media url
        #url = re.sub(r'/vp/[0-9A-Fa-f]{32}/[0-9A-Fa-f]{8}/', '/', url)
        # remove dimensions to get largest image
        #url = re.sub(r'/[sp]\d{3,}x\d{3,}/', '/', url)
        # get non-square image if one exists
        #url = re.sub(r'/c\d{1,}.\d{1,}.\d{1,}.\d{1,}/', '/', url)
        return url

    def set_story_url(self, item):
        """Sets the story url."""
        urls = []
        if 'video_resources' in item and item['video_resources']:
            urls.append(item['video_resources'][-1]['src'])
        if 'display_resources' in item:
            urls.append(item['display_resources'][-1]['src'])
        item['urls'] = urls
        return item

    def download(self, item, save_dir='./'):
        """Downloads the media file."""

        if self.filter_locations:
            save_dir = os.path.join(save_dir, self.get_key_from_value(self.filter_locations, item["location"]["id"]))

        files_path = []

        for full_url, base_name in self.templatefilename(item):
            url = full_url.split('?')[0] #try the static url first, stripping parameters

            file_path = os.path.join(save_dir, base_name)

            if not os.path.exists(os.path.dirname(file_path)):
                self.make_dir(os.path.dirname(file_path))

            if not os.path.isfile(file_path):
                headers = {'Host': urlparse(url).hostname}

                part_file = file_path + '.part'
                downloaded = 0
                total_length = None
                with open(part_file, 'wb') as media_file:
                    try:
                        retry = 0
                        retry_delay = RETRY_DELAY
                        while (True):
                            if self.quit:
                                return
                            try:
                                downloaded_before = downloaded
                                headers['Range'] = 'bytes={0}-'.format(downloaded_before)

                                with self.session.get(url, cookies=self.cookies, headers=headers, stream=True, timeout=CONNECT_TIMEOUT) as response:
                                    if response.status_code == 404 or response.status_code == 410:
                                        #on 410 error see issue #343
                                        #instagram don't lie on this
                                        break
                                    if response.status_code == 403 and url != full_url:
                                        #see issue #254
                                        url = full_url
                                        continue
                                    response.raise_for_status()

                                    if response.status_code == 206:
                                        try:
                                            match = re.match(r'bytes (?P<first>\d+)-(?P<last>\d+)/(?P<size>\d+)', response.headers['Content-Range'])
                                            range_file_position = int(match.group('first'))
                                            if range_file_position != downloaded_before:
                                                raise Exception()
                                            total_length = int(match.group('size'))
                                            media_file.truncate(total_length)
                                        except:
                                            raise requests.exceptions.InvalidHeader('Invalid range response "{0}" for requested "{1}"'.format(
                                                response.headers.get('Content-Range'), headers.get('Range')))
                                    elif response.status_code == 200:
                                        if downloaded_before != 0:
                                            downloaded_before = 0
                                            downloaded = 0
                                            media_file.seek(0)
                                        content_length = response.headers.get('Content-Length')
                                        if content_length is None:
                                            self.logger.warning('No Content-Length in response, the file {0} may be partially downloaded'.format(base_name))
                                        else:
                                            total_length = int(content_length)
                                            media_file.truncate(total_length)
                                    else:
                                        raise PartialContentException('Wrong status code {0}', response.status_code)

                                    for chunk in response.iter_content(chunk_size=64*1024):
                                        if chunk:
                                            downloaded += len(chunk)
                                            media_file.write(chunk)
                                        if self.quit:
                                            return

                                if downloaded != total_length and total_length is not None:
                                    raise PartialContentException('Got first {0} bytes from {1}'.format(downloaded, total_length))

                                break

                            # In case of exception part_file is not removed on purpose,
                            # it is easier to exemine it later when analising logs.
                            # Please do not add os.remove here.
                            except (KeyboardInterrupt):
                                raise
                            except (requests.exceptions.RequestException, PartialContentException) as e:
                                media = url
                                if item['shortcode'] and item['shortcode'] != '':
                                    media += " from https://www.instagram.com/p/" + item['shortcode']
                                if downloaded - downloaded_before > 0:
                                    # if we got some data on this iteration do not count it as a failure
                                    self.logger.warning('Continue after exception {0} on {1}'.format(repr(e), media))
                                    retry = 0 # the next fail will be first in a row with no data
                                    continue
                                if retry < MAX_RETRIES:
                                    self.logger.warning('Retry after exception {0} on {1}'.format(repr(e), media))
                                    self.sleep(retry_delay)
                                    retry_delay = min( 2 * retry_delay, MAX_RETRY_DELAY )
                                    retry = retry + 1
                                    continue
                                else:
                                    keep_trying = self._retry_prompt(media, repr(e))
                                    if keep_trying == True:
                                        retry = 0
                                        continue
                                    elif keep_trying == False:
                                        break
                                raise
                    finally:
                        media_file.truncate(downloaded)

                if downloaded == total_length or total_length is None and downloaded > 100:
                    try:
                        os.rename(part_file, file_path)
                    except FileNotFoundError:
                        self.logger.warning('.part file disappeared: ' + part_file)

                    timestamp = self.__get_timestamp(item)

                    if timestamp:
                        os.utime(file_path, (timestamp, timestamp))

            files_path.append(file_path)

        return files_path

    def templatefilename(self, item):

        for url in item['urls']:
            filename, extension = os.path.splitext(os.path.split(url.split('?')[0])[1])
            try:
                template = self.template
                template_values = {
                                    'username' : item['username'],
                                   'urlname': filename,
                                    'shortcode': str(item['shortcode']),
                                    'mediatype' : item['__typename'][5:],
                                   'datetime': time.strftime('%Y%m%d %Hh%Mm%Ss',
                                                             time.localtime(self.__get_timestamp(item))),
                                   'date': time.strftime('%Y%m%d', time.localtime(self.__get_timestamp(item))),
                                   'year': time.strftime('%Y', time.localtime(self.__get_timestamp(item))),
                                   'month': time.strftime('%m', time.localtime(self.__get_timestamp(item))),
                                   'day': time.strftime('%d', time.localtime(self.__get_timestamp(item))),
                                   'h': time.strftime('%Hh', time.localtime(self.__get_timestamp(item))),
                                   'm': time.strftime('%Mm', time.localtime(self.__get_timestamp(item))),
                                   's': time.strftime('%Ss', time.localtime(self.__get_timestamp(item)))}

                customfilename = str(template.format(**template_values) + extension)
                yield url, customfilename
            except KeyError:
                customfilename = str(filename + extension)
                yield url, customfilename

    def is_new_media(self, item):
        """Returns True if the media is new."""
        if self.latest is False or self.last_scraped_filemtime == 0:
            return True

        current_timestamp = self.__get_timestamp(item)
        return current_timestamp > 0 and current_timestamp > self.last_scraped_filemtime

    @staticmethod
    def __get_timestamp(item):
        if item:
            for key in ['taken_at_timestamp', 'created_time', 'taken_at', 'date', 'published_time']:
                found = item.get(key, 0)
                try:
                    found = int(found)
                    if found > 1:  # >1 to ignore any boolean casts
                        return found
                except ValueError:
                    pass
        return 0

    @staticmethod
    def __get_file_ext(url):
        return os.path.splitext(urlparse(url).path)[1][1:].strip().lower()

    @staticmethod
    def __search(query):
        resp = requests.get(SEARCH_URL.format(query))
        return json.loads(resp.text)

    def search_locations(self):
        query = ' '.join(self.usernames)
        result = self.__search(query)

        if len(result['places']) == 0:
            raise ValueError("No locations found for query '{0}'".format(query))

        sorted_places = sorted(result['places'], key=itemgetter('position'))

        for item in sorted_places[0:5]:
            place = item['place']
            print('location-id: {0}, title: {1}, subtitle: {2}, city: {3}, lat: {4}, lng: {5}'.format(
                place['location']['pk'],
                place['title'],
                place['subtitle'],
                place['location']['city'],
                place['location'].get('lat'),
                place['location'].get('lng')
            ))

    def merge_json(self, data, dst='./'):
        if not os.path.exists(dst):
            self.save_json(data, dst)
        if data:
            merged = data
            with open(dst, 'rb') as f:
                key = list(merged.keys())[0]
                file_data = json.load(codecs.getreader('utf-8')(f))
                self.remove_duplicate_data(file_data[key])
                if key in file_data:
                    merged[key] = file_data[key]
            self.save_json(merged, dst)

    @staticmethod
    def remove_duplicate_data(file_data):
        unique_ids = set()
        file_data_ids = []
        for post in file_data:
            file_data_ids.append(post["id"])
        file_ids_copy = file_data_ids.copy()
        for id_ in file_ids_copy:
            if id_ in unique_ids:
                file_data_ids.pop(file_data_ids.index(id_))
            else:
                unique_ids.add(id_)

    @staticmethod
    def save_json(data, dst='./'):
        """Saves the data to a json file."""
        if not os.path.exists(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))

        if data:
            output_list = {}
            if os.path.exists(dst):
                with open(dst, "rb") as f:
                    output_list.update(json.load(codecs.getreader('utf-8')(f)))

            with open(dst, 'wb') as f:
                output_list.update(data)
                json.dump(output_list, codecs.getwriter('utf-8')(f), indent=4, sort_keys=True, ensure_ascii=False)

    def _persist_metadata(self, dirname, filename):
        metadata_path = '{0}/{1}.json'.format(dirname, filename)
        if (self.media_metadata or self.comments or self.include_location):
            if self.posts:
                if self.latest:
                    self.merge_json({'GraphImages': self.posts}, metadata_path)
                else:
                    self.save_json({'GraphImages': self.posts}, metadata_path)

            if self.stories:
                if self.latest:
                    self.merge_json({'GraphStories': self.stories}, metadata_path)
                else:
                    self.save_json({'GraphStories': self.stories}, metadata_path)

    @staticmethod
    def get_logger(level=logging.DEBUG, dest='', verbose=0):
        """Returns a logger."""
        logger = logging.getLogger(__name__)

        dest +=  '/' if (dest !=  '') and dest[-1] != '/' else ''
        fh = logging.FileHandler(dest + 'instagram-scraper.log', 'w')
        fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        fh.setLevel(level)
        logger.addHandler(fh)

        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
        sh_lvls = [logging.ERROR, logging.WARNING, logging.INFO]
        sh.setLevel(sh_lvls[verbose])
        logger.addHandler(sh)

        logger.setLevel(level)

        return logger

    @staticmethod
    def get_values_from_file(usernames_file):
        """Parses a file containing a list of usernames."""
        users = []

        try:
            with open(usernames_file) as user_file:
                for line in user_file.readlines():
                    # Find all usernames delimited by ,; or whitespace
                    users += re.findall(r'[^,;\s]+', line.split("#")[0])
        except IOError as err:
            raise ValueError('File not found ' + err)

        return users

    @staticmethod
    def get_locations_from_file(locations_file):
        """
        parse an ini like file with sections composed of headers, [location],
        and arguments that are location ids
        """
        locations={}
        with open(locations_file, 'r') as f_in:
            lines = filter(None, (line.rstrip() for line in f_in))
            for line in lines:
                match = re.search(r"\[(\w+)\]", line)
                if match:
                    current_group = match.group(1)
                    locations.setdefault(current_group, [])
                else:
                    if  not line.strip().startswith("#"):
                        try:
                            locations[current_group].append(line.strip())
                        except NameError:
                            print("Must Start File with A Heading Enclosed in []")
                            sys.exit(1)
        return locations

    @staticmethod
    def get_key_from_value(location_dict, value):
        """
        Determine if value exist inside dict and return its key, otherwise return None
        """
        for key, values in location_dict.items():
            if value in values:
                return key
        return None

    @staticmethod
    def parse_delimited_str(input):
        """Parse the string input as a list of delimited tokens."""
        return re.findall(r'[^,;\s]+', input)

    def deep_get(self, dict, path):
        def _split_indexes(key):
            split_array_index = re.compile(r'[.\[\]]+')  # ['foo', '0']
            return filter(None, split_array_index.split(key))

        ends_with_index = re.compile(r'\[(.*?)\]$')  # foo[0]

        keylist = path.split('.')

        val = dict

        for key in keylist:
            try:
                if ends_with_index.search(key):
                    for prop in _split_indexes(key):
                        if prop.isdigit():
                            val = val[int(prop)]
                        else:
                            val = val[prop]
                else:
                    val = val[key]
            except (KeyError, IndexError, TypeError):
                return None

        return val

    def save_cookies(self):
        if self.cookiejar:
            with open(self.cookiejar, 'wb') as f:
                pickle.dump(self.session.cookies, f)



def main():
    parser = argparse.ArgumentParser(
        description="instagram-scraper scrapes and downloads an instagram user's photos and videos.",
        epilog=textwrap.dedent("""
        You can hide your credentials from the history, by reading your
        username from a local file:

        $ instagram-scraper @insta_args.txt user_to_scrape

        with insta_args.txt looking like this:
        -u=my_username
        -p=my_password

        You can add all arguments you want to that file, just remember to have
        one argument per line.

        Customize filename:
        by adding option --template or -T
        Default is: {urlname}
        And there are some option:
        {username}: Instagram user(s) to scrape.
        {shortcode}: post shortcode, but profile_pic and story are none.
        {urlname}: filename form url.
        {mediatype}: type of media.
        {datetime}: date and time that photo/video post on,
                     format is: 20180101 01h01m01s
        {date}: date that photo/video post on,
                 format is: 20180101
        {year}: format is: 2018
        {month}: format is: 01-12
        {day}: format is: 01-31
        {h}: hour, format is: 00-23h
        {m}: minute, format is 00-59m
        {s}: second, format is 00-59s

        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        fromfile_prefix_chars='@')

    parser.add_argument('username', help='Instagram user(s) to scrape', nargs='*')
    parser.add_argument('--destination', '-d', default='./', help='Download destination')
    parser.add_argument('--login-user', '--login_user', '-u', default=None, help='Instagram login user')
    parser.add_argument('--login-pass', '--login_pass', '-p', default=None, help='Instagram login password')
    parser.add_argument('--followings-input', '--followings_input', action='store_true', default=False,
                        help='Compile list of profiles followed by login-user to use as input')
    parser.add_argument('--followings-output', '--followings_output', help='Output followings-input to file in destination')
    parser.add_argument('--filename', '-f', help='Path to a file containing a list of users to scrape')
    parser.add_argument('--quiet', '-q', default=False, action='store_true', help='Be quiet while scraping')
    parser.add_argument('--maximum', '-m', type=int, default=0, help='Maximum number of items to scrape')
    parser.add_argument('--retain-username', '--retain_username', '-n', action='store_true', default=False,
                        help='Creates username subdirectory when destination flag is set')
    parser.add_argument('--media-metadata', '--media_metadata', action='store_true', default=False,
                        help='Save media metadata to json file')
    parser.add_argument('--profile-metadata', '--profile_metadata', action='store_true', default=False,
                        help='Save profile metadata to json file')
    parser.add_argument('--proxies', default={}, help='Enable use of proxies, add a valid JSON with http or/and https urls.')
    parser.add_argument('--include-location', '--include_location', action='store_true', default=False,
                        help='Include location data when saving media metadata')
    parser.add_argument('--media-types', '--media_types', '-t', nargs='+', default=['image', 'video', 'story'],
                        help='Specify media types to scrape')
    parser.add_argument('--latest', action='store_true', default=False, help='Scrape new media since the last scrape')
    parser.add_argument('--latest-stamps', '--latest_stamps', default=None,
                        help='Scrape new media since timestamps by user in specified file')
    parser.add_argument('--cookiejar', '--cookierjar', default=None,
                        help='File in which to store cookies so that they can be reused between runs.')
    parser.add_argument('--tag', action='store_true', default=False, help='Scrape media using a hashtag')
    parser.add_argument('--filter', default=None, help='Filter by tags in user posts', nargs='*')
    parser.add_argument('--filter-location', default=None, nargs="*", help="filter query by only accepting media with location filter as the location id")
    parser.add_argument('--filter-location-file', default=None, type=str, help="file containing list of locations to filter query by")
    parser.add_argument('--location', action='store_true', default=False, help='Scrape media using a location-id')
    parser.add_argument('--search-location', action='store_true', default=False, help='Search for locations by name')
    parser.add_argument('--comments', action='store_true', default=False, help='Save post comments to json file')
    parser.add_argument('--no-check-certificate', action='store_true', default=False, help='Do not use ssl on transaction')
    parser.add_argument('--interactive', '-i', action='store_true', default=False,
                        help='Enable interactive login challenge solving')
    parser.add_argument('--retry-forever', action='store_true', default=False,
                        help='Retry download attempts endlessly when errors are received')
    parser.add_argument('--verbose', '-v', type=int, default=0, help='Logging verbosity level')
    parser.add_argument('--template', '-T', type=str, default='{urlname}', help='Customize filename template')
    parser.add_argument('--log_destination', '-l', type=str, default='', help='destination folder for the instagram-scraper.log file')

    args = parser.parse_args()

    if (args.login_user and args.login_pass is None) or (args.login_user is None and args.login_pass):
        parser.print_help()
        raise ValueError('Must provide login user AND password')

    if not args.username and args.filename is None and not args.followings_input:
        parser.print_help()
        raise ValueError('Must provide username(s) OR a file containing a list of username(s) OR pass --followings-input')
    elif (args.username and args.filename) or (args.username and args.followings_input) or (args.filename and args.followings_input):
        parser.print_help()
        raise ValueError('Must provide only one of the following: username(s) OR a filename containing username(s) OR --followings-input')

    if args.tag and args.location:
        parser.print_help()
        raise ValueError('Must provide only one of the following: hashtag OR location')

    if args.tag and args.filter:
        parser.print_help()
        raise ValueError('Filters apply to user posts')

    if (args.filter_location or args.filter_location_file) and not args.include_location:
        parser.print_help()
        raise ValueError('Location filter needs locations in metadata to filter properly')

    if args.filename:
        args.usernames = InstagramScraper.get_values_from_file(args.filename)
    else:
        args.usernames = InstagramScraper.parse_delimited_str(','.join(args.username))

    if args.filter_location_file:
        args.filter_locations = InstagramScraper.get_locations_from_file(args.filter_location_file)
    elif args.filter_location:
        locations = {}
        locations.setdefault('', [])
        locations[''] = InstagramScraper.parse_delimited_str(','.join(args.filter_location))
        args.filter_locations = locations

    if args.media_types and len(args.media_types) == 1 and re.compile(r'[,;\s]+').findall(args.media_types[0]):
        args.media_types = InstagramScraper.parse_delimited_str(args.media_types[0])

    if args.retry_forever:
        global MAX_RETRIES
        MAX_RETRIES = sys.maxsize

    scraper = InstagramScraper(**vars(args))

    if args.login_user and args.login_pass:
        try:
            scraper.authenticate_with_login()
        except KeyError as e:
            if 'csrftoken' in str(e):
                raise KeyError('This error usually indicates that your IP address has been rate limited by Instagram. Try with a different VPN or proxy.') from e
            raise
    else:
        scraper.authenticate_as_guest()

    if args.followings_input:
        scraper.usernames = list(scraper.query_followings_gen(scraper.login_user))
        if args.followings_output:
            with open(os.path.join(scraper.destination, scraper.followings_output), 'w') as file:
                for username in scraper.usernames:
                    file.write(username + "\n")
            # If not requesting anything else, exit
            if args.media_types == ['none'] and args.media_metadata is False:
                scraper.logout()
                return

    if args.tag:
        scraper.scrape_hashtag()
    elif args.location:
        scraper.scrape_location()
    elif args.search_location:
        scraper.search_locations()
    else:
        scraper.scrape()

    scraper.save_cookies()


if __name__ == '__main__':
    main()
