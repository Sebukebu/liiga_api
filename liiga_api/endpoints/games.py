import functools
import requests
import pandas as pd
import json
from typing import Optional, Dict, Any, Literal
from liiga_api.utils import flatten_dict, ResponseParser
from liiga_api.base import Endpoint
from liiga_api.exceptions import LiigaAPIError


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
    
    _COLUMNS = {
        # Game-level fields
        "id": "gameId",
        "season": "season",
        "start": "start",
        "end": "end",
        "finishedType": "finishedType",
        "started": "started",
        "ended": "ended",
        "gameTime": "gameTime",
        "spectators": "spectators",
        "buyTicketsUrl": "buyTicketsUrl",
        "currentPeriod": "currentPeriod",
        "cacheUpdateDate": "cacheUpdateDate",
        "provider": "provider",
        "stale": "stale",
        "serie": "serie",
        "gameWeek": "gameWeek",
        
        # Home team fields
        "homeTeam.teamId": "homeTeamId",
        "homeTeam.teamPlaceholder": "homeTeamPlaceholder",
        "homeTeam.teamName": "homeTeamName",
        "homeTeam.goals": "homeGoals",
        "homeTeam.timeOut": "homeTimeOut",
        "homeTeam.powerplayInstances": "homePowerplayInstances",
        "homeTeam.powerplayGoals": "homePowerplayGoals",
        "homeTeam.shortHandedInstances": "homeShortHandedInstances",
        "homeTeam.shortHandedGoals": "homeShortHandedGoals",
        "homeTeam.expectedGoals": "homeExpectedGoals",
        "homeTeam.ranking": "homeRanking",
        "homeTeam.gameStartDateTime": "homeGameStartDateTime",
        "homeTeam.logos.darkBg": "homeDarkBgLogo",
        "homeTeam.logos.lightBg": "homeLightBgLogo",
        "homeTeam.logos.darkBgOriginal": "homeDarkBgOriginalLogo",
        "homeTeam.logos.lightBgOriginal": "homeLightBgOriginalLogo",
        
        # Away team fields
        "awayTeam.teamId": "awayTeamId",
        "awayTeam.teamPlaceholder": "awayTeamPlaceholder",
        "awayTeam.teamName": "awayTeamName",
        "awayTeam.goals": "awayGoals",
        "awayTeam.timeOut": "awayTimeOut",
        "awayTeam.powerplayInstances": "awayPowerplayInstances",
        "awayTeam.powerplayGoals": "awayPowerplayGoals",
        "awayTeam.shortHandedInstances": "awayShortHandedInstances",
        "awayTeam.shortHandedGoals": "awayShortHandedGoals",
        "awayTeam.expectedGoals": "awayExpectedGoals",
        "awayTeam.ranking": "awayRanking",
        "awayTeam.gameStartDateTime": "awayGameStartDateTime",
        "awayTeam.logos.darkBg": "awayDarkBgLogo",
        "awayTeam.logos.lightBg": "awayLightBgLogo",
        "awayTeam.logos.darkBgOriginal": "awayDarkBgOriginalLogo",
        "awayTeam.logos.lightBgOriginal": "awayLightBgOriginalLogo",

        # Ice rink fields
        "iceRink.id": "iceRinkId",
        "iceRink.name": "iceRinkName",
        "iceRink.latitude": "iceRinkLatitude",
        "iceRink.longitude": "iceRinkLongitude",
        "iceRink.streetAddress": "iceRinkStreetAddress",
        "iceRink.zip": "iceRinkZip",
        "iceRink.city": "iceRinkCity",
    }

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

    def _parse(self):
        games = []
        for game_data in self.response:
            game_record = ResponseParser._parse_record(game_data, self._COLUMNS)
            game_record['homeTeamId'] = game_record['homeTeamId'].split(':')[0]
            game_record['awayTeamId'] = game_record['awayTeamId'].split(':')[0]
            games.append(game_record)
        return games
    

class GamesGoalEvents(Endpoint):

    _GAME_COLUMNS = {
        "id": "gameId",
        "season": "season",
        "start": "gameStart",
        "homeTeam.teamName": "homeTeam",
        "awayTeam.teamName": "awayTeam",
    }
    
    # Goal event columns
    _GOAL_COLUMNS = {
        "scorerPlayerId": "scorerPlayerId",
        "scorerPlayer.playerId": "scorerPlayerPlayerId",
        "scorerPlayer.firstName": "scorerPlayerFirstName",
        "scorerPlayer.lastName": "scorerPlayerLastName",
        "scorerGoalsInSeason": "scorerGoalsInSeason",
        "assistantPlayers": "assistantPlayers",
        "assistsSoFarInSeason": "assistsSoFarInSeason",
        "goalTypes": "goalTypes",
        "logTime": "logTime",
        "winningGoal": "winningGoal",
        "gameTime": "gameTime",
        "period": "period",
        "eventId": "eventId",
        "plusPlayerIds": "plusPlayerIds",
        "minusPlayerIds": "minusPlayerIds",
        "homeTeamScore": "homeTeamScore",
        "awayTeamScore": "awayTeamScore",
        "goalsSoFarInSeason": "goalsSoFarInSeason",
        "videoClipUrl": "videoClipUrl",
        "videoThumbnailUrl": "videoThumbnailUrl",
    }

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
        super().__init__(endpoint_name="GamesGoalEvents", url_str=url_str)

    
    def _parse(self) -> list[dict]:
        response = self.response
        all_goal_events = []

        for r in response:
            game_info = ResponseParser._parse_record(r, self._GAME_COLUMNS)
            hometeam_id = r.get("homeTeam").get("teamId").split(":")[0]
            awayteam_id = r.get("awayTeam").get("teamId").split(":")[0]

            for team_type in ["homeTeam", "awayTeam"]:
                goal_events = r.get(team_type, {}).get("goalEvents", [])
                for e in goal_events:
                    goal_event = ResponseParser._parse_record(e, self._GOAL_COLUMNS)

                    assistants = e.get("assistantPlayers", []) or []
                    assistant1 = assistants[0] if len(assistants) > 0 else {"playerId": None, "firstName": None, "lastName": None}
                    assistant2 = assistants[1] if len(assistants) > 1 else {"playerId": None, "firstName": None, "lastName": None}

                    goal_event.update({
                        "homeTeamId": hometeam_id,
                        "awayTeamId": awayteam_id,
                        "goalTeamSide": "home" if team_type == "homeTeam" else "away",
                        "assistant1Id": assistant1.get("playerId"),
                        "assistant1FirstName": assistant1.get("firstName"),
                        "assistant1LastName": assistant1.get("lastName"),
                        "assistant2Id": assistant2.get("playerId"),
                        "assistant2FirstName": assistant2.get("firstName"),
                        "assistant2LastName": assistant2.get("lastName"),
                    })

                    goal_event.update(game_info)
                    all_goal_events.append(goal_event)

        return all_goal_events


# GAMESTAT ENDPOINTS

class GameInfo(Endpoint):

    _COLUMNS = {
        "game.id": "gameId",
        "game.season": "season",
        "game.start": "start",
        "game.end": "end",
        "game.homeTeam.teamId": "homeTeamId",
        "game.homeTeam.teamName": "homeTeamName",
        "game.homeTeam.goals": "homeGoals",
        "game.homeTeam.timeOut": "homeTimeOut",
        "game.homeTeam.powerplayInstances": "homePowerplayInstances",
        "game.homeTeam.powerplayGoals": "homePowerplayGoals",
        "game.homeTeam.shortHandedInstances": "homeShortHandedInstances",
        "game.homeTeam.shortHandedGoals": "homeShortHandedGoals",
        "game.homeTeam.expectedGoals": "homeExpectedGoals",
        "game.homeTeam.ranking": "homeRanking",
        "game.homeTeam.gameStartDateTime": "homeGameStartDateTime",
        "game.homeTeam.logos.darkBg": "homeDarkBgLogo",
        "game.homeTeam.logos.lightBg": "homeLightBgLogo",

        "game.awayTeam.teamId": "awayTeamId",
        "game.awayTeam.teamName": "awayTeamName",
        "game.awayTeam.goals": "awayGoals",
        "game.awayTeam.timeOut": "awayTimeOut",
        "game.awayTeam.powerplayInstances": "awayPowerplayInstances",
        "game.awayTeam.powerplayGoals": "awayPowerplayGoals",
        "game.awayTeam.shortHandedInstances": "awayShortHandedInstances",
        "game.awayTeam.shortHandedGoals": "awayShortHandedGoals",
        "game.awayTeam.expectedGoals": "awayExpectedGoals",
        "game.awayTeam.ranking": "awayRanking",
        "game.awayTeam.gameStartDateTime": "awayGameStartDateTime",
        "game.awayTeam.logos.darkBg": "awayDarkBgLogo",
        "game.awayTeam.logos.lightBg": "awayLightBgLogo",

        "game.finishedType": "finishedType",
        "game.started": "started",
        "game.ended": "ended",
        "game.gameTime": "gameTime",
        "game.spectators": "spectators",
        "game.iceRink.id": "iceRinkId",
        "game.iceRink.name": "iceRinkName",
        "game.iceRink.latitude": "iceRinkLatitude",
        "game.iceRink.longitude": "iceRinkLongitude",
        "game.iceRink.zip": "iceRinkZip",
        "game.iceRink.city": "iceRinkCity",
        "game.curretPeriod": "currentPeriod"
        }
    

    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GameInfo", url_str=url_str)

    def _parse(self):
        info = ResponseParser._parse_record(self.response, self._COLUMNS)
        info['homeTeamId'] = info['homeTeamId'].split(':')[0]
        info['awayTeamId'] = info['awayTeamId'].split(':')[0]
        return info

class GameGoalEvents(Endpoint):

    _GAME_COLUMNS = {
        "id": "gameId",
        "season": "season",
        "start": "gameStart",
        "homeTeam.teamName": "homeTeam",
        "awayTeam.teamName": "awayTeam"
    }

    _GOAL_COLUMNS = {
        "scorerPlayerId": "scorerPlayerId",
        "scorerPlayer.playerId": "scorerPlayerPlayerId",
        "scorerPlayer.firstName": "scorerPlayerFirstName",
        "scorerPlayer.lastName": "scorerPlayerLastName",
        "scorerGoalsInSeason": "scorerGoalsInSeason",
        "assistantPlayers": "assistantPlayers",
        "assistsSoFarInSeason": "assistsSoFarInSeason",
        "goalTypes": "goalTypes",
        "logTime": "logTime",
        "winningGoal": "winningGoal",
        "gameTime": "gameTime",
        "period": "period",
        "eventId": "eventId",
        "plusPlayerIds": "plusPlayerIds",
        "minusPlayerIds": "minusPlayerIds",
        "homeTeamScore": "homeTeamScore",
        "awayTeamScore": "awayTeamScore",
        "goalsSoFarInSeason": "goalsSoFarInSeason",
        "videoClipUrl": "videoClipUrl",
        "videoThumbnailUrl": "videoThumbnailUrl",
    }

    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GameGoalEvents", url_str=url_str)


    def _parse(self):
        game = self.response["game"]
        all_goal_events = []
        game_info = ResponseParser._parse_record(game, self._GAME_COLUMNS)
        hometeam_id = game.get("homeTeam").get("teamId").split(":")[0]
        awayteam_id = game.get("awayTeam").get("teamId").split(":")[0]

        for team_type in ["homeTeam", "awayTeam"]:
                goal_events = game.get(team_type, {}).get("goalEvents", [])
                for e in goal_events:
                    goal_event = ResponseParser._parse_record(e, self._GOAL_COLUMNS)

                    assistants = e.get("assistantPlayers", []) or []
                    assistant1 = assistants[0] if len(assistants) > 0 else {"playerId": None, "firstName": None, "lastName": None}
                    assistant2 = assistants[1] if len(assistants) > 1 else {"playerId": None, "firstName": None, "lastName": None}

                    goal_event.update({
                        "homeTeamId": hometeam_id,
                        "awayTeamId": awayteam_id,
                        "goalTeamSide": "home" if team_type == "homeTeam" else "away",
                        "assistant1Id": assistant1.get("playerId"),
                        "assistant1FirstName": assistant1.get("firstName"),
                        "assistant1LastName": assistant1.get("lastName"),
                        "assistant2Id": assistant2.get("playerId"),
                        "assistant2FirstName": assistant2.get("firstName"),
                        "assistant2LastName": assistant2.get("lastName"),
                    })

                    goal_event.update(game_info)
                    all_goal_events.append(goal_event)

        return all_goal_events


class GamePenaltyEvents(Endpoint):


    _GAME_COLUMNS = {
        "id": "gameId",
        "season": "season",
        "start": "gameStart",
        "homeTeam.teamName": "homeTeam",
        "awayTeam.teamName": "awayTeam"
    }

    _PENALTY_COLUMNS = {
        "playerId": "playerId",
        "suffererPlayerId": "suffererPlayerId",
        "eventId": "eventId",
        "logTime": "logTime",
        "gameTime": "gameTime",
        "period": "period",
        "penaltyBegintime": "penaltyBegintime",
        "penaltyEndtime": "penaltyEndtime",
        "penaltyFaultName": "penaltyFaultName",
        "penaltyFaultType": "penaltyFaultType",
        "penaltyInfo": "penaltyInfo",
        "penaltyMinutes": "penaltyMinutes"
        }
    
    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GamePenaltyEvents", url_str=url_str)


    def _parse(self):
        game = self.response["game"]
        all_penalty_events = []
        game_info = ResponseParser._parse_record(game, self._GAME_COLUMNS)
        hometeam_id = game.get("homeTeam").get("teamId").split(":")[0]
        awayteam_id = game.get("awayTeam").get("teamId").split(":")[0]

        for team_type in ["homeTeam", "awayTeam"]:
                penalty_events = game.get(team_type, {}).get("penaltyEvents", [])
                for e in penalty_events:
                    penalty_event = ResponseParser._parse_record(e, self._PENALTY_COLUMNS)

                    penalty_event.update({
                        "homeTeamId": hometeam_id,
                        "awayTeamId": awayteam_id,
                        "penaltyTeamSide": "home" if team_type == "homeTeam" else "away"
                    })

                    penalty_event.update(game_info)
                    all_penalty_events.append(penalty_event)

        return all_penalty_events

#class GameGoalKeeperEvents(Endpoint):
    #pass

#class GameWinningShotComp(Endpoint):
    #pass


class GameReferees(Endpoint):
    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GameReferees", url_str=url_str)

    
    def _parse(self):
        game = self.response["game"]
        refs = []
        for ref in game['referees']:
            refs.append(ref)
        return refs
        


class GameAwards(Endpoint):
    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GameAwards", url_str=url_str)

    def _parse(self):
        awards = []
        for a in self.response["awards"]:
            a['teamId'] = a['teamId'].split(':')[0]
            awards.append(a)
        return awards


class GamePlayers(Endpoint):
    def __init__(self, game_id: str, season: str):
        url_str: str = f"games/{season}/{game_id}"
        super().__init__(endpoint_name="GamePlayers", url_str=url_str)

    def _parse(self):
        homeplayers = self.response['homeTeamPlayers']
        awayplayers = self.response['awayTeamPlayers']

        players = []

        for team in [homeplayers, awayplayers]:
            for player in team:
                player['teamId'] = player['teamId'].split(':')[0]
                players.append(player)

        return players


class SkaterGameStats(Endpoint):

    _PERIOD_PLAYERSTAT_KEYS = {
        "jerseyId": "jerseyId",
        "playerId": "playerId",
        "period.points": "points",
        "period.period": "period",
        "period.assists": "assists",
        "period.goals": "goals",
        "period.validGoals": "validGoals",
        "period.plusminus": "plusminus",
        "period.plus": "plus",
        "period.minus": "minus",
        "period.shots": "shots",
        "period.penaltyminutes": "penaltyminutes",
        "period.powerplayGoals": "powerplayGoals",
        "period.shortHandedGoals": "shortHandedGoals",
        "period.winningGoal": "winningGoal",
        "period.blockedShots": "blockedShots",
        "period.faceoffsTotal": "faceoffsTotal",
        "period.faceoffsWon": "faceoffsWon",
        "period.corsiFor": "corsiFor",
        "period.corsiAgainst": "corsiAgainst",
        "period.faceoffsCenterTotal": "faceoffsCenterTotal",
        "period.faceoffsCenterWon": "faceoffsCenterWon",
        "period.faceoffsDefenceTotal": "faceoffsDefenceTotal",
        "period.faceoffsDefenceWon": "faceoffsDefenceWon",
        "period.faceoffsOffenceTotal": "faceoffsOffenceTotal",
        "period.faceoffsOffenceWon": "faceoffsOffenceWon",
        "period.fsZoneStartsDz": "fsZoneStartsDz",
        "period.fsZoneStartsOz": "fsZoneStartsOz",
        "period.powerplay2Goals": "powerplay2Goals",
        "period.penaltykill2Goals": "penaltykill2Goals",
        "period.powerplayAssists": "powerplayAssists",
        "period.penaltykillAssists": "penaltykillAssists",
        "period.goalsToEmptyGoal": "goalsToEmptyGoal",
        "period.fsTeamShots": "fsTeamShots",
        "period.fsTeamGoals": "fsTeamGoals",
        "period.fsTeamShotsAgainst": "fsTeamShotsAgainst",
        "period.fsTeamGoalsAgainst": "fsTeamGoalsAgainst",
        "period.timeofice": "timeofice",
        "distance": "distance",
        "totalPasses": "totalPasses",
        "successfulPasses": "successfulPasses",
        "playerPassesUnderPressure": "playerPassesUnderPressure",
        "playerSuccessfulPassesUnderPressure": "playerSuccessfulPassesUnderPressure",
        "playerPassesUnderHighPressure": "playerPassesUnderHighPressure",
        "playerSuccessfulPassesUnderHighPressure": "playerSuccessfulPassesUnderHighPressure",
        "expectedGoalsPlayer": "expectedGoalsPlayer",
        "expectedGoalsTeam": "expectedGoalsTeam",
        "expectedGoalsAgainst": "expectedGoalsAgainst",
        "expectedGoalsAgainstShotOnGoal": "expectedGoalsAgainstShotOnGoal"
    }
    _PERIOD_TEAM_CONTEXT = {
        "teamId": "teamId",
        "goals": "teamGoals",
        "shots": "teamShots",
        "powerPlayGoals": "teamPowerPlayGoals",
        "shortHandedGoalsAgainst": "teamShortHandedGoalsAgainst",
        "penaltyMinutes": "teamPenaltyMinutes",
        "faceOffWins": "teamFaceOffWins",
        "twoMinutePenalties": "teamTwoMinutePenalties",
        "fiveMinutePenalties": "teamFiveMinutePenalties",
        "tenMinutePenalties": "teamTenMinutePenalties",
        "twentyMinutePenalties": "teamTwentyMinutePenalties",
        "totalDistanceTravelled": "teamTotalDistanceTravelled"
    }

    _PERIOD_PUCK_KEYS = {
        "periodNumber": "periodNumber",
        "homeTeamControlDuration": "homeTeamControlDuration",
        "awayTeamControlDuration": "awayTeamControlDuration",
        "contestedControlDuration": "contestedControlDuration",
        "distance": "distance"
    }

    def __init__(self, game_id: str, season: str, summed: bool = True):
        if not isinstance(summed, bool):
            raise ValueError(f"Invalid parameter for summed: {summed}.")
        self.summed = summed
        url_str: str = f"games/stats/{season}/{game_id}"
        super().__init__(endpoint_name='SkaterGameStats', url_str=url_str)

    
    def _parse(self):
        return self._parse_sum_players() if self.summed else self._parse_by_period()
    
    def _parse_by_period(self) -> list[list[dict]]:
        periods_out = {}

        puck_stats = [ResponseParser._parse_record(p, self._PERIOD_PUCK_KEYS) for p in self.response.get("puckStats", [])]

        for side in ["homeTeam", "awayTeam"]:
            team_periods = self.response.get(side, [])
            for i, period in enumerate(team_periods):
                team_stats = ResponseParser._parse_record(period, self._PERIOD_TEAM_CONTEXT)
                team_stats['teamId'] = team_stats['teamId'].split(':')[0]

                # Get puck stats for this period if available, otherwise use empty dict
                puck_period = puck_stats[i] if i < len(puck_stats) else {}

                for player in period.get("periodPlayerStats", []):
                    player_stats = ResponseParser._parse_record(player, self._PERIOD_PLAYERSTAT_KEYS)
                    player_stats.update(team_stats)
                    player_stats.update(puck_period)
                    player_stats['teamSide'] = side.replace("Team", "").lower()
                    period_number = player_stats.get("period")
                    if period_number not in periods_out:
                        periods_out[period_number] = []
                    periods_out[period_number].append(player_stats)

        return [periods_out[p] for p in sorted(periods_out.keys()) if periods_out[p]]
    
    
    def _parse_sum_players(self) -> list[dict]:
        by_period = self._parse_by_period()
        player_totals: dict[str, dict] = {}

        for period in by_period:
            for player in period:
                player_id = player.get("playerId")
                if not player_id:
                    continue

                # Initialize with a copy of the first period's data
                if player_id not in player_totals:
                    player_totals[player_id] = player.copy()
                else:
                    total = player_totals[player_id]
                    for k, v in player.items():
                        # Skip identifiers
                        if k in ["playerId", "jerseyId", "teamId"]:
                            continue
                        if k == "period":
                            # Keep the highest period number
                            total[k] = max(total.get(k, 0), v if isinstance(v, int) else 0)
                        elif isinstance(v, (int, float)):
                            # Sum numeric values
                            total[k] = total.get(k, 0) + v
                        elif v is not None:
                            total[k] = v
        # Optionally, sort by playerId for consistency
        return [player_totals[pid] for pid in sorted(player_totals)]
    
class GoalieGameStats(Endpoint):

    _PERIOD_PLAYERSTAT_KEYS = {
        "jerseyId": "jerseyId",
        "playerId": "playerId",
        "period.shotsOnGoal": "shotsOnGoal",
        "period.period": "period",
        "period.penaltyminutes": "penaltyminutes",
        "period.timeofice": "timeofice",
        "period.saves": "saves",
        "period.goalsAllowed": "goalsAllowed",
        "period.savesPercentage": "savesPercentage",
        "period.assists": "assists",
        "period.goals": "goals",
        "period.validGoals": "validGoals",
        "period.blockedShots": "blockedShots",
        "period.faceoffsTotal": "faceoffsTotal",
        "period.faceoffsWon": "faceoffsWon",
        "period.faceoffsCenterTotal": "faceoffsCenterTotal",
        "period.faceoffsCenterWon": "faceoffsCenterWon",
        "period.faceoffsDefenceTotal": "faceoffsDefenceTotal",
        "period.faceoffsDefenceWon": "faceoffsDefenceWon",
        "period.faceoffsOffenceTotal": "faceoffsOffenceTotal",
        "period.faceoffsOffenceWon": "faceoffsOffenceWon",
        "period.points": "points",
        "period.plus": "plus",
        "period.minus": "minus",
        "period.powerplayGoals": "powerplayGoals",
        "period.shortHandedGoals": "shortHandedGoals",
        "period.winningGoal": "winningGoal",
        "period.corsiFor": "corsiFor",
        "period.corsiAgainst": "corsiAgainst",
        "period.fsZoneStartsOz": "fsZoneStartsOz",
        "period.fsZoneStartsDz": "fsZoneStartsDz",
        "period.powerplay2Goals": "powerplay2Goals",
        "period.penaltykill2Goals": "penaltykill2Goals",
        "period.powerplayAssists": "powerplayAssists",
        "period.penaltykillAssists": "penaltykillAssists",
        "period.goalsToEmptyGoal": "goalsToEmptyGoal",
        "period.fsTeamShots": "fsTeamShots",
        "period.fsTeamGoals": "fsTeamGoals",
        "period.fsTeamShotsAgainst": "fsTeamShotsAgainst",
        "period.fsTeamGoalsAgainst": "fsTeamGoalsAgainst",
        "distance": "distance",
        "totalPasses": "totalPasses",
        "successfulPasses": "successfulPasses",
        "playerPassesUnderPressure": "playerPassesUnderPressure",
        "playerSuccessfulPassesUnderPressure": "playerSuccessfulPassesUnderPressure",
        "playerPassesUnderHighPressure": "playerPassesUnderHighPressure",
        "playerSuccessfulPassesUnderHighPressure": "playerSuccessfulPassesUnderHighPressure",
        "expectedGoalsPlayer": "expectedGoalsPlayer",
        "expectedGoalsTeam": "expectedGoalsTeam",
        "expectedGoalsAgainst": "expectedGoalsAgainst",
        "expectedGoalsAgainstShotOnGoal": "expectedGoalsAgainstShotOnGoal"
    }


    _PERIOD_TEAM_CONTEXT = {
        "teamId": "teamId",
        "goals": "teamGoals",
        "shots": "teamShots",
        "powerPlayGoals": "teamPowerPlayGoals",
        "shortHandedGoalsAgainst": "teamShortHandedGoalsAgainst",
        "penaltyMinutes": "teamPenaltyMinutes",
        "faceOffWins": "teamFaceOffWins",
        "twoMinutePenalties": "teamTwoMinutePenalties",
        "fiveMinutePenalties": "teamFiveMinutePenalties",
        "tenMinutePenalties": "teamTenMinutePenalties",
        "twentyMinutePenalties": "teamTwentyMinutePenalties",
        "totalDistanceTravelled": "teamTotalDistanceTravelled"
    }

    _PERIOD_PUCK_KEYS = {
        "periodNumber": "periodNumber",
        "homeTeamControlDuration": "homeTeamControlDuration",
        "awayTeamControlDuration": "awayTeamControlDuration",
        "contestedControlDuration": "contestedControlDuration",
        "distance": "distance"
    }

    def __init__(self, game_id: str, season: str, summed: bool = True):
        if not isinstance(summed, bool):
            raise ValueError(f"Invalid parameter for summed: {summed}.")
        self.summed = summed
        url_str: str = f"games/stats/{season}/{game_id}"
        super().__init__(endpoint_name='GoalieGameStats', url_str=url_str)

    
    def _parse(self):
        return self._parse_sum_players() if self.summed else self._parse_by_period()
    
    def _parse_by_period(self) -> list[list[dict]]:
        periods_out = {}

        puck_stats = [ResponseParser._parse_record(p, self._PERIOD_PUCK_KEYS) for p in self.response.get("puckStats", [])]

        for side in ["homeTeam", "awayTeam"]:
            team_periods = self.response.get(side, [])
            for period, puck_period in zip(team_periods, puck_stats):
                team_stats = ResponseParser._parse_record(period, self._PERIOD_TEAM_CONTEXT)
                team_stats['teamId'] = team_stats['teamId'].split(':')[0]


                for player in period.get("goaliePeriodStats", []):
                    player_stats = ResponseParser._parse_record(player, self._PERIOD_PLAYERSTAT_KEYS)
                    player_stats.update(team_stats)
                    player_stats.update(puck_period)
                    player_stats['teamSide'] = side.replace("Team", "").lower()
                    period_number = player_stats.get("period")
                    if period_number not in periods_out:
                        periods_out[period_number] = []
                    periods_out[period_number].append(player_stats)
                    


        return [periods_out[p] for p in sorted(periods_out.keys()) if periods_out[p]]
    
    def _parse_sum_players(self) -> list[dict]:
        by_period = self._parse_by_period()
        player_totals: dict[str, dict] = {}

        for period in by_period:
            for player in period:
                player_id = player.get("playerId")
                if not player_id:
                    continue

                # Initialize with a copy of the first period's data
                if player_id not in player_totals:
                    player_totals[player_id] = player.copy()
                else:
                    total = player_totals[player_id]
                    for k, v in player.items():
                        # Skip identifiers
                        if k in ["playerId", "jerseyId", "teamId"]:
                            continue
                        if k == "period":
                            # Keep the highest period number
                            total[k] = max(total.get(k, 0), v if isinstance(v, int) else 0)
                        elif isinstance(v, (int, float)):
                            # Sum numeric values
                            total[k] = total.get(k, 0) + v
                        elif v is not None:
                            total[k] = v
        # Optionally, sort by playerId for consistency
        return [player_totals[pid] for pid in sorted(player_totals)]


class GameShotMap(Endpoint):
    def __init__(self, game_id: str, season: str):
        url_str: str = f"shotmap/{season}/{game_id}"
        super().__init__(endpoint_name="GameShotMap", url_str=url_str)
