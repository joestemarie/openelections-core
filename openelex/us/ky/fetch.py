"""
This downloads the data locally based on datasource.py using the Clarity tool.
"""
import os
import os.path
import urllib
import urlparse
from zipfile import ZipFile

from bs4 import BeautifulSoup
import requests

from openelex.base.fetch import BaseFetcher
from openelex.us.ar.datasource import Datasource
import clarify

class FetchResults(BaseFetcher):
    def __init__(self):
        super(FetchResults,self).__init__()
        self._datasource = Datasource()
        self._fetched = set()
        self._results_portal_url = self._datasource.RESULTS_PORTAL_URL

    def fetch(self, url, fname=None, overwrite=False):
        if url in self._fetched:
            # quit if data for that election is already downloaded
            return

        if url.startswith(self._results_portal_url):
            # fetch from clarity portal
            self._fetch_portal(url,fname,overwrite)
        elif url.endswith('.zip'):
            # fetch zip using automatically generated name
            super(FetchResults, self).fetch(url, zip_fname, overwrite)
            self._extract_zip(url, zip_fname, overwrite)
        else:
            super(FetchResults, self).fetch(url, fname, overwrite)

        # adds the URL to the list we've downloaded
        self._fetched.add(url)

    def _fetch_portal(self, url, fname, overwrite=False):
        """
        Gets the results from the Clarity portal.
        """

        local_file_name = os.path.join(self.cache.abspath, fname)
        
