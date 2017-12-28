"This script contains useful functions for building the Twitter bot."

import json

import psycopg2  # We're using postgres as our database system.
import requests
from lxml.html import fromstring
from credentials import SHORTE_ST_TOKEN
from twitter import TwitterHTTPError
# Here 't' is account handler defined in the main script.

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


def shorten_url(url):
    """Shortens the passed url using shorte.st's API."""

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


def reply_with_shortened_url(kwargs):  # Note the nontraditional use of kwargs.
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
    news_content = get_top_headline(tweet["user"]["name"])

    # rep_tweet = self.handler.search.tweets(
    #     q=tweet["user"]["name"],
    #     count=1, lang="en"
    #     )["statuses"][0]

    # tweet_link = \
    #     "https://twitter.com/"\
    #     + rep_tweet["user"]["screen_name"]\
    #     + "/status/"+rep_tweet["id_str"]

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
