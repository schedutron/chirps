"""
This script contains classes for account management as well as listening
and responding to Twitter info.
"""

import json
import random
import re
import time
import threading
import traceback
from urllib import parse  # For database connection/

import requests
# Useful functions for Twitter and scraping stuff.
import chirps.functions as functions
# For identifying offensive tweets.
from chirps.offensive import OFFENSIVE
try:
    from chirps.screen_name import screen_name
except ModuleNotFoundError:
    import os
    screen_name = os.environ['SCREEN_NAME']

# Perhaps using a database would be better if frequent updation is needed.
# This gets links to files containing relevant data.
# Add hashtabgs to tweets - they generate more views.
# Simply use Twitter to add keywords to the database instead of using Dropbox.
# Move fast and break things!
# Add ease of scaling down follow, like and retweet functionalities separately.
# Eventually create a dashboard for this sort of stuff.
# Eventually use different messages for different people.
# Why not use inheritance for different manager threads? IMPORTANT

class StreamThread(threading.Thread):
    """
    This class is to be used for listening specific people on Twitter and
    respond to them as soon as they tweet.
    """

    def __init__(self, identifier, stream_handler, account_handler, url, action_func):
        self.identifier = identifier
        threading.Thread.__init__(self)
        self.stream_handler = stream_handler
        self.handler = account_handler
        self.conn = functions.db_connect(url)
        print("Database connection successful.")
        self.cur = self.conn.cursor()
        self.db_access = {'conn': self.conn, 'cur': self.cur, 'url': url}  # To encapsulate db access data.
        self.action_func = action_func

    def run(self):
        """This is the function for main listener loop."""
        # TBD: Add periodic data checks to get updated data for messages, bads.
        # Listen to bad people.
        print(self.identifier, "started.")
        if self.identifier == 'Streamer':
            rel_name = 'accounts'
            print("Tracking:", end=" ")
        else:
            rel_name = 'admins'
            print("Admins:", end=" ")
        accounts = functions.get_accounts(self.db_access, rel_name)
        print(accounts)
        listener = self.stream_handler.statuses.filter(
            follow=','.join([str(account) for account in accounts])
        )
        while True:
            try:
                tweet = next(listener)
                # Check if the tweet is original - workaroud for now.
                # Listener also gets unwanted retweets, replies and so on.
                if tweet['user']['id'] not in accounts:  # The 'in' operation not very efficient?
                    # we have to ensure that the id is the person we're tracking. Maybe 'in' isn't good for that. 
                    continue
                kwargs = {'tweet': tweet, 'handler': self.handler, 'db_access': self.db_access}
                self.action_func(kwargs)  # Note the nontraditional use of kwargs here.
            except Exception as exception:
                # Loop shouldn't stop if error occurs, and exception should be
                # logged.
                print(json.dumps(tweet, indent=4))
                print(exception)
                print('-*-'*33)


class AccountThread(threading.Thread):
    """Account thread manages favoriting, retweeting and following people who
    tweet interesting stuff."""
    def __init__(self, handler, upload_handler, url, sleep_time, fav, retweet, follow, follow_limit, scrape):
        threading.Thread.__init__(self)
        self.handler = handler
        self.upload_handler = upload_handler
        self.conn = functions.db_connect(url)
        print("Database connection successful.")
        self.cur = self.conn.cursor()
        self.db_access = {'conn': self.conn, 'cur': self.cur, 'url': url}  # To encapsulate db access data.
        self.sleep_time = sleep_time
        self.fav = fav
        self.retweet = retweet
        self.follow = follow
        self.follow_limit = follow_limit
        self.scrape = scrape
        print('sleep_time: %s, fav: %s, retweet: %s, follow: %s, scrape: %s' %
              (self.sleep_time, self.fav, self.retweet, self.follow, self.scrape)
             )

    def run(self):
        """Main loop to handle account retweets, follows, and likes."""

        print("Account Manager started.")
        news = functions.find_news(self.scrape)
        subtract_string = ' -from:%s' % screen_name  # For not extracting self's tweets.
        while True:
            cur = functions.get_cursor(self.db_access)
            word = functions.get_keyword(cur)
            # Add '-from:TheRealEqualizer' in the following line.
            tweets = self.handler.search.tweets(
                q=word+subtract_string, count=100,
                lang="en")["statuses"]  # Understand OR operator.
            print("Chosen word:", word)

            if self.follow:
                friends_ids = self.handler.friends.ids(screen_name=screen_name)["ids"]
                if len(friends_ids) > follow_limit:

                    # To unfollow old follows because Twitter doesn't allow a large
                    # following / followers ratio for people with less followers.
                    # Using 4000 instead of 5000 for 'safety', so that I'm able to
                    # follow some interesting people manually even after a bot
                    # crash.

                    # Perhaps 1000 is the upper limit of mass unfollow in one go.

                    for _ in range(1000):
                        functions.unfollow(self.handler, friends_ids.pop())

            for tweet in tweets:
                try:
                    if re.search(OFFENSIVE, tweet["text"]) is None:
                        if self.fav and functions.fav_tweet(self.handler, tweet):
                            functions.print_tweet(tweet)
                            print()
                        if self.retweet and functions.retweet(self.handler, tweet) and not self.fav:
                            functions.print_tweet(tweet)
                            print()
                        if self.follow:
                            self.handler.friendships.create(_id=tweet["user"]["id"])
                            if "retweeted_status" in tweet:
                                op = tweet["retweeted_status"]["user"]
                                self.handler.friendships.create(_id=op["id"])

                    if self.scrape:
                        try:
                            item = next(news)
                        except StopIteration:
                            news = functions.find_news(self.scrape)
                            item = next(news)
                        # If it's a tuple, it contains media link, that's the
                        # protocol we follow.
                        if isinstance(item, tuple):
                            content = item[0]
                        else:
                            content = item
                        if not re.search(
                            r'(?i)this|follow|search articles', content
                            ):
                            print("Scraped: ", content)

                            # This uploads the relevant photo and gets it's
                            # id for attachment in tweet.
                            if isinstance(item, tuple):
                                photo_id = self.upload_handler.media.upload(
                                    media=requests.get(item[1]).content
                                    )["media_id_string"]

                                self.handler.statuses.update(
                                    status=item[0],
                                    media_ids=photo_id
                                    )
                            else:
                                self.handler.statuses.update(status=content)
                except Exception as exception:
                    print(exception)
                    traceback.print_exc()
                time.sleep(self.sleep_time)
