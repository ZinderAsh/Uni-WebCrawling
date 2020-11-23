# Assignment 5

Various scripts for fetching and extracting information from URLs and HTML. Mainly Wikipedia.
This script was written for a university assignment.

## Dependencies

Python3 is required to run these scripts.

These packages are required for this package:
- beautifulsoup4 (v4.9.1)
- regex (v2020.10.15)
- pandas (v1.1.3)
- altair (v4.1.0)
- requests (v2.24.0)

Install these using [pip](https://pip.pypa.io/en/stable/).
```
pip install beautifulsoup4
pip install regex
pip install pandas
pip install altair
pip install requests
```

## Usage

How to generate output files, as well as how to use the scripts. To import and use the methods, put the files in the same directory as the script using them.

### 5.1 Sending url requests

This script fetches the HTML from an URL.

Run the program from the terminal to generate output files:
```bash
python requesting_urls.py
```

This script generates files for these Wikipedia pages:
- Studio Ghibli
- Star Wars
- Dungeons & Dragons
- Main Page
- Hurricane Gonzalo

To use the method that fetches the HTML, import the python file as such:
```python
from requesting_urls import get_html

# Then use it like this
html = get_html("https://www.wikipedia.org")
```

### 5.2 Regex for filtering URLs

This script uses regular expressions to find all URLs in an HTML string, or to find all articles in a Wikipedia page.

Run the program from the terminal to generate output files:
```bash
python filter_urls.py
```

This script generates files for these Wikipedia pages:
- Nobel Prize
- Bundesliga
- 2019-20 FIS Alpine Ski World Cup

To use the method that finds all URLs:
```python
from requesting_urls import get_html
from filter_urls import find_urls

html = get_html("https://www.wikipedia.org")
url_list = find_urls(html)
```

To use the method that finds all Wikipedia article links within a Wikipedia article:
```python
from filter_urls import find_articles

article_list = find_articles("https://www.wikipedia.org")
```

### 5.3 Regular Expressions for finding dates

This script uses regular expressions to find all dates in an HTML string.

Run the program from the terminal to generate output files:
```bash
python collect_dates.py
```

This generates output files for these Wikipedia pages:
- Linus Pauling
- Rafael Nadal
- J. K. Rowling
- Richard Feynman
- Hans Rosling

To use the method that finds all dates:
```python
from requesting_urls import get_html
from collect_dates import find_dates

html = get_html("https://www.wikipedia.org")
date_list = find_dates(html)
```

### 5.4 Soup for filtering

This script uses beautifulsoup4 and regex to extract information about skiing events, and to generate a betting slip in markdown format.

Run the program from the terminal to generate output files:
```bash
python time_planner.py
```

This generates the betting slip for this Wikipedia page:
- 2019-20 FIS Alpine Ski World Cup

To use methods to get events and generate bettings slips:
```python
from requesting_urls import get_html
from time_planner import extract_events
from time_planner import save_betting_slip

html = get_html("https://en.wikipedia.org/wiki/2019%E2%80%9320_FIS_Alpine_Ski_World_Cup")

# Get a list of events from the article
events = extract_events(html)

# Turn those events into a betting slip
save_betting_slip(events, "betting_slip.md")
```

### 5.5 NBA Player Statistics

This script uses beautifulsoup4 and regex to fetch the the stats for the top player in the NBA.
Pandas and Altair is used to generate charts.

Run the program from the terminal to generate output files:
```bash
python fetch_player_statistics.py
```

This generates three charts for points, blocks and rebounds per game for the top 3 players of each team that competed in the semifinals.
The charts are generates as HTML, but can be saved to PNG by opening them in the browser.
The script generates the chart for the 2020 NBA playoffs.

To use the methods in this script:
```python
import fetch_player_statistics as ps

# Returns a list of all teams, on the form [team_url, team_name]
teams = ps.get_teams("https://en.wikipedia.org/wiki/2020_NBA_playoffs")

# If you want to get a list of all players
players = []
for team in teams:
    # You can optionally add a third argument to get only the top N scoring players
    # This also calls ps.get_player_stats(player) for each player
    players += ps.get_players(t[0], t[1])

# Use any graphing tool to make the charts, Altair for example

# Create a pandas dataframe from the players as dictionaries
data = pd.DataFrame([p.to_dict() for p in players])

# Export as a graph over points per game
chart = alt.Chart(data).mark_bar().encode(
    y=alt.Y("name", sort="color", title="Player Name"),
    x=alt.X("ppg:Q", title="Points per Game),
    color=alt.Color("team:N", title="Team Name"))
chart.save("players_over_ppg.html")
```

### 5.6

This script finds a short path, but not always the shortest, from one Wikipedia article to another.

Run the program from the terminal to generate output files:
```bash
python wiki_race_challenge.py
```

This generates an output file for the path from "Parque 18 de marzo de 1938" to "Bill Mundell".

To use the methods:
```python
import wiki_race_challenge as wr

# Specify start and goal
start = "https://en.wikipedia.org/wiki/Parque_18_de_marzo_de_1938"
goal = "https://en.wikipedia.org/wiki/Bill_Mundell"

# This returns the path found
# You can optionally add these parameters:
# - output: name for the output file to write the path to
# - greed: Value from 0-3 (Default: 2). The larger the value, the more greedy the algorithm's approach is
#   * Might never terminate if set to 0 or 1.
# - threads: The number of threads to use (Default: 4)
# - sleeptime: The time for each thread to sleep before checking the next article (Default: 0.01)
path = wiki_race(start, goal)
```

You can also simply modify the start and goal URLs within the script itself to try other paths.
