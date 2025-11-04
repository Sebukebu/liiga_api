# PlayersBasicStats

Fetches and parses basic statistics for Liiga players across a range of seasons.

This class retrieves basic stats for all players, optionally filtered by game type and team. This shouldn't be used (and won't work) for a large range of seasons, recommended to use with 1-10 seasons at a time.

**DataFrame Structure:**
- `playerId` (int): Unique player identifier. (If summed = True, if False then multiple rows with same id for different teams)

**Full Column List (45 total):**
playerId, teamId, teamName, teamShortName, role, firstName, lastName, nationality, tournament, pictureUrl, previousTeamsForTournament, injured, jersey, lastSeason, goalkeeper, games, playedGames, rookie, suspended, removed, timeOnIce, current, isU20, goldenHelmets, alumniPoints, goals, assists, points, plus, minus, plusMinus, penaltyMinutes, powerplayGoals, penaltykillGoals, winningGoals, shots, shotsIntoGoal, expectedGoals, contestWon, contestLost, goalsToEmptyGoal, contestWonPercentage, xge, shotPercentage, timeOnIceAvg

**Example Usage:**
```python
stats = PlayersBasicStats(start_season="2023", end_season="2024", gametype="regularseason", team_id="168761288")
df = stats.get_data_frame()
top_players = df.sort_values(by="points", ascending=False).head(10)
```

**Example Endpoint URL:**
https://liiga.fi/api/v2/players/stats/summed/2024/2024/runkosarja/false?team=875886777&dataType=basicStats&splitTeams=true

**Game Type Options:**

"regularseason": Regular season statistics.
"playoff": Playoff statistics.
"preseason": Preseason statistics.
"playout": Playout statistics.
"qualification": Qualification statistics.