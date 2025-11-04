# AllPlayers

Fetches and parses aggregated statistics for all Liiga players across a range of seasons.

This class retrieves summed statistics for all players, optionally filtered by game type (e.g., regular season or playoffs). The data from this endpoint goes back to the 1975-76 season (start_season=1976), so it works for historical comparisons. Unfortunately, the data excludes stats made for teams that aren't active anymore. The responses can be slow.

**DataFrame Structure:**
- `playerId` (int): Unique player identifier.

**Full Column List (53 total):**
playerId, teamId, teamName, teamShortName, role, firstName, lastName, nationality, tournament, pictureUrl, previousTeamsForTournament, injured, jersey, lastSeason, goalkeeper, games, playedGames, rookie, suspended, removed, timeOnIce, current, isU20, goldenHelmets, alumniPoints, assists, shots, goals, minus, plus, plusMinus, penalties, points, powerplayGoals, penaltykillGoals, winningGoals, emptyNetGoals, penaltyMinutes, shutOut, faceoffWon, wins, losses, ties, blockedOrSavedShots, goalsAgainst, faceoffTotal, gkWins, gkLosses, gkTies, shotPercentage, savePercentage, goalsAgainstAvg, winPercentage

**Example Usage:**
```python
players = AllPlayers(start_season="2020", end_season="2024", gametype="regularseason")
df = players.get_data_frame()
top_scorers = df.sort_values(by="goals", ascending=False).head(10)
```

**Example Endpoint URL:**
https://liiga.fi/api/v2/players/stats/summed/2021/2025/runkosarja/false?team=&dataType=all&splitTeams=true

**Game Type Options:**

"regularseason": Regular season statistics.
"playoff": Playoff statistics.