"""
Script defining my Twitter bot, using sixohsix's Python wrapper for the
Twitter API.
"""

# Currently, news images are small. Make them large.
# Employ machine learning - follow only those people who follow back,
# and unfollow only those people who don't unfollow back!
# Instead of searching tweets and then doing actions on them, why not try
# streaming interesting tweets in realtime and then performing actions on them?

import html.parser
import json
import os
import random
import re
import requests
import threading
import time
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import webbrowser

parser = html.parser.HTMLParser()  # Used in find_news()

# Following offensive compilation is not my stuff.
# Copyright (c) 2013-2017 Molly White.
offensive = re.compile(
    r"\b(deaths?|dead(ly)?|die(s|d)?|hurts?|(sex(ual(ly)?)?|"
    r"child)[ -]?(abused?|trafficking|"
    r"assault(ed|s)?)|injur(e|i?es|ed|y)|kill(ing|ed|er|s)?s?|"
    r"wound(ing|ed|s)?|fatal(ly|ity)?|"
    r"shoo?t(s|ing|er)?s?|crash(es|ed|ing)?|attack(s|ers?|ing|ed)?|"
    r"murder(s|er|ed|ing)?s?|"
    r"hostages?|(gang)?rap(e|es|ed|ist|ists|ing)|assault(s|ed)?|"
    r"pile-?ups?|massacre(s|d)?|"
    r"assassinate(d|s)?|sla(y|in|yed|ys|ying|yings)|victims?|"
    r"tortur(e|ed|ing|es)|"
    r"execut(e|ion|ed|ioner)s?|gun(man|men|ned)|suicid(e|al|es)|"
    r"bomb(s|ed|ing|ings|er|ers)?|"
    r"mass[- ]?graves?|bloodshed|state[- ]?of[- ]?emergency|al[- ]?Qaeda|"
    r"blasts?|violen(t|ce)|"
    r"lethal|cancer(ous)?|stab(bed|bing|ber)?s?|casualt(y|ies)|"
    r"sla(y|ying|yer|in)|"
    r"drown(s|ing|ed|ings)?|bod(y|ies)|kidnap(s|ped|per|pers|ping|pings)?|"
    r"rampage|beat(ings?|en)|"
    r"terminal(ly)?|abduct(s|ed|ion)?s?|missing|behead(s|ed|ings?)?|"
    r"homicid(e|es|al)|"
    r"burn(s|ed|ing)? alive|decapitated?s?|jihadi?s?t?|hang(ed|ing|s)?|"
    r"funerals?|traged(y|ies)|"
    r"autops(y|ies)|child sex|sob(s|bing|bed)?|pa?edophil(e|es|ia)|"
    r"9(/|-)11|Sept(ember|\.)? 11|"
    r"genocide)\W?\b",
    flags=re.IGNORECASE)

news_block_expr = re.compile(
    r'(?s)<a class="story-link".*?href="(.*?)".*?>.*?<h2.*?>(.*?)</h2>.*?'
    r'<img.*?src="(.*?)".*?>.*?</a>'
    )
latest_expr = re.compile(
    r'(?s)<ol class="story-menu theme-stream initial-set">(.*)</ol>'
    )

try:
    oauth = OAuth(
        os.environ['ACCESS_TOKEN'],
        os.environ['ACCESS_SECRET'],
        os.environ['CONSUMER_KEY'],
        os.environ['CONSUMER_SECRET']
    )
    SHORTE_ST_TOKEN = os.environ['SHORTE_ST_TOKEN']
except KeyError:  # For local tests.
    with open('credentials', 'r') as secret:
        exec(secret.read())
        oauth = OAuth(
            ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET
        )

t = Twitter(auth=oauth)
# For uploading photos.
t_upload = Twitter(auth=oauth, domain="upload.twitter.com")

ts = TwitterStream(auth=oauth)
tu = TwitterStream(auth=oauth, domain="userstream.twitter.com")

# Following are some useful wrappers for Twitter-related functionalities.


def pf(sn):
    """
    Attempts to print the followers of a user, provided their
    screen name.
    """

    cursor = -1
    next_cursor = 1
    while cursor != 0:
        followers = t.followers.list(screen_name=sn, cursor=cursor)
        f = followers["users"]
        for follower in f:
            print(follower["screen_name"])
        cursor = followers["next_cursor"]


def fav_tweet(tweet):
    """Attempts to favorite a tweet."""

    t.favorites.create(_id=tweet['id'])


def retweet(tweet):
    """Attempts to retweet a tweet."""

    t.statuses.retweet._id(_id=tweet["id"])


def quote_tweet(tweet, text):
    """Quotes a tweet with text."""
    # May not work for long links because of 140-limit. Can be improved.
    id = tweet["id"]
    sn = tweet["user"]["screen_name"]
    link = "https://twitter.com/%s/status/%s" % (sn, id)
    string = text + " " + link
    t.statuses.update(status=string)


def search_and_fav(keyword, num):
    """Searches tweets having a keyword and likes them."""

    tweets = t.search.tweets(
        q=keyword, result_type="recent", count=num, lang="en"
        )["statuses"]
    first = tweets[0]["text"]
    last = tweets[-1]["text"]
    success = 0
    tweets.reverse()
    for tweet in tweets:
        if fav_tweet(tweet):
            success += 1
    print("Favorited %i tweets." % success)
    print("First's text:", first)
    print("Last's text:", last)


def search_and_follow(text, num):  # Improve this! Inaccurate feedback!
    """Searches tweets for a keyword and followers their tweet-ers."""

    tweets = t.search.tweets(q=text, lang="en", count=num)
    tweets = tweets["statuses"]
    success = 0
    for tweet in tweets:
        try:
            t.friendships.create(_id=tweet["user"]["id"])
            success += 1
        except Exception as e:
            print(e)
    print("Followed %i people." % success)


def unfollow(iden):
    """Attempts to unfollow a user, provided their id."""

    t.friendships.destroy(_id=iden)


def print_tweet(tweet):
    """Displays the primary info of a tweet."""

    print(tweet["user"]["name"])
    print(tweet["user"]["screen_name"])
    print(tweet["created_at"])
    print(tweet["text"])
    hashtags = []
    hs = tweet["entities"]["hashtags"]
    for h in hs:
        hashtags.append(h["text"])
    print(hashtags)


def find_news():  # I'm adventuring with regular expressions for parsing!
    """Finds news for tweeting, along with their links."""

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
        news.append(item)

    '''tv = requests.get('https://theverge.com', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'})
    feed_patt = r'(?s)<div class="c-compact-river">(.*?)<div class="l-col__sidebar"'
    bunches = re.findall(feed_patt, tv.text)
    verge_news = []
    for cluster in bunches:
        snippets = re.findall(r'<h2.*?><a.*>(.*?)</a></h2>', cluster)
        verge_news.extend(snippets)
    for item in verge_news:
        news.append(parser.unescape(item))
    random.shuffle(news) #to bring a feel of randomness'''
    return news


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


# Confused stuff happened during the initialization at Heroku on
# Saturday, 4 Feb, 2017: around 2 pm.

# See the confused_stuff snap.
# By the way, confused stuff still happens sometimes.
class AccountThread(threading.Thread):
    def __init__(self, handler, upload_handler=None):
        self.t = handler
        self.t_upload = upload_handler

    def print_followers(self, username):
        """Method to print the followers of a user."""
        try:
            followers = self.t.followers.ids(screen_name=username)
            c = followers["next_cursor"]
            while c != -1:
                followers = self.t.followers.list(
                    screen_name=username,
                    cursor=c
                    )
                f = followers["users"]

                for follower in followers:
                    print(follower["screen_name"])
                c = followers["next_cursor"]
        except Exception as e:
            print("------")
            print(e)
            print("------")

    def run(self):
        """Main loop to handle account retweets, follows, and likes."""

        print("Account Manager started.")
        news = []
        while 1:
            with requests.get(
                "https://dl.dropboxusercontent.com"
                "/s/zq02iogqhx5x9j2/keywords.txt?dl=0"
                ) as keywords:
                    words = [word.strip() for word in keywords.text.split()]
            word = random.choice(words)
            tweets = self.t.search.tweets(
                q=word+' -from:arichduvet', count=199, lang="en"
                )["statuses"]  # Understand OR operator.
            fr = self.t.friends.ids(screen_name="arichduvet")["ids"]
            """
            The purpose of following if:
            To unfollow old follows because Twitter doesn't allow a large
            following / followers ratio for people with less followers.
            Using 4990 instead of 5000 for 'safety', so that I'm able
            to follow some interesting people manually even after a
            bot crash.
            """
            if len(fr) > 4200:
                # Perhaps the upper limit for mass unfollow is 1000 a day.
                for i in range(500):
                    unfollow(fr.pop())

            for tweet in tweets:
                try:
                    # Following if: So that bad tweets don't come into play.
                    if re.search(offensive, tweet["text"]) is None:
                        print("Search tag:", word)
                        print_tweet(tweet)
                        print()
                        fav_tweet(tweet)
                        retweet(tweet)
                        # Disabling follows for a while.
                        """
                        self.t.friendships.create(_id=tweet["user"]["id"])
                        if "retweeted_status" in tweet:
                            op = tweet["retweeted_status"]["user"]
                            self.t.friendships.create(_id=op["id"])
                        """
                        if not news:
                            news = find_news()
                        item = news.pop()
                        if not re.search(
                            r'(?i)this|follow|search articles',
                            item[0]
                            ):
                            print("Scraped: ", item[0])

                            # This uploads the relevant photo and gets it's
                            # id for attachment in tweet.
                            photo_id = self.t_upload.media.upload(
                                media=requests.get(item[1]).content
                                )["media_id_string"]

                            self.t.statuses.update(
                                status=item[0],
                                media_ids=photo_id
                                )

                    else:
                        print("[No offense]:", tweet["text"])
                except Exception as e:
                    print("------")
                    print(e)
                    print("------")
                time.sleep(61)


class StreamThread(threading.Thread):
    def __init__(self, handler):
        """Constructor for this class, sets the handler for streaming."""
        threading.Thread.__init__(self)
        self.ts = handler

    def run(self):
        """This is the function for main listener loop."""
        # TBD: Add periodic data checks to get updated data for messages, bads.
        # Listen to bad people.
        print("Streamer started.")
        listener = self.ts.statuses.filter(
            follow=','.join(
                [str(bad) for bad in bads]
            )
        )
        while True:
            try:
                tweet = next(listener)
                """
                Check if the tweet is original - workaroud for now. listener
                also gets unwanted retweets, replies and so on.
                """
                if tweet['user']['id'] not in bads:
                    print("Ignored from:", tweet['user']['screen_name'])
                    continue
                # Gets messages to tweet.
                with requests.get(links['messages']) as messages_file:
                    messages = messages_file.text.split('\n')[:-1]
                # If they tweet, send them a kinda slappy reply.
                reply(
                    tweet['id'],
                    tweet['user']['screen_name'],
                    random.choice(messages)
                )
                # Print tweet for logging.
                print('-*-'*33)
                print_tweet(tweet)
            except Exception as e:  # So that loop still continues.
                print(json.dumps(tweet, indent=4))
                print(e)
            print('-*-'*33)


def main():
    """Main function to handle different activites of the account."""
    #streamer = StreamThread(ts)  # For the reply and dm's part.

    # For retweets, likes, follows.
    account_manager = AccountThread(t, t_upload)
    #streamer.start()
    account_manager.run()


if __name__ == "__main__":
    main()
