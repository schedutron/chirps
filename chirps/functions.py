"This script contains useful functions for building the Twitter bot."

import json
import random
import re
import unicodedata

import psycopg2  # We're using postgres as our database system.
import requests
from lxml.html import fromstring
import nltk  # Used here to split paragraphs into sentences.
nltk.download('punkt')
from twitter import TwitterHTTPError

def reply(account_handler, tweet_id, user_name, msg):
    """
    Sends msg as reply to the tweet whose id is passed.
    user_name of the tweet's author is required as per Twitter API docs.
    """

    account_handler.statuses.update(
        status='@%s %s' % (user_name, msg),
        in_reply_to_status_id=tweet_id
        )


def print_tweet(tweet):
    """Displays the primary contents of a tweet, maybe except links."""

    print(tweet["user"]["name"])
    print(tweet["user"]["screen_name"])
    print(tweet["created_at"])
    print(tweet["text"])
    hashtags_list = []
    hashtags = tweet["entities"]["hashtags"]
    for tag in hashtags:
        hashtags_list.append(tag["text"])
    print(hashtags_list)


def fav_tweet(account_handler, tweet):
    """Favorites a passed tweet and returns a success status - 0 if successful
    otherwise 1.
    """
    try:
        account_handler.favorites.create(_id=tweet['id'])
        return 0
    except TwitterHTTPError:
        return 1


def retweet(account_handler, tweet):
    """Retweets a passed tweet and returns a success status - 0 if successful
    otherwise 1.
    """

    try:
        account_handler.statuses.retweet._id(_id=tweet["id"])
        return 0

    except TwitterHTTPError:
        return 1


def quote_tweet(account_handler, tweet, text):
    """Quotes a passed tweet with a passed text and then tweets it."""

    # May not work for long links because of 140-limit. Can be improved.
    tweet_id = tweet["id"]
    screen_name = tweet["user"]["screen_name"]
    link = "https://twitter.com/%s/status/%s" % (screen_name, tweet_id)
    try:
        string = text + " " + link
        account_handler.statuses.update(status=string)
        return 0
    except TwitterHTTPError:
        return 1


def unfollow(account_handler, iden):
    """Unfollows the person identified by 'iden', returns 0 if successful,
    otherwise 0."""
    try:
        account_handler.friendships.destroy(_id=iden)
        return 0
    except TwitterHTTPError:
        return 1


def get_tech_news():  # I'm adventuring with regular expressions for parsing!
    """Finds news for tweeting, along with their links."""
    news_block_expr = re.compile(
        r'(?s)<a class="story-link".*?href="(.*?)".*?>.*?<h2.*?>(.*?)</h2>.*?'
        r'<img.*?src="(.*?)".*?>.*?</a>'
    )
    latest_expr = re.compile(
        r'(?s)<ol class="story-menu theme-stream initial-set">(.*)</ol>'
    )
    nyTech = requests.get('https://nytimes.com/section/technology')
    latest = latest_expr.search(nyTech.text)
    news_blocks = news_block_expr.findall(latest.group(1))
    news = []
    for i in range(len(news_blocks)):
        item = (
            news_blocks[i][1].strip() + ' ' + shorten_url(news_blocks[i][0]),
            news_blocks[i][2].strip())  # This is img src.
        if item[1].startswith('Daily Report: '):
            item = item[14:]
        yield item


def scrape_themerkle(num_pages=17):
    """Scrapes news links from themerkle.com"""
    links = []
    for i in range(num_pages):
        r = requests.get("https://themerkle.com/page/%i" % (i+1))
        tree = fromstring(r.content)
        collection = tree.xpath("//h2[@class='title front-view-title']/a/@href")
        links.extend(collection)

    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    for link in links:
        r = requests.get(link)
        tree = fromstring(r.content)
        paras = tree.xpath('//div[@class="thecontent"]/p')
        paras = [para.text_content() for para in paras if para.text_content()]
        para = random.choice(paras)
        para = tokenizer.tokenize(para)
        # To fix unicode issues:
        para = [unicodedata.normalize('NFKD', text) for text in para]
        for i in range(10):
            text = random.choice(para)
            if text and 60 < len(text) < 210:
                break
        else:
            continue
        yield '"%s" %s' % (text, link)


def find_news(newsfuncs):
    """Interface to get news from different news scraping functions."""
    news_iterators = []
    for func in newsfuncs:
        news_iterators.append(globals()[func]())
    while True:
        for i, iterator in enumerate(news_iterators):
            try:
                yield next(iterator)
            except StopIteration:
                news_iterators[i] = globals()[newsfuncs[i]]()


def shorten_url(url):
    """Shortens the passed url using shorte.st's API."""
    from chirps.credentials import SHORTE_ST_TOKEN
    response = requests.put(
        "https://api.shorte.st/v1/data/url",
        {"urlToShorten": url}, headers={"public-api-token": SHORTE_ST_TOKEN}
        )
    info = json.loads(response.content.decode())
    if info["status"] == "ok":
        return info["shortenedUrl"]
    return url  # If shortening fails, the original url is returned.


def get_top_headline(query):
    """Gets top headline for a query from Google News.
    Returns in format (headline, link)."""

    # Following assumes that query doesn't contain special characters.
    url_encoded_query = '%20'.join(query.split())
    req = "https://news.google.com/news/search/section/q/" + url_encoded_query

    tree = fromstring(requests.get(req).content)
    news_item = tree.find(".//main/div/c-wiz/div/c-wiz")
    headline = news_item.xpath('.//a/text()')[0].strip()
    link = news_item.xpath('.//a/@href')[0].strip()

    return (headline, link)


def get_keyword(cursor):
    """Returns a random keyword from the database."""
    cursor.execute(
        "SELECT word FROM keywords " +
        "OFFSET floor(random()*(SELECT COUNT(*) FROM keywords)) LIMIT 1"
        )

    return cursor.fetchall()[0][0]


def get_message(cursor):
    """Returns a random message from the database.
    Functionality bound to change."""
    cursor.execute(
        "SELECT message FROM messages " +
        "OFFSET floor(random()*(SELECT COUNT(*) FROM messages)) LIMIT 1"
        )

    return cursor.fetchall()[0][0]


def get_accounts(db_access, rel_name):
    """To get the accounts to track."""
    cur = get_cursor(db_access)
    cur.execute("SELECT * FROM %s" %  str(rel_name))
    rows = cur.fetchall()
    accounts = [row[0] for row in rows]
    return accounts


def db_connect(url):
    """Returns a database connection object."""
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    return conn


def get_cursor(db_access):
    """To get cursor for interacting with database."""
    if db_access['conn'].closed:
        db_access['conn'] = db_connect(db_access['url'])
        db_access['cur'] = db_access['conn'].cursor()
    return db_access['cur']


def reply_with_shortened_url(kwargs, use_short_url=False):  # Note the nontraditional use of kwargs.
    """Function for replying to the tweet with a shortened url."""
    tweet = kwargs['tweet']
    handler = kwargs['handler']
    db_access = kwargs['db_access']

    # Gets messages to tweet.
    cur = get_cursor(db_access)
    message = get_message(cur)
    # If they tweet, send them a kinda slappy reply.

    # reply(self.handler,
    #     tweet['id'],
    #     tweet['user']['screen_name'],
    #     random.choice(messages)
    # )
    # max_length = 0
    # for word in tweet["text"].split():  # Finds the largest word.
    #     if len(word) > max_length:
    #         max_length = len(word)
    #         max_word = word

    # Searches for a related news, later add images.

    # rep_tweet = self.handler.search.tweets(
    #     q=tweet["user"]["name"],
    #     count=1, lang="en"
    #     )["statuses"][0]

    # tweet_link = \
    #     "https://twitter.com/"\
    #     + rep_tweet["user"]["screen_name"]\
    #     + "/status/"+rep_tweet["id_str"]
    short_url = ''
    if use_short_url:
        news_content = get_top_headline(tweet["user"]["name"])
        short_url = shorten_url(news_content[1])
    # message = random.choice(messages) + " " + short_url
    # Instead of a catchy but unrelated text, tweet the headline
    # itself with the short link.
    cur = get_cursor(db_access)

    message = get_message(get_cursor(db_access)) + ' ' + short_url

    reply(
        handler,
        tweet['id'],
        tweet['user']['screen_name'],
        message
    )

    # Print tweet for logging.
    print("Tweet:")
    print_tweet(tweet)
    print('*'*33+ "\nReply:")
    print(message, end='\n\n')


def admin_action(kwargs):
    """Function to manage different administrator tasks."""
    pass
