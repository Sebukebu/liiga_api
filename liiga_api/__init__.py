
from .exceptions import LiigaAPIError
from .base import Endpoint


from .endpoints.players import (
    PlayerGameLog,
    PlayerProfile,
    PlayerTeamsPlayedFor,
    PlayerActiveSeasons,
    PlayerStatsPerSeason,
    PlayersBasicStats,
    PlayersAdvanced,
    PlayersGoals,
    PlayersShots,
    PlayersPasses,
    PlayersGameTime,
    PlayersPenalties,
    PlayersSkating,
    AllPlayers
)


from .endpoints.games import (
    SkaterGameStats,
    GoalieGameStats,
    GamesResults,
    GameGoalEvents,
    GamesGoalEvents,
    GamesSimpleResults,

    GameInfo,
    GamePlayers,
    GameAwards,
    GamePenaltyEvents,
    GameShotMap,
    GameReferees
)

from .endpoints.teams import (
    TeamsInfo,
    TeamsAllTime,
    TeamsRosters,
    TeamsStatsPerSeason,
    TeamStandings,
    TeamShots,
    TeamPasses,
    TeamEvenStrength,
    TeamPowerPlay,
    TeamPenaltyKill,
    TeamPenalties,
    TeamFaceoffs,
    TeamAttendance,
    Standings
)


__all__ = [
    # Base classes and exceptions
    "LiigaAPIError",
    "Endpoint",
    
    # Player endpoints
    "PlayerGameLog",
    "PlayerProfile",
    "PlayerTeamsPlayedFor",
    "PlayerActiveSeasons",
    "PlayerStatsPerSeason",
    "PlayersBasicStats",
    "PlayersAdvanced",
    "PlayersGoals",
    "PlayersShots",
    "PlayersPasses",
    "PlayersGameTime",
    "PlayersPenalties",
    "PlayersSkating",
    "AllPlayers",
    
    # Game endpoints
    "SkaterGameStats",
    "GoalieGameStats",
    "GamesResults",
    "GameGoalEvents",
    "GamesGoalEvents",
    "GamesSimpleResults",
    "GameInfo",
    "GamePlayers",
    "GameAwards",
    "GamePenaltyEvents",
    "GameShotMap",
    "GameReferees",
    
    # Team endpoints
    "TeamsInfo",
    "TeamsAllTime",
    "TeamsRosters",
    "TeamsStatsPerSeason",
    "TeamStandings",
    "TeamShots",
    "TeamPasses",
    "TeamEvenStrength",
    "TeamPowerPlay",
    "TeamPenaltyKill",
    "TeamPenalties",
    "TeamFaceoffs",
    "TeamAttendance",
    "Standings",
]