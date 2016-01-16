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

    # PUBLIC INTERFACE - used across all states so data is mapped uniformly
    def mappings(self, year=None):
        """
        Returns an array of dicts containing the source url
        and standardized filename for a raw results file, along
        with other metadata.
        """
        mappings=[]
        for yr, elecs in self.elections(year).items():
            mappings.extend(self._build_metadata(yr,elecs))
        return mappings

    def target_urls(self,year=None):
        """Get list of source data urls, optional year filter"""
        return[item['raw_url'] for item in self.mappings(year)]

    def filename_url_pairs(self, year=None):
        return [(item['generated_filename'], item['raw_url'])
            for item in self.mappings(year)]

    # PRIVATE METHODS - used only in KY and built around their weirdness
    def _build_metadata(self, year, elections):
        meta_entries = []
        year_int = int(year)
        
        for election in elections:
            meta_entries.append({
                "generated_filename": self._standardized_filename(election),
                "raw_url": election['direct_links'][0],
                "ocd_id": "ocd-division/country:us/state:{}".format(self.state),
                "name": self.state,
                "election": election['slug']
            })
        return meta_entries
