# PlayersPasses

Fetches and parses pass-specific statistics for Liiga players across a range of seasons.

**DataFrame Structure:**
- `playerId` (int): Unique player identifier.

**Full Column List:**
[List all columns here]

**Example Usage:**
```python
passes = PlayersPasses(start_season="2023", end_season="2024", gametype="regularseason", summed=False)
df = passes.get_data_frame()
top_passers = df.sort_values(by="completedPasses", ascending=False).head(10)
```

**Example Endpoint URL:**
https://liiga.fi/api/v2/players/stats/summed/2024/2024/runkosarja/false?team=&dataType=passes&splitTeams=true

**Game Type Options:**

"regularseason": Regular season statistics.
"playoff": Playoff statistics.
"preseason": Preseason statistics.
"playout": Playout statistics.
"qualification": Qualification statistics.