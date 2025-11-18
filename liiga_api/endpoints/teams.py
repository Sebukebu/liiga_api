import functools
import requests
import pandas as pd
import json
from typing import Optional, Dict, Any, Literal
from liiga_api.utils import flatten_dict, ResponseParser
from liiga_api.base import Endpoint
from liiga_api.exceptions import LiigaAPIError


# TEAM ENDPOINTS

class TeamsAllTime(Endpoint):

    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]
    def __init__(self, season: str, gametype: gametype_literal, team_id: str = ""):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom=1976&seasonTo=2025&tournament={gtype}&dataType=standings"
        super().__init__(endpoint_name="TeamsAllTime", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results


class TeamsInfo(Endpoint):

    _COLUMNS = {
    "id": "teamId",
    "name": "teamName",
    "contact_info": "contactInfo",
    "country.code": "countryCode",
    "country.name": "countryName",
    "current_venue_capacity": "currentVenueCapacity",
    "general_info": "generalInfo",
    "url": "url",
    "locality": "locality",
    "logo": "logo",
    "short_name": "shortName",
    "slug": "slug"
    }

    def __init__(self):
        url_str: str = f"teams/info"
        super().__init__(endpoint_name="TeamsInfo", url_str=url_str)

    def _parse(self) -> list[dict]:
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        r = self.response['teams']
        data = []

        for team in r.values():
            data.append(ResponseParser._parse_record(team, self._COLUMNS))

        return data

class TeamsStatsPerSeason(Endpoint):

    def __init__(self):
        url_str: str = f"teams/info"
        super().__init__(endpoint_name="TeamsStatsPerSeason", url_str=url_str)

    def _parse(self) -> list[dict]:
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        r = self.response['teams']
        data = []

        for team in r.values():
            stats = team['teamtournamentstats']
            for row in stats:
                data.append(row)

        return data

class TeamsRosters(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]
    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"players/info?tournament={gtype}&fromSeason={start_season}&toSeason={end_season}&team="
        super().__init__(endpoint_name="TeamsRosters", url_str=url_str)



# Season team stats

class TeamStandings(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason", team_id: str | None = None):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=standings"
        super().__init__(endpoint_name="TeamStandings", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results
        
class TeamShots(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=shots"
        super().__init__(endpoint_name="TeamShots", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results

class TeamPasses(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=passes"
        super().__init__(endpoint_name="TeamPasses", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results

class TeamFaceoffs(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=faceoffs"
        super().__init__(endpoint_name="TeamFaceoffs", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results

class TeamEvenStrength(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=even_strength"
        super().__init__(endpoint_name="TeamEvenStrength", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results

class TeamPenaltyKill(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=penalty_kill"
        super().__init__(endpoint_name="TeamPenaltyKill", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results

class TeamPowerPlay(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=powerplay"
        super().__init__(endpoint_name="TeamPowerPlay", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results
    
class TeamPenalties(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: str):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=penalties"
        super().__init__(endpoint_name="TeamPenalties", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results
    
class TeamAttendance(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: str):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")

        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={start_season}&seasonTo={end_season}&tournament={gtype}&dataType=attendance"
        super().__init__(endpoint_name="TeamAttendance", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["teamStats"]
        for team in data:
            results.append(flatten_dict(team))
        return results
    


# SIMPLE STANDINGS

class Standings(Endpoint):
    def __init__(self, season: str):
        url_str: str = f"standings/?season={season}"
        super().__init__(endpoint_name="Standings", url_str=url_str)

    def _parse(self) -> list[dict]:
        if not isinstance(self.response, dict):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")
        
        results = []
        data = self.response["season"]
        for team in data:
            results.append(flatten_dict(team))
        return results
