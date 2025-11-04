# PlayersAdvanced

Fetches and parses advanced statistics for Liiga players across a range of seasons.

This endpoint provides detailed advanced metrics such as Corsi, zone starts, and PDO for players.

---

## **DataFrame Structure**
- `playerId` (int): Unique player identifier.
- `teamId` (float): Team identifier. If `summed=True`, this will be `null` for the total row.
- `corsiFor` (int): Corsi For (shots attempted for while player is on ice).
- `corsiAgainst` (int): Corsi Against (shots attempted against while player is on ice).
- `corsiDiffTotal` (int): Corsi differential (Corsi For - Corsi Against).
- `zoneStartsOz` (int): Offensive zone starts.
- `zoneStartsDz` (int): Defensive zone starts.
- `fsTeamShots` (int): Team shots while player is on ice.
- `fsTeamShotsAgainst` (int): Opponent shots while player is on ice.
- `fsTeamGoals` (int): Team goals while player is on ice.
- `fsTeamGoalsAgainst` (int): Opponent goals while player is on ice.
- `corsiPercentageFor` (float): Corsi For percentage.
- `zoneStartsDzPercentage` (float): Percentage of defensive zone starts.
- `zoneStartsOzPercentage` (float): Percentage of offensive zone starts.
- `fsTeamShotPercentage` (float): Team shooting percentage while player is on ice.
- `fsTeamSavePercentage` (float): Team save percentage while player is on ice.
- `pdo` (float): PDO (sum of team shooting percentage and save percentage while player is on ice).

---

## **Full Column List (40 total)**
playerId, teamId, teamName, teamShortName, role, firstName, lastName, nationality, tournament, pictureUrl,
previousTeamsForTournament, injured, jersey, lastSeason, goalkeeper, games, playedGames, rookie, suspended,
removed, timeOnIce, current, isU20, goldenHelmets, alumniPoints, corsiFor, corsiAgainst, corsiDiffTotal,
zoneStartsOz, zoneStartsDz, fsTeamShots, fsTeamShotsAgainst, fsTeamGoals, fsTeamGoalsAgainst, corsiPercentageFor,
zoneStartsDzPercentage, zoneStartsOzPercentage, fsTeamShotPercentage, fsTeamSavePercentage, pdo

## **Example Usage**
```python
advanced = PlayersAdvanced(start_season="2023", end_season="2024", gametype="regularseason", summed=False)
df = advanced.get_data_frame()
top_corsi = df.sort_values(by="corsiFor", ascending=False).head(10)
```

**Example Endpoint URL**
https://liiga.fi/api/v2/players/stats/summed/2023/2024/runkosarja/false?team=&dataType=advancedStats&splitTeams=true

**Game Type Options**

"regularseason": Regular season statistics.
"playoff": Playoff statistics.
"preseason": Preseason statistics.
"playout": Playout statistics.
"qualification": Qualification statistics.