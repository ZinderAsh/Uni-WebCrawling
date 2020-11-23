from bs4 import BeautifulSoup
from requesting_urls import get_html
import regex as re
import altair as alt
import pandas as pd

class Player:
    """
    Class to store information on NBA players
    """
    def __init__(self, name, team, url):
        self.name = name
        self.team = team
        self.url = url
        self.ppg = 0
        self.bpg = 0
        self.rpg = 0

    def __lt__(self, other):
        # Less-than method to sort by points per game
        return self.ppg < other.ppg

    def to_dict(self):
        # Returns the class as a dictionary, as Altair works best with them
        return {
            "name": self.name,
            "team": self.team,
            "ppg": self.ppg,
            "bpg": self.bpg,
            "rpg": self.rpg
        }

def safe_float(string):
    """
    Converts a string to float with a zero as a safetynet
    Args:
        string: The string to get float from
    Returns:
        float: The first float value within the string. If no valid float exists, returns 0
    """
    num = re.match("[\d\.]+", string)
    return float(num.group(0)) if num else 0

def get_player_stats(player):
    """
    Fetches the points/blocks/rebounds per game stats for a given Player
    Args:
        player: Player-object to fetch stats for and to write them back to
    """
    print("Fetching stats for", player.name)

    # Find the correct header for regular season stats
    html = get_html("https://en.wikipedia.org" + player.url)
    soup = BeautifulSoup(html, "html.parser")
    soup_header = soup.find("span", {"id": "Regular_season"})

    # If the header was not found, assume no stats for the season
    if soup_header:
        soup_table = soup_header.findNext("tbody")
        for row in soup_table.findAll("tr"):
            cells = row.findAll("td")
            # Row must have appropriate number of cells, and match the correct season date
            if len(cells) >= 13 and re.match("2019.20", cells[0].get_text()):
                # Extract the stats from each cell
                player.ppg = safe_float(cells[12].get_text())
                player.bpg = safe_float(cells[11].get_text())
                player.rpg = safe_float(cells[8].get_text())

def get_players(team_url, team_name, limit=None):
    """
    Gets a list of Players for an NBA team, and each of their stats
    Args:
        team_url (string): The url for the team's wikipedia page
        team_name (string): The name of the team. This is assigned to each Player
        [limit] (int): Limits the list of Players to the top [limit] players by points per game
    Returns:
        list: A list of Players for the team
    """
    # Find the table for the Roster
    html = get_html("https://en.wikipedia.org" + team_url)
    soup = BeautifulSoup(html, "html.parser")
    soup_header = soup.find("span", {"id": "Roster"})
    soup_table = soup_header.findNext("tbody").findNext("tbody")

    players = []
    for row in soup_table.findAll("tr"):
        cells = row.findAll("td")
        # Row must contain a minimum of 2 cells to have a player name
        if len(cells) > 2:
            a = cells[2].find("a")
            # Create a Player-object with the name and url of the player
            player = Player(a["title"], team_name, a["href"])
            get_player_stats(player)
            players.append(player)
    # Limit the list to top [limit] players by points per game if the argument is given
    if limit:
        players.sort(reverse=True)
        players = players[:limit]
    return players

def get_teams(url):
    """
    Fetches a list of NBA teams in the semifinals from the NBA playoffs Wikipedia page
    Args:
        url (string): The URL of the Wikipedia page
    Returns:
        list: A list of the teams in the semifinals, where each item is a list of [team_url, team_name]
    """
    html = get_html(url)

    # Find the table containing the bracket
    soup = BeautifulSoup(html, "html.parser")
    soup_table = soup.find("table", {"border": "0"})

    # All winners are in bold text, and semifinals require one win,
    # so finding all bold names in the table find all semifinal teams
    # Put them in a set to remove duplicates
    teams = set(re.findall('<b>[^<]*<a href="([^"]*)"[^>]*>([^<]*)', str(soup_table)))

    # Remove results with "Conference" as these are noe actually teams in the table
    teams = [t for t in teams if not re.search("Conference", t[1])]
    return teams

if __name__ == "__main__":
    teams = get_teams("https://en.wikipedia.org/wiki/2020_NBA_playoffs")

    # Make a list of all players for all teams
    players = []
    for team in teams:
        print(team)
        players += get_players(team[0], team[1], 3)

    # Create a pandas dataframe of the Player-objects as dictionaries
    data = pd.DataFrame([player.to_dict() for player in players])

    stats = ["ppg", "bpg", "rpg"]
    title = ["Points Per Game", "Blocks Per Game", "Rebound Per Game"]
    files = [""]

    # Assemble the three charts for ppg, bpg and rpg
    for stat in range(3):
        chart = alt.Chart(data).mark_bar().encode(
            y=alt.Y("name", sort="color", title="Player Name"),
            x=alt.X(stats[stat] + ":Q", title=title[stat]),
            color=alt.Color("team:N", title="Team Name"))
        chart.save("NBA_player_statistics/players_over_" + stats[stat] + ".html")
