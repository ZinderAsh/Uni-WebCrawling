import regex as re
from requesting_urls import get_html

def find_urls(html, url=None, output=None):
    """
    Finds all URLs within a body of HTML
    Args:
        html (string): The HTML string to find URLs in
        [url] (string): The URL of the HTML to make relative links complete
    Returns:
        list: A list of all URLs found within the HTML
    """
    # Find elements starting with <a, then any characters until it meets the href with the URL
    urls = re.findall('<a[^(?:href)]*href="([^"#]*)"', html)
    if url:
        # Add base URL to all relative URLs
        base = re.compile('(https://[^/]*)')
        base_url = base.match(url).group(1)
        urls = [s if base.search(s) else f"{base_url}{s}" for s in urls]

    if output:
        write_to_file(output, urls)

    return urls

def find_articles(url, output=None):
    """
    Finds all Wikipedia article links within a Wikipedia page.
    Args:
        url (string): The URL of the wikipedia page to fetch
        [output] (string): Optional filename to write urls to
    Returns:
        list: List of Wikipedia article URLs
    """
    html = get_html(url)
    urls = find_urls(html, url)
    # Article test, URL must either be relative or have a wikipedia URL
    is_wiki_url = re.compile('(?:^|wikipedia.org)/wiki/')
    # Check if the URL is a namespace (contains a colon)
    is_namespace = re.compile('https://[^:]*:')
    # Create a list containing only URLs that passes the article test and is not a namespace
    article_urls = [url for url in urls if is_wiki_url.search(url) and not is_namespace.search(url)]

    if output:
        write_to_file(output, article_urls)

    return article_urls

def write_to_file(output, urls):
    """
    Writes urls to file
    Args:
        output (string): filename to write to
        urls (list): list of urls to be written to file
    """
    f = open(output, "w")
    for i in urls:
        f.write(f"{i}\n")
    f.close()

if __name__ == "__main__":
    find_urls(get_html("https://en.wikipedia.org/wiki/Nobel_Prize"), "https://en.wikipedia.org/wiki/Nobel_Prize", "filter_urls/Nobel_Prize_urls.txt")
    find_urls(get_html("https://en.wikipedia.org/wiki/Bundesliga"), "https://en.wikipedia.org/wiki/Bundesliga", "filter_urls/Bundesliga_urls.txt")
    find_urls(get_html("https://en.wikipedia.org/wiki/2019%E2%80%9320_FIS_Alpine_Ski_World_Cup"), "https://en.wikipedia.org/wiki/2019%E2%80%9320_FIS_Alpine_Ski_World_Cup", "filter_urls/2019-20_FIS_Alpine_Ski_World_Cup_urls.txt")

    find_articles("https://en.wikipedia.org/wiki/Nobel_Prize", "filter_urls/Nobel_Prize_articles.txt")
    find_articles("https://en.wikipedia.org/wiki/Bundesliga", "filter_urls/Bundesliga_articles.txt")
    find_articles("https://en.wikipedia.org/wiki/2019%E2%80%9320_FIS_Alpine_Ski_World_Cup", "filter_urls/2019-20_FIS_Alpine_Ski_World_Cup_articles.txt")
