from filter_urls import find_articles
from requesting_urls import get_html
import regex as re
import time
import concurrent.futures
import threading

class Article:
    """
    Class to contains Article information
    Properties:
        url: The url to the article
        path: The full path from the source article
        score: The score rewarded from the keyword search
    """
    def __init__(self, url, parent=None):
        self.url = url
        self.path = [url]
        if parent:
            self.path += parent.path
        self.score = 0

class ArticleList:
    """
    Encapsulated list of articles to handle race conditions for threads
    """
    def __init__(self, articles):
        self.articles = articles
        self._lock = threading.Lock()

    def next_article(self):
        # Removes and returns the first article in the list
        with self._lock:
            if len(self.articles) > 0:
                article = self.articles[0]
                self.articles = self.articles[1:]
                return article
            else:
                return None

    def append(self, article):
        # Adds an article to the list
        with self._lock:
            self.articles.append(article)

    def insert(self, article):
        # Inserts a new Article to the list in a sorted position in regards to their score
        with self._lock:
            for i in range(len(self.articles)):
                if article.score > self.articles[i].score:
                    self.articles.insert(i, article)
                    return
            self.articles.append(article)

    def contains(self, article):
        # Checks if the list contains a specific article
        return article in self.articles

    def clear(self):
        # Emtpies the entire list
        with self._lock:
            self.articles = []

    def __len__(self):
        return len(self.articles)

def wiki_thread(goal, article, queue, visited, sub_articles, keywords, sleeptime=0.01):
    """
    Checks all sub articles from links in an article, grants them scores, and puts them in the queue
    Args:
        goal (string): The article it is trying to find a path to
        article (Article): The article the links were fetched from
        queue (ArticleList): The queue to insert sub articles into
        visited (ArticleList): The list of previusly visited articles
        sub_articles (ArticleList): The list of articles to be checked
        keywords (list): List of keywords to score articles by
        sleeptime (float): Time to sleep between each article
    """
    title_exp = re.compile("<title>(.+) -.+</title>")

    while True:
        time.sleep(sleeptime) # Slight delay to avoid denied responses
        l = sub_articles.next_article()
        # Stop when article list is empty
        if not l:
            break
        # Only search if link has not been visited already
        if not visited.contains(l):
            visited.append(l) # Add to visited list
            if l == goal:
                # The correct link was found!
                print("Done!")
                sub_articles.clear()
                return Article(l, article).path
            elif "en.w" in l and "/Main_Page" not in l:
                # Only check english wiki links and do not go to the Main Page. No cheating!

                # Tries to get the html repeatedly until the request is accepted.
                # In case a request is denied.
                html = None
                while not html:
                    try:
                        html = get_html(l)
                    except:
                        pass

                content = html.lower()
                item = Article(l, article)
                # Check for keywords in the HTML, to grant the Article a score
                for i in range(len(keywords)):
                    for k in keywords[i]:
                        if k in content:
                            # Grant points if keywords are in the HTML
                            item.score += [1, 10, 50][i]
                        if k.replace(" ", "_") in l.lower():
                            # Grant more points if keywords are in the URL
                            item.score += [5, 30, 100][i]
                # Insert Article into search queue in accordance to its score
                inserted = queue.insert(item)


def wiki_race(start, goal, output=None, greed=2, threads=4, sleeptime=0.01):
    """
    Finds the a short path between two wikipedia pages.
    It usually finds a short path, but may not always find the shortest, as it can grow quite greedy.
    Tried BFS, that didn't terminate and Wikipedia started denying my requests, so here we are!
    Ranks all articles by their keyword scores, and goes to the most promising articles first.
    If no articles look promising, it performs regular BFS.
    Args:
        start (string): The starting Wikipedia Article to find the path from
        goal (string): The Wikipedia article to find the path to
        [output] (string): Optional output file to write the path to
        [greed] (int): Specified how what keywords to consider when scoring articles
            0: No keywords are considered, pure BFS (THIS WILL TAKE FOREVER)
            1: High Priority keywords only, this will probably take a long time
            2: Mid-High Priority, this usually finds the best path (DEFAULT)
            3: All keywords. Rarely finds the best path, but does find a path very quickly
        [threads] (int): The amount of threads, too many might make Wikipedia deny requests eventually
            Default: 4, this works well as long as the algorithm isn't called excessively
        [sleeptime] (float): The time each thread sleeps before moving to next thread, to avoid denied requests
    Returns:
        list: An list containing the path from the start to the goal
    """

    goal_html = get_html(goal)

    # All the articles contents are in <p> objects
    goal_points = re.findall('<p>.*', goal_html)

    # Concatenate the content
    goal_content = ""
    for p in goal_points:
        goal_content += p
        goal_content += "\n"

    # Find (possibly) important keywords in the articles
    keywords = [
        # Low Priority, any single word from Mid and High priority
        [],
        # Mid Priority, the titles of any hyperlinks in the article
        re.findall('title="([^"#]*)"', goal_content),
        # High Priority, text that is in bold, as well as the title of the article
        re.findall('<b>([^<]*)</b>', goal_content) + [goal[goal.rindex("/"):].replace("_", " ")]
    ]

    # Remove special characters from keywords
    for i in range(len(keywords[1])):
        keywords[1][i] = (''.join(e for e in keywords[1][i] if e.isalnum() or e == " ")).lower()
    for i in range(len(keywords[2])):
        keywords[2][i] = (''.join(e for e in keywords[2][i] if e.isalnum() or e == " ")).lower()

    # Put all words in Mid and High priority in Low priority list
    for k in keywords[1] + keywords[2]:
        keywords[0] += k.split(' ')

    # Empty the keyword lists based on the greed argument
    if greed <= 0:
        keywords[2] = []
    if greed <= 1:
        keywords[1] = []
    if greed <= 2:
        keywords[0] = []

    # Remove short keywords to avoid words like "for", "of", etc.
    for i in range(len(keywords)):
        keywords[i] = [s for s in keywords[i] if len(s) > 3]

    # Print out the keywords
    print("LOW PRIORITY")
    for i in keywords[0]:
        print(i)
    print("\nMID PRIORITY")
    for i in keywords[1]:
        print(i)
    print("\nHIGH PRIORITY")
    for i in keywords[2]:
        print(i)
    print("\nSCANNING ARTICLES")

    # Create the thread-safe queue and visited lists
    queue = ArticleList([Article(start)])
    visited = ArticleList([start])

    while True:
        article = queue.next_article()
        # Stop when no articles remain in the queue
        if not article:
            break

        # Find all links in the article, and create a thread-safe list
        links = ArticleList(find_articles(article.url))

        # Print the score, url and number of sub-articles as a progress update
        print(f"{article.score}: {article.url} ({len(links)} sub-articles)")

        # Make 4 threads that check all the sub-articles for keywords. Any more than 4, and Wikipedia starts denying requests at some point
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(wiki_thread, goal, article, queue, visited, links, keywords) for i in range(threads)]

        # Check if any thread reported a valid path
        results = [f.result() for f in futures]
        for r in results:
            if r:
                if output:
                    f = open(output, "w")
                    for i in r:
                        f.write(f"{i}\n")
                    f.close()
                return r

if __name__ == "__main__":
    # Define starting and stopping positions
    start = "https://en.wikipedia.org/wiki/Parque_18_de_marzo_de_1938"
    goal = "https://en.wikipedia.org/wiki/Bill_Mundell"

    # Time the search, to report how long it took to find
    start_time = time.time()
    path = wiki_race(start, goal, output="wiki_race_challenge/shortest_way.txt")

    # Print the path
    print("\nPATH FOUND:")
    for i in path:
        print(i)

    # Report the step count and time
    print(f"The path is {len(path) - 1} steps long and took {time.time() - start_time}s to find.")
