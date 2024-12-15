BASE_URL = 'https://www.instagram.com/'
LOGIN_URL = BASE_URL + 'accounts/login/ajax/'
LOGOUT_URL = BASE_URL + 'accounts/logout/'
CHROME_WIN_UA = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36'
USER_URL = BASE_URL + '{0}/?__a=1'
USER_INFO = 'https://i.instagram.com/api/v1/users/{0}/info/'

MAIN_STORIES_URL = BASE_URL + 'graphql/query/?query_hash=45246d3fe16ccc6577e0bd297a5db1ab&variables=%7B%22reel_ids%22%3A%5B%22{0}%22%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%5D%2C%22precomposed_overlay%22%3Afalse%7D'
HIGHLIGHT_STORIES_USER_ID_URL = BASE_URL + 'graphql/query/?query_hash=c9100bf9110dd6361671f113dd02e7d6&variables=%7B%22user_id%22%3A%22{0}%22%2C%22include_chaining%22%3Afalse%2C%22include_reel%22%3Afalse%2C%22include_suggested_users%22%3Afalse%2C%22include_logged_out_extras%22%3Afalse%2C%22include_highlight_reels%22%3Atrue%2C%22include_related_profiles%22%3Afalse%7D'
HIGHLIGHT_STORIES_REEL_ID_URL = BASE_URL + 'graphql/query/?query_hash=45246d3fe16ccc6577e0bd297a5db1ab&variables=%7B%22reel_ids%22%3A%5B%5D%2C%22tag_names%22%3A%5B%5D%2C%22location_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B%22{0}%22%5D%2C%22precomposed_overlay%22%3Afalse%7D'
STORIES_UA = 'Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15'

BROADCAST_URL = BASE_URL + 'api/v1/feed/user/{0}/story/'

TAGS_URL = BASE_URL + 'explore/tags/{0}/?__a=1'
LOCATIONS_URL = BASE_URL + 'explore/locations/{0}/?__a=1'
VIEW_MEDIA_URL = BASE_URL + 'p/{0}/?__a=1'
SEARCH_URL = BASE_URL + 'web/search/topsearch/?context=blended&query={0}'

QUERY_FOLLOWINGS = BASE_URL + 'graphql/query/?query_hash=c56ee0ae1f89cdbd1c89e2bc6b8f3d18&variables={0}'
QUERY_FOLLOWINGS_VARS = '{{"id":"{0}","first":50,"after":"{1}"}}'

QUERY_COMMENTS = BASE_URL + 'graphql/query/?query_hash=33ba35852cb50da46f5b5e889df7d159&variables={0}'
QUERY_COMMENTS_VARS = '{{"shortcode":"{0}","first":50,"after":"{1}"}}'

QUERY_HASHTAG = BASE_URL + 'graphql/query/?query_hash=ded47faa9a1aaded10161a2ff32abb6b&variables={0}'
QUERY_HASHTAG_VARS = '{{"tag_name":"{0}","first":50,"after":"{1}"}}'

QUERY_LOCATION = BASE_URL + 'graphql/query/?query_hash=ac38b90f0f3981c42092016a37c59bf7&variables={0}'
QUERY_LOCATION_VARS = '{{"id":"{0}","first":50,"after":"{1}"}}'

QUERY_MEDIA = BASE_URL + 'graphql/query/?query_hash=42323d64886122307be10013ad2dcc44&variables={0}'
QUERY_MEDIA_VARS = '{{"id":"{0}","first":50,"after":"{1}"}}'

MAX_CONCURRENT_DOWNLOADS = 5
CONNECT_TIMEOUT = 90
MAX_RETRIES = 5
RETRY_DELAY = 5
MAX_RETRY_DELAY = 60

LATEST_STAMPS_USER_SECTION = 'users'
