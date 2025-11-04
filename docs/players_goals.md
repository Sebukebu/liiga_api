# PlayersGoals

Fetches and parses goal-specific statistics for Liiga players across a range of seasons.

**DataFrame Structure:**
- `playerId` (int): Unique player identifier.

**Full Column List (37 total):**
playerId, teamId, teamName, teamShortName, role, firstName, lastName, nationality, tournament, pictureUrl, previousTeamsForTournament, injured, jersey, lastSeason, goalkeeper, games, playedGames, rookie, suspended, removed, timeOnIce, current, isU20, goldenHelmets, alumniPoints, goals, shots, shotsIntoGoal, powerplayGoals, powerplay2Goals, penaltykillGoals, penaltykill2Goals, winningGoals, goalsToEmptyGoal, winningShotCompGoals, winningShotGoals, shotPercentage, timeOnIceAvg

**Example Usage:**
```python
goals = PlayersGoals(start_season="2023", end_season="2024", gametype="regularseason", summed=False)
df = goals.get_data_frame()
top_scorers = df.sort_values(by="goals", ascending=False).head(10)
```

**Example Endpoint URL:**
https://liiga.fi/api/v2/players/stats/summed/2024/2024/runkosarja/false?team=&dataType=goalStats&splitTeams=true

**Game Type Options:**

"regularseason": Regular season statistics.
"playoff": Playoff statistics.
"preseason": Preseason statistics.
"playout": Playout statistics.
"qualification": Qualification statistics.