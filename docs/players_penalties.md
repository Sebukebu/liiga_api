# PlayersPenalties

Fetches and parses penalty-specific statistics for Liiga players across a range of seasons.

**DataFrame Structure:**
- `playerId` (int): Unique player identifier.

**Full Column List:**
[List all columns here]

**Example Usage:**
```python
penalties = PlayersPenalties(start_season="2023", end_season="2024", gametype="regularseason", summed=False)
df = penalties.get_data_frame()
top_penalized = df.sort_values(by="penaltyMinutes", ascending=False).head(10)
```

**Example Endpoint URL:**
https://liiga.fi/api/v2/players/stats/summed/2024/2024/runkosarja/false?team=&dataType=penaltyStats&splitTeams=true

**Game Type Options:**

"regularseason": Regular season statistics.
"playoff": Playoff statistics.
"preseason": Preseason statistics.
"playout": Playout statistics.
"qualification": Qualification statistics.