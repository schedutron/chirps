#!/usr/bin/env python3
"""Script for initializing credentials and database for the bot."""
# Bound to change (a lot!)

import argparse
from urllib.parse import urlparse
from chirps.functions import db_connect

parser = argparse.ArgumentParser()
parser.add_argument("db_url", help="Postgres database url")
args = parser.parse_args()

url = urlparse(args.db_url)
conn = db_connect(url)
cur = conn.cursor()

# Create database.
cur.execute("CREATE TABLE keywords(word varchar)")
conn.commit()
print("Enter keywords to be followed one by one. When done, type 'exit':")
words = []
while True:
    word = input()
    if word.lower() == "exit":
        break
    words.append(word)

for word in words:
    cur.execute("INSERT INTO keywords VALUES(%s)", (word,))
conn.commit()

cur.execute("CREATE TABLE accounts(id bigint)")
conn.commit()
print("\nEnter account id's (NOT usernames) to be tracked, one by one. When done, type 'exit':")
accounts = []
while True:
    account = input()
    if account.lower() == "exit":
        break
    accounts.append(int(account))
for account in accounts:
    cur.execute("INSERT INTO accounts VALUES(%s)", (account,))
conn.commit()

cur.execute("CREATE TABLE admins(id bigint)")
conn.commit()

print("\nEnter admins' id's (NOT usernames) to be tracked, one by one. When done, type 'exit':")
admins = []

while True:
    admin = input()
    if admin.lower() == "exit":
        break
    admins.append(int(admin))
for admin in admins:
    cur.execute("INSERT INTO admins VALUES(%s)", (admin,))
conn.commit()

cur.execute("CREATE TABLE messages(message varchar)")
conn.commit()

print("\nEnter reply messages one by one. When done, type 'exit':")
messages = []
while True:
    message = input()
    if message.lower() == "exit":
        break
    messages.append(message)
for message in messages:
    cur.execute("INSERT INTO messages VALUES(%s)", (message,))
conn.commit()

print("\nDatabase initialized successfully!")

print("\nNow enter your credentials: ")

access_token = input("Access token: ")
access_secret = input("Access secret: ")
consumer_key = input("Consumer key: ")
consumer_secret = input("Consumer secret: ")
shorte_st_token = input("shorte.st token: ")

with open("chirps/credentials.py", "w") as f:
    f.write("ACCESS_TOKEN='%s'\n" % access_token)
    f.write("ACCESS_SECRET='%s'\n" % access_secret)
    f.write("CONSUMER_KEY='%s'\n" % consumer_key)
    f.write("CONSUMER_SECRET='%s'\n" % consumer_secret)
    f.write("DATABASE_URL='%s'\n" % args.db_url)
    f.write("SHORTE_ST_TOKEN='%s'\n" % shorte_st_token)
print("\ncredentials.py created successfully!")

screen_name = input("Enter your Twitter username: ")
with open("chirps/screen_name.py", "w") as f:
    f.write("screen_name='%s'\n" % screen_name)
print("\nscreen_name.py created successfully!")