# PlayerGameLog

Fetches and parses game-by-game statistics for a Liiga player.

This class retrieves a player's game logs for a specified season and game type, such as regular season, playoffs, or preseason.

**DataFrame Structure:**
- `gameId` (int): Unique game ID.

**Full Column List (39 total):**
gameStr, gameId, date, assists, blockedOrSavedShots, faceoffsTotal, faceoffsWon, faceoffsPercentage, goals, minus, totalPoints, homeTeamName, awayTeamName, penaltyMinutes, penaltykillAssists, penaltykillGoals, penaltykillPoints, plus, plusMinus, powerplayAssists, powerplayGoals, powerplaySeconds, timeOnIce, saves, savePercentage, blockOrSavedShotsPercentage, shots, shotsIntoGoal, shutOut, shotsSaved, shotsSavedBySkater, shotPercentage, shotIntoGoalPercentage, goalsAgainst, goalkeeper, winningGoals, won, tied, lost

**Example Usage:**
```python
gamelog = PlayerGameLog(player_id='40311015', season='2024', gametype='all')
df = gamelog.get_data_frame()
max_goals_game = df.loc[df['goals']==df['goals'].max()]
```

**Game Type Options:**

"regularseason": Regular season games.
"playoff": Playoff games.
"preseason": Preseason games.
"playout": Playout games.
"qualification": Qualification games.
"chl": CHL games.
"all": All game types (default).