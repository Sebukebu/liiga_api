# PlayersShots

Fetches and parses shot-specific statistics for Liiga players across a range of seasons.

**DataFrame Structure:**
- `playerId` (int): Unique player identifier.

**Full Column List (34 total):**
playerId, teamId, teamName, teamShortName, role, firstName, lastName, nationality, tournament, pictureUrl, previousTeamsForTournament, injured, jersey, lastSeason, goalkeeper, games, playedGames, rookie, suspended, removed, timeOnIce, current, isU20, goldenHelmets, alumniPoints, shots, shotsIntoGoal, goals, shotsSaved, shotsWideOrHigh, shotsBlocked, hardestShotVelocity, shotIntoGoalPercentage, shotPercentage, timeOnIceAvg

**Example Usage:**
```python
shots = PlayersShots(start_season="2023", end_season="2024", gametype="regularseason", summed=False)
df = shots.get_data_frame()
top_shooters = df.sort_values(by="shots", ascending=False).head(10)
```

**Example Endpoint URL:**
https://liiga.fi/api/v2/players/stats/summed/2024/2024/runkosarja/false?team=&dataType=shotStats&splitTeams=true

**Game Type Options:**

"regularseason": Regular season statistics.
"playoff": Playoff statistics.
"preseason": Preseason statistics.
"playout": Playout statistics.
"qualification": Qualification statistics.