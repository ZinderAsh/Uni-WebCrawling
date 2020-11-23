import requests as req

def get_html(url, params=None, output=None):
    """
    Requests the HTML of a website. Can also write the HTML to a file.
    Args:
        url (string): The URL of the website to get
        [params] (dict): Parameters to apply to the request
        [output] (string): The output file to optionally write the HTML to
    Returns:
        String: The HTML contents of the given website
    """
    resp = req.get(url, params=params)

    if output:
        write_to_file(output, resp)
        
    return resp.text

def write_to_file(output, resp):
    file = open(output, "w")
    file.write(f"{resp.url}\n\n")
    file.write(resp.text)
    file.close()

if __name__ == "__main__":
    wiki = "https://en.wikipedia.org/wiki/"
    get_html(f"{wiki}Studio_Ghibli", None, "requesting_urls/Studio_Ghibli.txt")
    get_html(f"{wiki}Star_Wars", None, "requesting_urls/Star_Wars.txt")
    get_html(f"{wiki}Dungeons_%26_Dragons", None, "requesting_urls/Dungeons_&_Dragons.txt")

    wiki = "https://en.wikipedia.org/w/"
    params = {"title": "Main_Page", "action": "info"}
    get_html(f"{wiki}index.php", params, "requesting_urls/Main_Page.txt")
    params = {"title": "Hurricane_Gonzalo", "oldid": "983056166"}
    get_html(f"{wiki}index.php", params, "requesting_urls/Hurricane_Gonzalo.txt")
