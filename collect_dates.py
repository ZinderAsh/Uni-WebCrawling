from requesting_urls import get_html
import regex as re

def month2num(month):
    """
    Gets the correct month number for a month name.
    Args:
        month (string): The string name of the month
    Returns:
        int: The number of the month from 1-12. 0 if the month is invalid
    """
    switcher = {
        "Jan": 1, "January": 1,
        "Feb": 2, "February": 2,
        "Mar": 3, "March": 3,
        "Apr": 4, "April": 4,
        "May": 5, # May only gets one >:c
        "Jun": 6, "June": 6,
        "Jul": 7, "July": 7,
        "Aug": 8, "August": 8,
        "Sep": 9, "September": 9,
        "Oct": 10, "October": 10,
        "Nov": 11, "November": 11,
        "Dec": 12, "December": 12
    }
    return switcher.get(month, 0)

def find_dates(html, output=None):
    """
    Finds all dates within an HTML string
    Args:
        html (string): The HTML string to fetch dates from
        [output] (string): Optional filename to write the dates to
    Returns:
        list: A list of all dates as strings in a yyyy/mm/dd format. If day was not present, then yyyy/mm
    """
    # Regex for each date component (Month may be only first 3 letters)
    months = "(Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|June?|July?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|(?:Nov|Dec)(?:ember)?)"
    days = "([0-9]{1,2})"
    year = "([0-9]{4})"

    # Specify the four date formats
    DMY = f"(?:{days} )?{months} {year}"
    MDY = f"{months}(?: {days})?, {year}"
    YMD = f"{year} {months}(?: {days})?"
    ISO = "([0-9]{4})-([0-9]{2})-([0-9]{2})"

    # Replace all instances of each date format in the HTML
    # All formatted dates are encapsulated in two hashtags
    html = re.sub(DMY, lambda x:
            "#%s/%02d" % (x.group(3), month2num(x.group(2))) +
            ("/%02d#" % int(x.group(1)) if x.group(1) else "#"),
            html)
    html = re.sub(MDY, lambda x:
            "#%s/%02d" % (x.group(3), month2num(x.group(1))) +
            ("/%02d#" % int(x.group(2)) if x.group(2) else "#"),
            html)
    html = re.sub(YMD, lambda x:
            "#%s/%02d" % (x.group(1), month2num(x.group(2))) +
            ("/%02d#" % int(x.group(3)) if x.group(1) else "#"),
            html)

    # ISO is much simpler
    html = re.sub(ISO, "#\\1/\\2/\\3#", html)

    # Find and sort all dates in the new target format
    # Use the hashtag encapsulation to find only the previously formatted dates
    goal_format = "#([0-9]{4}/[0-9]{2}(?:/[0-9]{2})?)#"
    all_dates = re.findall(goal_format, html)
    all_dates.sort()

    # Write to file if argument was provided
    if output:
        write_to_file(output, all_dates)

    return all_dates

def write_to_file(output, dates):
    """
    Writes dates to file
    Args:
        output (string): filename to write to
        dates (list): list of dates to be written to file
    """
    f = open(output, "w")
    for d in dates:
        f.write(f"{d}\n")
    f.close()


if __name__ == "__main__":
    find_dates(get_html("https://en.wikipedia.org/wiki/Linus_Pauling"), "filter_dates_regex/Linus_Pauling.txt")
    find_dates(get_html("https://en.wikipedia.org/wiki/Rafael_Nadal"), "filter_dates_regex/Rafael_Nadal.txt")
    find_dates(get_html("https://en.wikipedia.org/wiki/J._K._Rowling"), "filter_dates_regex/J._K_Rowling.txt")
    find_dates(get_html("https://en.wikipedia.org/wiki/Richard_Feynman"), "filter_dates_regex/Richard_Feynman.txt")
    find_dates(get_html("https://en.wikipedia.org/wiki/Hans_Rosling"), "filter_dates_regex/Hans_Rosling.txt")
