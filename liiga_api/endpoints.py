import functools
import requests
import pandas as pd
import json
from typing import Optional, Dict, Any, Literal
from liiga_api.utils import flatten_dict, player_stat_parse



class LiigaAPIError(Exception):
    """Custom exception for Liiga API errors."""

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
        else:
            return pd.DataFrame(self.data)
    
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
    def __init__(self, player_id: str):
        url_str: str = f"players/info/{player_id}"
        super().__init__(endpoint_name="PlayerProfile", url_str=url_str)
    
    def _parse(self) -> dict:
        r = self.response
        
        profile = {
            "birthCountry": r.get("birthLocality", {}).get("country", {}).get("name"),
            "birthCountryCode": r.get("birthLocality", {}).get("country", {}).get("code"),
            "birthLocality": r.get("birthLocality", {}).get("name"),
            "dateOfBirth": r.get("dateOfBirth"),
            "fihaId": r.get("fihaId"),
            "firstName": r.get("firstName"),
            "lastName": r.get("lastName"),
            "handedness": r.get("handedness"),
            "height": r.get("height"),
            "isSuspended": r.get("isSuspended", False),
            "isRemoved": r.get("isRemoved", False),
            "nationality": r.get("nationality", {}).get("name"),
            "nationalityCode": r.get("nationality", {}).get("code"),
            "weight": r.get("weight")
        }
        return profile

class PlayerTeamsPlayedFor(Endpoint):
    def __init__(self, player_id: str):
        url_str: str = f"players/info/{player_id}"
        super().__init__(endpoint_name="PlayerTeamsPlayedFor", url_str=url_str)

    def _parse_teams(self) -> list[dict]:
        
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
        
        return player_stat_parse(self)
        
    

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

        return player_stat_parse(self)


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
        
        return player_stat_parse(self)


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
        
        return player_stat_parse(self)


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
        
        return player_stat_parse(self)


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
        
        return player_stat_parse(self)


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
        
        return player_stat_parse(self)


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
        
        return player_stat_parse(self)

# GAMES RESULTS AND SCHEDULE ENDPOINTS 


class GamesSimpleResults(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications",
        "chl": "chl"
    }
    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification", "chl"]
    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"schedule?tournament={gtype}&season={season}"
        super().__init__(endpoint_name="GamesSimpleResults", url_str=url_str)

    def _parse(self) -> list[dict]:
        if not isinstance(self.response, list):
            raise LiigaAPIError(f"Unexpected response type for {self.endpoint_name}: {type(self.response)}")

        results = []
        data = self.response
        for item in data:
            # Rename 'id' to 'rinkId' in 'iceRink' to avoid collision
            if "iceRink" in item and isinstance(item["iceRink"], dict):
                item["iceRink"]["rinkId"] = item["iceRink"].pop("id")

            # Flatten the item
            flattened = flatten_dict(item)
            results.append(flattened)
        return results

class GamesResults(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs",
        "preseason": "valmistavat_ottelut",
        "playout": "playout",
        "qualification": "qualifications",
        "chl": "chl"
    }
    gametype_literal = Literal["regularseason", "playoff", "preseason", "playout", "qualification", "chl"]
    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"games?tournament={gtype}&season={season}"
        super().__init__(endpoint_name="GamesResults", url_str=url_str)

# SPLIT GAMERESULTS INTO MULTIPLE CLASSES


# GAMESTAT ENDPOINTS

class GameInfo(Endpoint):
    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GameInfo", url_str=url_str)


# SPLIT INTO MULTIPLE CLASSES


class GameStatsBase(Endpoint):
    """Base class for game stats, handles parsing by period or summed totals."""

    PLAYER_STATS_KEY: str  # must be set in subclasses
    ENDPOINT_NAME: str     # must be set in subclasses

    def __init__(self, game_id: str, season: str, summed: bool = True):
        if not isinstance(summed, bool):
            raise ValueError(f"Invalid parameter for summed: {summed}.")
        self.summed = summed
        url_str: str = f"games/stats/{season}/{game_id}"
        super().__init__(endpoint_name=self.ENDPOINT_NAME, url_str=url_str)

    def _parse(self):
        return self._parse_sum_players() if self.summed else self._parse_by_period()

    def _parse_by_period(self) -> list[list[dict]]:
        if not isinstance(self.response, dict):
            raise LiigaAPIError(
                f"Unexpected response type for {self.endpoint_name}: {type(self.response)}"
            )

        periods_out = {}

        for side in ["homeTeam", "awayTeam"]:
            team_periods = self.response.get(side, [])
            for period in team_periods:
                period_number = period.get("period")
                if period_number not in periods_out:
                    periods_out[period_number] = []

                team_context = {
                    "team_side": side.replace("Team", "").lower(),
                    "team_id": period.get("teamId").split(":")[0],
                    "team_name": period.get("teamId").split(":")[1],
                    "team_goals": period.get("goals"),
                    "team_shots": period.get("shots"),
                    "team_penalty_minutes": period.get("penaltyMinutes"),
                    "team_faceoff_wins": period.get("faceOffWins"),
                    "team_powerplay_goals": period.get("powerPlayGoals"),
                    "team_shorthanded_goals_against": period.get("shortHandedGoalsAgainst"),
                }

                for player in period.get(self.PLAYER_STATS_KEY, []):
                    flattened = flatten_dict(player)
                    flattened.update(team_context)
                    periods_out[period_number].append(flattened)

        return [periods_out[p] for p in sorted(periods_out.keys()) if periods_out[p]]

    def _parse_sum_players(self) -> list[dict]:
        by_period = self._parse_by_period()
        player_totals: dict[str, dict] = {}

        for period in by_period:
            for player in period:
                player_id = player.get("playerId")
                if player_id is None:
                    continue

                if player_id not in player_totals:
                    player_totals[player_id] = player.copy()
                else:
                    for k, v in player.items():
                        if k in ["playerId", "jerseyId", "teamId"]:
                            continue
                        if k == "period":
                            # Keep the max period instead of summing
                            player_totals[player_id][k] = max(
                                player_totals[player_id].get(k, 0), v if isinstance(v, int) else 0
                            )
                        elif isinstance(v, (int, float)):
                            player_totals[player_id][k] = player_totals[player_id].get(k, 0) + v
                        else:
                            player_totals[player_id][k] = v  # take last non-numeric value

        return list(player_totals.values())


class GameSkaterStats(GameStatsBase):
    PLAYER_STATS_KEY = "periodPlayerStats"
    ENDPOINT_NAME = "GameSkaterStats"


class GameGoalieStats(GameStatsBase):
    PLAYER_STATS_KEY = "goaliePeriodStats"
    ENDPOINT_NAME = "GameGoalieStats"


class GameShotMap(Endpoint):
    def __init__(self, game_id: str, season: str):
        url_str: str = f"shotmap/{season}/{game_id}"
        super().__init__(endpoint_name="GameShotMap", url_str=url_str)


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


class TeamInfo(Endpoint):
    def __init__(self):
        url_str: str = f"teams/info"
        super().__init__(endpoint_name="TeamInfo", url_str=url_str)


class TeamRosters(Endpoint):
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
        url_str: str = f"players/info?tournament={gtype}&fromSeason={season}&toSeason={season}&team={team_id}"
        super().__init__(endpoint_name="TeamRosters", url_str=url_str)


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

    def __init__(self, season: str, gametype: gametype_literal = "regularseason", team_id: str | None = None):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=standings"
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

    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=shots"
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

    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=passes"
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

    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=faceoffs"
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

    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=even_strength"
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

    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=penalty_kill"
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

    def __init__(self, season: str, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=powerplay"
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

    def __init__(self, season: str, gametype: str):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=penalties"
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

    def __init__(self, season: str, gametype: str):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")

        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"teams/stats?seasonFrom={season}&seasonTo={season}&tournament={gtype}&dataType=attendance"
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
