# -*- coding:utf-8 -*-
import unittest


class URLReplaceTests(unittest.TestCase):

    def test_repository_url_to_download_zip_url(self):
        """
        hogan: git://github.com/twitter/hogan.js.git
        https://github.com/twitter/hogan.js/archive/master.zip
        """
        from metafanstatic.downloading import repository_url_to_download_zip_url
        repository_url = "git://github.com/twitter/hogan.js.git"
        result = repository_url_to_download_zip_url(repository_url)
        self.assertEqual(result, "https://github.com/twitter/hogan.js/archive/master.zip")
