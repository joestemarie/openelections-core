"""
"""
from os.path import join
import json
import datetime
import urlparse

from openelex import PROJECT_ROOT
from openelex.base.datasource import BaseDatasource
from openelex.lib import build_github_url

class Datasource(BaseDatasource):
    def mappings(self, year=None):
        mappings=[]
        for yr, elecs in self.elections(year).items(): # gets list of elections by year
            mappings.extend(self._build_metadata(yr,elecs))

        return mappings

    def target_urls(self,year=None):
        return[item['raw_url'] for item in self.mappings(year)]

    def filename_url_pairs(self, year=None):
        return [(item['generated_filename'], item['raw_url'])
            for item in self.mappings(year)]

    def _build_metadata(self, year, elections):
        meta_entires = []
        for election in elections:
            meta_entries.append({
                "generated_filename": self._standardized_filename(election),
                "raw_url": election['direct_links'][0],
                "ocd_id": "ocd-division/country:us/state:{}".format(self.state),
                "name": self.state,
                "election": election['slug']
            })
        return meta_entries
