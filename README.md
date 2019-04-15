# ![chirps](1.png )

![Lines of code](https://tokei.rs/b1/github/schedutron/chirps)

Twitter bot powering www.twitter.com/arichduvet

Uses [@sixohsix](https://github.com/sixohsix)'s Python-based Twitter API for posting and other actions.
Scraping done with the help of [Kenneth Reitz](https://github.com/kennethreitz)'s `requests` module and some rudimentary regular expressions.

## Prerequisites

This bot framework is built in Python, so make sure Python 3.x is installed on your system. Once Python is installed, create a virtual environment in the root directory of this repo using the following command:

```$ python3 -m venv bot```

Then activate this virtual environment using:

```$ source bot/bin/activate``` (for Windows users this can look like `mkvirtualenv bot`)

Now install the dependencies using the following command:

```
$ pip install -r requirements.txt
```

You will need a PostgreSQL database service ready, a good free service is [ElephantSQL](https://elephantsql.com). Once you've set up an empty database, save its url.

For bot deployment, this framework uses [Heroku](https://heroku.com), so you'll also need a Heroku account.

## Setting It Up

After creating a new app on Heroku dashboard and installing the Heroku CLI on your machine, use the following commands to add a new remote to this repository:
```
$ heroku login
<enter your Heroku credentials>
...

$ heroku git:remote -a <your Heroku app name>
```

(You can setup a GitHub pipeline on Heroku, but instructions on setting it up are beyond the scope of this README.)

Now create a new branch for this repository, name it "deploy" and check it out:
```
$ git checkout -b deploy
```

Next, run the bot initialization script and enter the required information very carefully:

```
$ python3 chirps/init_script.py
```

The bot setup is essentially complete once this script executes successfully. Now you just need to "tune" certain options of the bot in the Heroku Procfile. Create a file named "Procfile" in the root of this repository and provide the configuration options as per your needs:

```
[Procfile] # Do not include this in file
worker: python3 -m chirps.main --rate=300 --fav --retweet --follow --follow_limit=6000 --scrape scrape_thenewstack get_tech_news
```

For example, the above Procfile says "Tweet every 5 minutes (300 seconds), like (favorite) and follow tweets (those tweets that have keywords specified in `init_script.py`), keep following people tweeting about those keywords till your following count reaches 6000, and use scraper functions `scrape_thenewstack()` and `get_tech_news()` for aggregating content to be tweeted by your bot. You can build your own scraper functions in `scrapers.py` and tune other parameters as per your requirements.
