#!/usr/bin/env python3
"""
This script gives people what they deserve on Twitter, and tries luck in 'RT
to win' competititons.
"""
import os
from urllib import parse
import psycopg2
from twitter import Twitter, OAuth, TwitterStream

import functions # Useful boilerplate functions for the overall Twitter bot.
import managers  # Useful classes for streaming and account handling.

# A different idea - use cookies to visit shortened links via visitors' devices.
# Maybe we can utilize 'RT to win' stuff by this same script.
# Use the below link for image search.
# https://www.google.co.in/search?site=imghp&tbm=isch&source=hp&biw=1280&bih=647&q=trump+funny+meme
# Also post images in replies.
# Implement PostgreSQL instead of reading from files.

# Fix the weird error on Heroku about expecting bytes instead of string!

try:
    ACCESS_TOKEN = os.environ['ACCESS_TOKEN'],
    ACCESS_SECRET = os.environ['ACCESS_SECRET'],
    CONSUMER_KEY = os.environ['CONSUMER_KEY'],
    CONSUMER_SECRET = os.environ['CONSUMER_SECRET']
    
    SHORTE_ST_TOKEN = os.environ['SHORTE_ST_TOKEN']
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:  # For local runs.
    from credentials import *

url = parse.urlparse(DATABASE_URL)

OAUTH = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
ACCOUNT_HANDLER = Twitter(auth=OAUTH)
STREAM_HANDLER = TwitterStream(auth=OAUTH)
ADMIN_HANDLER = TwitterStream(auth=OAUTH)


def main():
    """Main function to handle different activites of the account."""

    streamer = managers.StreamThread("Streamer",
        STREAM_HANDLER, ACCOUNT_HANDLER, url,
        functions.reply_with_shortened_url)  # For the troubling part.
    account_manager = managers.AccountThread(ACCOUNT_HANDLER, url, 60)  # For retweets, likes, follows.
    admin = managers.StreamThread(
        "Admin", ADMIN_HANDLER, ACCESS_SECRET, url, functions.admin_action)
    streamer.start()
    account_manager.start()
    admin.start()
    for thread in [streamer, account_manager, admin]:
        thread.join()


# Execute the main() function only if script is executed directly.
if __name__ == "__main__":
    print("Starting the bot...")
    main()
