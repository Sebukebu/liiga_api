import functools
import requests
import pandas as pd
import json
from typing import Optional, Dict, Any, Literal
from liiga_api.utils import flatten_dict, ResponseParser
from liiga_api.base import Endpoint
from liiga_api.exceptions import LiigaAPIError


# PLAYER ENDPOINTS

class PlayerGameLog(Endpoint):
    """Fetches and parses game-by-game statistics for a Liiga player.
    """

    GAMETYPE_OPTIONS = {
        "regularseason": "regular",
        "playoff": "playoffs",
        "preseason": "practice",
        "playout": "playout",
        "qualification": "qualifications",
        "chl": "chl",
        "all": ""
        }
    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification", "chl", "all"]
        
    def __init__(self, player_id: str, season: str, gametype: gametype_literal = "all"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        self.gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"players/info/{player_id}/games/{season}"
        super().__init__(endpoint_name="PlayerGameLog", url_str=url_str)

    # OVERRIDE DEFAULT PARSE
    def _parse(self) -> list[dict]:
        gametypes = self.response.keys()

        if self.gtype != "":
            if self.gtype not in self.response:
                raise LiigaAPIError(f"Gametype '{self.gtype}' not available. ")
            games = self.response[self.gtype]

        else:
            games = []
            for g in list(gametypes):
                games.extend(self.response[g])

        return games


class PlayerActiveSeasons(Endpoint):
    def __init__(self, player_id: str):
        url_str: str = f"players/info/{player_id}"
        super().__init__(endpoint_name="PlayerActiveSeasons", url_str=url_str)
    
    def _parse(self) -> list:
        return self.response["activeSeasons"]


class PlayerProfile(Endpoint):

    _COLUMNS = {
        "birthLocality.country.name": "birthCountry",
        "birthLocality.country.code": "birthCountryCode",
        "birthLocality.name": "birthLocality",
        "dateOfBirth": "dateOfBirth",
        "fihaId": "fihaId",
        "firstName": "firstName",
        "lastName": "lastName",
        "handedness": "handedness",
        "height": "height",
        "isSuspended": "isSuspended",
        "isRemoved": "isRemoved",
        "nationality.name": "nationality",
        "nationality.code": "nationalityCode",
        "weight": "weight"
    }


    def __init__(self, player_id: str):
        url_str: str = f"players/info/{player_id}"
        super().__init__(endpoint_name="PlayerProfile", url_str=url_str)
    
    def _parse(self) -> dict:
        profile = ResponseParser._parse_record(self.response, self._COLUMNS)
        return profile

class PlayerTeamsPlayedFor(Endpoint):
    def __init__(self, player_id: str):
        url_str: str = f"players/info/{player_id}"
        super().__init__(endpoint_name="PlayerTeamsPlayedFor", url_str=url_str)

    def _parse(self) -> list[dict]:
        
        teams_data = self.response.get("teams", {})
        
        teams = []
        for season_key, team_info in teams_data.items():
            teams.append({
                "season": team_info["season"],
                "teamId": team_info["teamId"],
                "teamName": team_info["teamName"],
                "slug": team_info["slug"],
                "jersey": team_info.get("jersey"),
                "position": team_info.get("position"),
                "imageUrl": team_info.get("imageUrl")
            })

        return teams

class PlayerStatsPerSeason(Endpoint):
    
    GAMETYPE_OPTIONS = {
        "regularseason": "regular",
        "playoff": "playoffs",
        "practice": "practice",
        "playout": "playout",
        "qualification": "qualifications",
        "all": "all"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]
    
    def __init__(self, player_id: str, gametype: gametype_literal = "regularseason"):
        self.player_id = player_id
        self.gametype = gametype
        url_str = f"players/info/{player_id}"
        super().__init__(endpoint_name="PlayerStatsPerSeason", url_str=url_str)
    
    def _parse(self) -> list[dict]:
        historical = self.response.get("historical", {})
        
        if self.gametype == "all":
            all_stats = []
            for gametype_key, seasons in historical.items():
                if isinstance(seasons, list):
                    for season in seasons:
                        season_copy = season.copy()
                        season_copy["gametype"] = gametype_key
                        all_stats.append(season_copy)
            #sort by season and gametype -> no summing, return multiple rows per season, one for each gametype
            return sorted(all_stats, key=lambda x: (x["season"], x["gametype"]), reverse=True)
        else:
            stats = historical.get(self.gametype, [])

            return [
                {**season, "gametype": self.gametype} 
                for season in stats
            ]



# PLAYERS SUMMED STATS

class AllPlayers(Endpoint):
    """Fetches and parses aggregated statistics for all Liiga players across a range of seasons.
    """

    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs"
    }
    gametype_literal = Literal["regularseason", "playoff"]

    def __init__(self, start_season: str = "1976", end_season:str = "2026", gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=all&splitTeams=true"
        super().__init__(endpoint_name="AllPlayers", url_str=url_str)


class PlayersBasicStats(Endpoint):
    """Fetches and parses basic statistics for Liiga players.

    See docs/players_basic_stats.md for detailed documentation and examples.
    """


    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str ,gametype: gametype_literal = "regularseason", team_id: str | None = None, summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team={team_id}&dataType=basicStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersBasicStats", url_str=url_str)


    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players

    

class PlayersGoals(Endpoint):
    """Fetches and parses goal-specific statistics for Liiga players.

    See docs/players_goals.md for detailed documentation and examples.
    """

    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str,gametype: gametype_literal = "regularseason", summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=goalStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersGoals", url_str=url_str)



    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players


class PlayersShots(Endpoint):
    """Fetches and parses shot-specific statistics for Liiga players.

    See docs/players_shots.md for detailed documentation and examples.
    """

    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason", summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=shotStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersShots", url_str=url_str)

    

    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players


class PlayersPasses(Endpoint):
    """Fetches and parses pass-specific statistics for Liiga players.

    See docs/players_passes.md for detailed documentation and examples.
    """
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason", summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=passes&splitTeams=true"
        super().__init__(endpoint_name="PlayersPasses", url_str=url_str)

    

    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players


class PlayersPenalties(Endpoint):
    """Fetches and parses penalty-specific statistics for Liiga players.

    See docs/players_penalties.md for detailed documentation and examples.
    """
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason", summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=penaltyStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersPenalties", url_str=url_str)



    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players


class PlayersGameTime(Endpoint):
    """Fetches and parses time one ice statistics for Liiga players.

    See docs/players_gametime.md for detailed documentation and examples.
    """
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason", summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=gameTimes&splitTeams=true"
        super().__init__(endpoint_name="PlayersGameTime", url_str=url_str)

    

    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players


class PlayersSkating(Endpoint):
    """Fetches and parses skating statistics for Liiga players.

    See docs/players_skating.md for detailed documentation and examples.
    """
    
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season: str, gametype: gametype_literal = "regularseason", summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=skatingStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersSkating", url_str=url_str)

    

    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players

class PlayersAdvanced(Endpoint):
    """Fetches and parses advanced statistics for Liiga players.

    See docs/players_advanced.md for detailed documentation and examples.
    """
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications"
    }

    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification"]

    def __init__(self, start_season: str, end_season, gametype: gametype_literal = "regularseason", summed: bool = True):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        self.summed = summed
        url_str: str = f"players/stats/summed/{start_season}/{end_season}/{gtype}/false?team=&dataType=advancedStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersAdvanced", url_str=url_str)



    def _parse(self) -> list[dict]:
        players = []

        if self.summed:
            players.extend(self.response)

        else:
            for player_data in self.response:
                previous_teams = player_data.get("previousTeamsForTournament")
                if previous_teams:
                    players.extend(previous_teams)
                else:
                    players.append(player_data)
        return players
