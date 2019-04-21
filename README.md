# ![chirps](1.png )

![Lines of code](https://tokei.rs/b1/github/schedutron/chirps)

Twitter bot powering www.twitter.com/arichduvet

Uses [@sixohsix](https://github.com/sixohsix)'s Python-based Twitter API for posting and other actions.
Scraping done with the help of [Kenneth Reitz](https://github.com/kennethreitz)'s `requests` module and some rudimentary regular expressions.

## Prerequisites

This bot framework is built in Python, so make sure Python 3.x is installed on your system. Once Python is installed, create a virtual environment in the root directory of this repo using the following command:

```$ python3 -m venv bot```

Then activate this virtual environment using:

```$ source bot/bin/activate``` (for Windows users this can look like `workon bot`)

Now install the dependencies using the following command:

```
$ pip install -r requirements.txt
```

You will need a PostgreSQL database service ready, a good free service is [ElephantSQL](https://elephantsql.com). Once you've set up an empty database, save its url (it'll be needed while running `init_script` below).

For bot deployment, this framework uses [Heroku](https://heroku.com), so you'll also need a Heroku account.

## Setting It Up

After creating a new app on Heroku dashboard, install the Heroku CLI on your machine. Then use the following commands to add a new remote to this repository:
```
$ heroku login
<enter your Heroku credentials>
...

$ heroku git:remote -a <your Heroku app name>
```

(You can setup a GitHub pipeline on Heroku, but instructions on setting it up are beyond the scope of this README.)

Now create a new branch for this repository, name it "deploy" and check it out:
```
$ gi checkout -b deploy
```

Remove the `chirps/credentials.py` and `chirps/screen_name.py` entries from the `.gitignore` file. The file should now look like:

```
[.gitignore]
.DS_Store
.env
bot/
.vscode/
chirps/__pycache__/
```

Next, run the bot initialization script and enter the required information very carefully:

```
$ python -m chirps.init_script <your database URL>
```

The bot setup is essentially complete once this script executes successfully. Now you just need to "tune" certain options of the bot in the Heroku Procfile. Create a file named "Procfile" in the root of this repository and provide the configuration options as per your needs:

```
[Procfile] # Do not include this in file
worker: python3 -m chirps.main --rate=300 --fav --retweet --follow --follow_limit=6000 --scrape scrape_thenewstack get_tech_news
```

For example, the above Procfile says "Tweet every 5 minutes (300 seconds), like (favorite) and follow tweets (those tweets that have keywords specified in `init_script.py`), keep following people tweeting about those keywords till your following count reaches 6000, and use scraper functions `scrape_thenewstack()` and `get_tech_news()` for aggregating content to be tweeted by your bot. You can build your own tweet-er functions (usually scrapers) in `scrapers.py` (they should `return` or `yield` strings, which will be tweeted by your bot) and tune other parameters as per your requirements.

Finally, deploy your bot using the following command:
```
$ git push heroku deploy:master
```

Once the deployment completes, "switch on" the bot as follows:
```
$ heroku ps:scale worker=1
```

Now your bot should be up and running!
***

If you want to dig deeper into the codebase and know more about the implementation of "generator-of-generators" function in `chirps/functions.py`, see [my tutorial on DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-scrape-web-pages-and-post-content-to-twitter-with-python-3) which explains that part in detail.
