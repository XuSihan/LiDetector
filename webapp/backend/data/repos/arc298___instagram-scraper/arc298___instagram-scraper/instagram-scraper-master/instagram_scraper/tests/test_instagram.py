import unittest
import os
import shutil
import tempfile
import requests_mock
import glob
from instagram_scraper import InstagramScraper
from instagram_scraper.constants import *

class InstagramTests(unittest.TestCase):

    def setUp(self):
        fixtures_path = os.path.join(os.path.dirname(__file__), 'fixtures')

        fixture_files = glob.glob(os.path.join(fixtures_path, '*'))

        for file_path in fixture_files:
            basename = os.path.splitext(os.path.basename(file_path))[0]
            self.__dict__[basename] = open(file_path).read()

        # This is a max id of the last item in response_first_page.json.
        self.max_id = "1369793132326237681_50955533"

        self.test_dir = tempfile.mkdtemp()

        args = {
            'usernames': ['test'],
            'destination': self.test_dir,
            'login_user': None,
            'login_pass': None,
            'quiet': True,
            'maximum': 0,
            'retain_username': False,
            'media_metadata': False,
            'media_types': ['image', 'video', 'story'],
            'latest': False
        }

        self.scraper = InstagramScraper(**args)

    def tearDown(self):
        shutil.rmtree(self.test_dir)