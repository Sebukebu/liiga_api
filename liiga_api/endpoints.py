import requests
import pandas as pd
import json
from typing import Optional, Dict, Any, Literal
from liiga_api.utils import flatten_dict



class LiigaAPIError(Exception):
    """Custom exception for Liiga API errors."""

class Endpoint:
    BASE_URL: str = "https://liiga.fi/api/v2"
    
    
    def __init__(self, endpoint_name: str, url_str: str, **params: str):
        self.endpoint_name: str = endpoint_name
        self.url_str: str = url_str
        self.params: Dict = params
        self.response: Dict = self._get()
        self.data: Any = self._parse()

    def _get(self) -> Dict:
        try:
            url: str = f"{self.BASE_URL}/{self.url_str}"
            response: requests.Response = requests.get(url, params=self.params)
            response.raise_for_status()
            
        except requests.RequestException as e:
            raise LiigaAPIError(f"Error fetching {self.endpoint_name}: {e}") from e
        return response.json()
    
    def _parse(self) -> Optional[Any]:
        # Default parse for simple endpoints
        try:
            if isinstance(self.response, (dict, list)):
                return self.response
        except Exception as e:
            raise LiigaAPIError(f"Error parsing {self.endpoint_name}: {e}") from e

    def get_data_frame(self) -> Any:
        # Returns multiple dataframes if data is a list of list of dicts
        if isinstance(self.data, list) and self.data and isinstance(self.data[0], list):
            
            return [pd.DataFrame(sublist) for sublist in self.data]
        # Otherwise returns single dataframe
        else:
            return pd.DataFrame(self.data)
    
    def get_json(self) -> str:
        return json.dumps(self.data, indent=2)
    
    def get_dict(self) -> Any:
        return self.data
    


# PLAYER ENDPOINTS

class PlayerGameLog(Endpoint):
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


class PlayerInfo(Endpoint):
    def __init__(self, player_id: str):
        url_str: str = f"players/info/{player_id}"
        super().__init__(endpoint_name="PlayerInfo", url_str=url_str)


# PLAYERS SUMMED STATS

class AllPlayers(Endpoint):
    GAMETYPE_OPTIONS = {
        "regularseason": "runkosarja",
        "playoff": "playoffs"
    }
    gametype_literal = Literal["regularseason", "playoff"]

    def __init__(self, gametype: gametype_literal = "regularseason"):
        if gametype not in self.GAMETYPE_OPTIONS:
            raise ValueError(f"Invalid gametype: {gametype}. Choose one of {list(self.GAMETYPE_OPTIONS.keys())}")
        gtype = self.GAMETYPE_OPTIONS[gametype]
        url_str: str = f"players/stats/summed/1976/2025/{gtype}/false?team=&dataType=all&splitTeams=true"
        super().__init__(endpoint_name="AllPlayers", url_str=url_str)


class PlayersBasicStats(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team={team_id}&dataType=basicStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersBasicStats", url_str=url_str)


class PlayersGoals(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team=&dataType=goalStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersGoals", url_str=url_str)


class PlayersShots(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team=&dataType=shotStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersShots", url_str=url_str)


class PlayersPasses(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team=&dataType=passes&splitTeams=true"
        super().__init__(endpoint_name="PlayersPasses", url_str=url_str)


class PlayersPenalties(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team=&dataType=penaltyStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersPenalties", url_str=url_str)


class PlayersGameTime(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team=&dataType=gameTimes&splitTeams=true"
        super().__init__(endpoint_name="PlayersGameTime", url_str=url_str)


class PlayersSkating(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team=&dataType=skatingStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersSkating", url_str=url_str)


class PlayersAdvanced(Endpoint):
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
        url_str: str = f"players/stats/summed/{season}/{season}/{gtype}/false?team=&dataType=advancedStats&splitTeams=true"
        super().__init__(endpoint_name="PlayersAdvanced", url_str=url_str)

# GAMES RESULTS AND SCHEDULE ENDPOINTS 

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
        super().__init__(endpoint_name="GameResults", url_str=url_str)


# GAMESTAT ENDPOINTS

class GameInfo(Endpoint):
    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GameInfo", url_str=url_str)


class GameSkaterStats(Endpoint):
    def __init__(self, game_id: str, season: str, summed: bool = True):
        if not isinstance(summed, bool):
            raise ValueError(f"Invalid parameter for summed: {summed}.")
        
        self.summed = summed
        url_str: str = f"games/stats/{season}/{game_id}"
        super().__init__(endpoint_name="GameSkaterStats", url_str=url_str)

    def _parse(self):
        return self._parse_sum_players() if self.summed else self._parse_by_period()

    def _parse_by_period(self) -> list[list[dict]]:
        if not isinstance(self.response, dict):
            raise LiigaAPIError(
                f"Unexpected response type for {self.endpoint_name}: {type(self.response)}"
            )

        periods_out = {1: [], 2: [], 3: []}


        for side in ["homeTeam", "awayTeam"]:
            team_periods = self.response.get(side, [])
            for period in team_periods:
                team_context = {
                    "team_side": side.replace("Team", "").lower(),
                    "team_id": period.get("teamId").split(":")[0],
                    "team_name": period.get("teamId").split(":")[1],
                    "period_number": period.get("period"),
                    "team_goals": period.get("goals"),
                    "team_shots": period.get("shots"),
                    "team_penalty_minutes": period.get("penaltyMinutes"),
                    "team_faceoff_wins": period.get("faceOffWins"),
                    "team_powerplay_goals": period.get("powerPlayGoals"),
                    "team_shorthanded_goals_against": period.get("shortHandedGoalsAgainst"),
                }

                for player in period.get("periodPlayerStats", []):
                    flattened = flatten_dict(player)
                    flattened.update(team_context)
                    periods_out[team_context["period_number"]].append(flattened)

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
                        if isinstance(v, (int, float)):
                            player_totals[player_id][k] = player_totals[player_id].get(k, 0) + v
                        else:
                            player_totals[player_id][k] = v  # take last non-numeric value

        return list(player_totals.values())
                

class GameGoalieStats(Endpoint):
    def __init__(self, game_id: str, season: str, summed: bool = True):
        if not isinstance(summed, bool):
            raise ValueError(f"Invalid parameter for summed: {summed}.")
        
        self.summed = summed
        url_str: str = f"games/stats/{season}/{game_id}"
        super().__init__(endpoint_name="GameGoalieStats", url_str=url_str)

    def _parse(self):
        return self._parse_sum_players() if self.summed else self._parse_by_period()

    def _parse_by_period(self) -> list[list[dict]]:
        if not isinstance(self.response, dict):
            raise LiigaAPIError(
                f"Unexpected response type for {self.endpoint_name}: {type(self.response)}"
            )

        periods_out = {1: [], 2: [], 3: []}


        for side in ["homeTeam", "awayTeam"]:
            team_periods = self.response.get(side, [])
            for period in team_periods:
                team_context = {
                    "team_side": side.replace("Team", "").lower(),
                    "team_id": period.get("teamId").split(":")[0],
                    "team_name": period.get("teamId").split(":")[1],
                    "period_number": period.get("period"),
                    "team_goals": period.get("goals"),
                    "team_shots": period.get("shots"),
                    "team_penalty_minutes": period.get("penaltyMinutes"),
                    "team_faceoff_wins": period.get("faceOffWins"),
                    "team_powerplay_goals": period.get("powerPlayGoals"),
                    "team_shorthanded_goals_against": period.get("shortHandedGoalsAgainst"),
                }

                for player in period.get("goaliePeriodStats", []):
                    flattened = flatten_dict(player)
                    flattened.update(team_context)
                    periods_out[team_context["period_number"]].append(flattened)

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
                        if isinstance(v, (int, float)):
                            player_totals[player_id][k] = player_totals[player_id].get(k, 0) + v
                        else:
                            player_totals[player_id][k] = v  # take last non-numeric value

        return list(player_totals.values())


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
