import functools
import requests
import pandas as pd
import json
from typing import Optional, Dict, Any, Literal
from liiga_api.utils import flatten_dict, ResponseParser
from liiga_api.exceptions import LiigaAPIError


class Endpoint:
    """Base class for LiigaAPI endpoints.

    This provides the basic functionality and methods shared across all endpoints.    

        Attributes:
        BASE_URL (str): The base URL for the Liiga API.
        endpoint_name (str): The name of the endpoint (e.g., "PlayersBasicStats", "Standings").
        url_str (str): The URL path for the endpoint (e.g., "players/info/40311015/games/2024").
        params (Dict): Query parameters for the API request.
        response: The raw JSON response from the API. Lazy loaded when users wants to access data
        data: The parsed data, ready for use. Lazy loaded when users wants to access data
    """

    BASE_URL: str = "https://liiga.fi/api/v2"
    
    
    def __init__(self, endpoint_name: str, url_str: str, **params: str):
        self.endpoint_name: str = endpoint_name
        self.url_str: str = url_str
        self.params: Dict = params


    @functools.cached_property
    def response(self) -> Dict:
        """Fetches and caches the API response."""
        try:
            url = f"{self.BASE_URL}/{self.url_str}"
            response = requests.get(url, params=self.params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise LiigaAPIError(f"Error fetching {self.endpoint_name}: {e}") from e

    @functools.cached_property
    def data(self) -> Any:
        """Parses and caches the API response."""
        return self._parse()
    
    def _parse(self) -> Optional[Any]:
        # Default parse for simple endpoints
        try:
            if isinstance(self.response, (dict, list)):
                return self.response
        except Exception as e:
            raise LiigaAPIError(f"Error parsing {self.endpoint_name}: {e}") from e

    def get_data_frame(self) -> Any:
        """Returns parsed dataframe of the endpoints response
        Returns a single dataframe or a list of dataframes based on endpoint and parameters"""
        # Returns multiple dataframes if data is a list of list of dicts
        if isinstance(self.data, list) and self.data and isinstance(self.data[0], list):
            
            return [pd.DataFrame(sublist) for sublist in self.data]
        # Otherwise returns single dataframe
        elif isinstance(self.data, list):
            return pd.DataFrame(self.data)
        elif isinstance(self.data, dict):
            return pd.DataFrame([self.data])
        else:
            raise LiigaAPIError(f"Cannot convert data to DataFrame for {self.endpoint_name}.")
    
    def get_json(self) -> str:
        """Return parsed json string(s) of the endpoints response"""
        return json.dumps(self.data, indent=2)
    
    def get_dict(self) -> Any:
        """Return parsed dictionary or dictionaries of the endpoints response"""
        return self.data
    
    def get_response(self) -> Any:
        """Return raw unparsed response for debugging or own implementations."""
        return self.response
    
    def clear_cache(self) -> None:
        del self.response
        del self.data
        return None
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.BASE_URL}/{self.url_str})"



