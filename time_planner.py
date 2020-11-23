from bs4 import BeautifulSoup
from requesting_urls import get_html
import regex as re

def get_discipline(disc):
    """
    Converts a shorthand disclipline notation to the full version
    Args:
        disc (string): Shorthand discipline
    Returns:
        string: The full version of the discipline name
    """
    disciplines = {
        "DH": "Downhill",
        "SL": "Slalom",
        "GS": "Giant Slalom",
        "SG": "Super Giant Slalom",
        "AC": "Alpine Combined",
        "PG": "Parallel Giant Slalom"
    }
    return disciplines.get(disc)

def extract_events(html):
    """
    Gets all skiing events from a Wikipedia page
    Args:
        html (string): The HTML contents of the wikipedia page
    Returns:
        list: A list of skiing events where each item is a list of [date, venue, discipline]
    """

    soup = BeautifulSoup(html, "html.parser")

    # Find the table of events and the rows within
    soup_table = soup.find("table", {"class": "wikitable"})
    soup_tbody = soup_table.find("tbody")
    soup_rows = soup_tbody.findAll("tr")

    soup_rows = soup_rows[1:] # Remove headers

    # Regex expressions that retrieve each field from each row
    # Rows are very inconsistently composed, so this is simpler than pure BeautifulSoup
    r_date = re.compile("[\d]{1,2} [a-zA-Z]* [\d]{4}")
    r_venue = re.compile("<td.*flagicon.*<a[^>]*>(.*)</a>.*\s.*(DH|SL|GS|SG|AC|PG)")
    r_disc = re.compile("<td.*(DH|SL|GS|SG|AC|PG).*<")

    last_venue = None # The venue of the previous row
    events = []

    for soup_row in soup_rows:
        row = str(soup_row)
        date = r_date.search(row)
        # If the row has no date, the row is invalid and should not be checked further
        if date:
            # If the row has no venue, the venue must span multiple cells. Use the previous venue
            venue = r_venue.search(row) or last_venue
            last_venue = venue
            disc = r_disc.search(row).group(1)
            events.append([date.group(0), venue.group(1), get_discipline(disc)])

    return events

def save_betting_slip(events, output):
    """
    Writes a list of events to a file as a betting slip in markdown format
    Args:
        events (list): The list of events where each item is a list of [date, venue, discipline]
        output (string): The name of the file to write the betting slip too
    """
    f = open(output, "w")
    f.write("# BETTING SLIP\n")
    f.write("## Name: \n")
    f.write("| DATE | VENUE | DISCIPLINE | Who Wins? |\n")
    f.write("| :---: | :---: | :---: | :---: |\n")
    for e in events:
        f.write(f"| {e[0]} | {e[1]} | {e[2]} |  |\n")

if __name__ == "__main__":

    html = get_html("https://en.wikipedia.org/wiki/2019%E2%80%9320_FIS_Alpine_Ski_World_Cup")

    events = extract_events(html)

    save_betting_slip(events, "datetime_filter/betting_slip_empty.md")
