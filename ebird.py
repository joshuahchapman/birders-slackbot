"""
Utilities for interacting with the eBird APIs

See the API documentation here:
  https://documenter.getpostman.com/view/664302/ebird-api-20/2HTbHW
"""

import requests
import pandas as pd

API_ROOT = "https://ebird.org/ws2.0"
LISTS_ENDPOINT = "/product/lists"
OBS_ENDPOINT = "/data/obs"
REGION_ENDPOINT = "/ref/region"
CHECKLIST_ENDPOINT = "/product/checklist"


class EbirdClient:

    """
    Utilities for interacting with the eBird APIs
    """

    def __init__(self, api_token):

        self.api_token = api_token

    def get_recent_observations_for_region(self, region_code, days_back=14, max_results=0):
        """NB: The eBird endpoint returns each taxon only once."""

        api_params = {"key": self.api_token, "back": days_back, "cat": "species"}

        if max_results != 0:
            api_params["maxResults"] = max_results

        obs = requests.get(API_ROOT + OBS_ENDPOINT + "/" + region_code + "/recent", params=api_params)
        data = obs.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_recent_notable_observations_for_region(self, region_code, days_back=0, max_results=0):

        """
        If days_back is 0 or not set, uses eBird's max allowed value.
        """

        url = API_ROOT + OBS_ENDPOINT + "/" + region_code + "/recent/notable"

        api_params = {
            "key": self.api_token,
            "back": 30 if days_back == 0 else days_back
        }

        if max_results != 0:
            api_params["maxResults"] = max_results

        obs = requests.get(url=url, params=api_params)
        data = obs.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_recent_observations_by_lat_long(self, latitude, longitude, **kwargs):

        OPTIONAL_PARAMS = {
            'dist': 25,
            'back': 14,
            'cat': None,
            'maxResults': None,
            'includeProvisional': 'false',
            'hotspot': 'false',
            'sort': 'date',
            'sppLocale': 'en'
        }

        api_params = {"key": self.api_token, "lat": latitude, "lng": longitude}
        api_params.update(OPTIONAL_PARAMS)

        for key, value in kwargs.items():
            if key in OPTIONAL_PARAMS:
                api_params[key] = value
            else:
                print('Ignoring unrecognized parameter ' + key)

        obs = requests.get(API_ROOT + OBS_ENDPOINT + "/geo/recent", params=api_params)
        data = obs.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_recent_notable_observations_by_lat_long(self, latitude, longitude, **kwargs):

        OPTIONAL_PARAMS = {
            'dist': 25,
            'back': 14,
            'maxResults': None,
            'detail': 'simple',
            'hotspot': 'false'
        }

        api_params = {"key": self.api_token, "lat": latitude, "lng": longitude}
        api_params.update(OPTIONAL_PARAMS)

        for key, value in kwargs.items():
            if key in OPTIONAL_PARAMS:
                api_params[key] = value
            else:
                print('Ignoring unrecognized parameter ' + key)

        obs = requests.get(API_ROOT + OBS_ENDPOINT + "/geo/recent/notable", params=api_params)
        data = obs.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_recent_observations_for_region_for_species(self, region_code,
                                                       species_code, days_back=14, max_results=0):

        url = API_ROOT + OBS_ENDPOINT + "/" + region_code + "/recent/" + species_code

        api_params = {"key": self.api_token, "back": days_back}

        if max_results != 0:
            api_params["maxResults"] = max_results

        obs = requests.get(url, params=api_params)
        data = obs.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_recent_checklists_for_region(self, region_code, max_results=0):

        """
        If no value is passed for max_results, uses eBird's max allowed value.
        """

        url = API_ROOT + LISTS_ENDPOINT + "/" + region_code

        api_params = {
            "key": self.api_token,
            "maxResults": 200 if max_results == 0 else max_results
        }

        obs = requests.get(url, params=api_params)
        data = obs.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_checklists_for_date(self, region_code, year, month, day, max_results=0):

        # no zero-padding for month and day (e.g. year=2019, month=1, day=1)
        url = API_ROOT + LISTS_ENDPOINT + "/" + region_code + "/" + str(year) + "/" + str(month) + "/" + str(day)

        api_params = {
            "key": self.api_token,
            "maxResults": 200 if max_results == 0 else max_results
        }

        obs = requests.get(url, params=api_params)
        data = obs.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_checklist_details(self, submission_id):

        api_params = {"key": self.api_token}

        url = API_ROOT + CHECKLIST_ENDPOINT + "/view/" + submission_id

        checklist_details = requests.get(url, params=api_params)
        data = checklist_details.json()
        df = pd.DataFrame.from_dict(data)

        return df

    def get_county_codes_for_region(self, region_code):

        api_params = {"key": self.api_token}

        region_list = requests.get(API_ROOT + REGION_ENDPOINT + "/list/subnational2/" +
                                   region_code + ".json", params=api_params)
        data = region_list.json()
        df = pd.DataFrame.from_dict(data)

        return df
