"""
For all elections in 2010 and after, Kentucky posts results using the Clarity
portal. For all elections before, results are available by county only.
"""
from os.path import join
import json
import datetime
import urlparse

from openelex import PROJECT_ROOT
from openelex.base.datasource import BaseDatasource
from openelex.lib import build_github_url

class Datasource(BaseDatasource):
    # defining prefixes so that we can use different methods to fetch data
    # from different places
    RESULTS_PORTAL_URL = "http://elect.ky.gov/SiteCollectionDocuments/"
    CLARITY_PORTAL_URL = "http://results.enr.clarityelections.com/KY"

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
        """
        Builds out metadata given input of elections.
        """
        meta_entries = []
        for election in elections:
            election_metadata = self._build_election_metadata(election)
            meta_entries.extend(election_metadata)
        return meta_entries

    def _build_election_metadata(self,election):
        """
        This is the main method for building out the datasource. Works two different
        ways for the different ways we get data:
        - Clarity (2010 - present) - builds out mapping for county and precinct level
        - Fixed width files - builds out mapping for county level data
        """
        # NEW VERSION
        if any(self.CLARITY_PORTAL_URL in link for link in election['direct_links']):
            return self._build_election_metadata_clarity
        #elif:   # if link is not to the file itself
            # call method to handle
        else:   # do default thing
            return [{
                "generated_filename": self._standardized_filename(election,
                    reporting_level='county', extension='.txt'),
                "raw_url": election['direct_links'][0],
                "ocd_id": 'ocd-division/country:us/state:ky',
                "name": 'Kentucky',
                "election": election['slug']
            }]

    def _build_election_metadata_clarity(self, election, fmt="xml"):
        """
        Return metadata entries for election resulsts provided through Clarity,
        for elections starting in 2010.
        """
        county_mapping = self._build_election_metadata_clarity_county(election, fmt)
        precinct_mapping = self._build_election_metadata_clarity_precinct(election, fmt)
        meta_entries = county_mapping + precinct_mapping
        return meta_entries

    def _build_election_metadata_clarity_county(self, election, fmt):
        # this method returns the mapping for county-level data for elections
        # that have results in the Clarity system
        results_url = [x for x in election['direct_links'] if x.startswith(self.RESULTS_PORTAL_URL)][0]

        meta_entries = []
        meta_entries.append({
            "generated_filename": self._standardized_filename(election,
                reporting_level='county', extension='.txt'),
            "raw_extracted_filename": "detail.{}".format('txt'),
            "raw_url": results_url,
            "ocd_id": 'ocd-division/country:us/state:ky',
            "name": 'Kentucky',
            "election": election['slug']
        })
        return meta_entries

    def _build_election_metadata_clarity_precinct(self, election, fmt):
        """
        To get the data for each precinct, we use the Clarify library. We use the link from
        the Metadata API to create a list of counties with results. Then, we use Clarify's
        get_subjurisdictions() method to get all of the counties within and get a link to all
        of their results.
        """
        meta_entries = []

        # get the URL in the election links that has the portal URL in it
        clarity_url = [x for x in election['direct_links'] if x.startswith(self.CLARITY_PORTAL_URL)][0]
        statewide_jurisdiction = clarify.Jurisdiction(url=clarity_url, level='state')
        subs = statewide_jurisdiction.get_subjurisdictions()

        for county in subs:
            county_jurisdiction = clarify.Jurisdiction(url=county.url,level='county')
            report_url = county_jurisdiction.report_url('xml')
            ocd_id = 'ocd-division/country:us/state:ky/county:{}'.format(ocd_type_id(county.name))
            filename = self._standardized_filename(election,
                jurisdiction=county.name, reporting_level='precinct',
                extension='.'+fmt)

            meta_entries.append({
                "generated_filename": filename,
                "raw_extracted_filename": "detail.{}".format('txt'),
                "raw_url": report_url,
                "ocd_id": ocd_id,
                "name": county.name,
                "election": election['slug']
            })

        return meta_entries
