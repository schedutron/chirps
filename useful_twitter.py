from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import webbrowser, time, random, re

offensive = re.compile(
    r"\b(deaths?|dead(ly)?|die(s|d)?|hurts?|(sex(ual(ly)?)?|child)[ -]?(abused?|trafficking|"
    r"assault(ed|s)?)|injur(e|i?es|ed|y)|kill(ing|ed|er|s)?s?|wound(ing|ed|s)?|fatal(ly|ity)?|"
    r"shoo?t(s|ing|er)?s?|crash(es|ed|ing)?|attack(s|ers?|ing|ed)?|murder(s|er|ed|ing)?s?|"
    r"hostages?|(gang)?rap(e|es|ed|ist|ists|ing)|assault(s|ed)?|pile-?ups?|massacre(s|d)?|"
    r"assassinate(d|s)?|sla(y|in|yed|ys|ying|yings)|victims?|tortur(e|ed|ing|es)|"
    r"execut(e|ion|ed|ioner)s?|gun(man|men|ned)|suicid(e|al|es)|bomb(s|ed|ing|ings|er|ers)?|"
    r"mass[- ]?graves?|bloodshed|state[- ]?of[- ]?emergency|al[- ]?Qaeda|blasts?|violen(t|ce)|"
    r"lethal|cancer(ous)?|stab(bed|bing|ber)?s?|casualt(y|ies)|sla(y|ying|yer|in)|"
    r"drown(s|ing|ed|ings)?|bod(y|ies)|kidnap(s|ped|per|pers|ping|pings)?|rampage|beat(ings?|en)|"
    r"terminal(ly)?|abduct(s|ed|ion)?s?|missing|behead(s|ed|ings?)?|homicid(e|es|al)|"
    r"burn(s|ed|ing)? alive|decapitated?s?|jihadi?s?t?|hang(ed|ing|s)?|funerals?|traged(y|ies)|"
    r"autops(y|ies)|child sex|sob(s|bing|bed)?|pa?edophil(e|es|ia)|9(/|-)11|Sept(ember|\.)? 11|"
    r"genocide)\W?\b",
    flags=re.IGNORECASE) #Copyright (c) 2013-2016 Molly White
    #Above offensive compilation is not my stuff

# Variables that contain the user credentials to access Twitter API





oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)

t = Twitter(auth=oauth)
ts = TwitterStream(auth=oauth)
if __name__ == "__main__":
    webbrowser.open("http://twitter.com")

#useful Python functions

def print_followers(username):
    try:
        c = 0
        while(c!=-1):
            followers = t.followers.list(screen_name=username, cursor = c)
            f = followers["users"]

            for follower in followers:
                print follower["screen_name"]
                c = followers["next_cursor"]
    except:
        pass

def pf(sn): #better version for above (rate limiting problem?)
     cursor = -1
     next_cursor=1
     while cursor != 0:
             followers = t.followers.list(screen_name=sn, cursor=cursor)
             f = followers["users"]
             for follower in f:
                     print follower["screen_name"]
             cursor = followers["next_cursor"]

def fav_tweet(tweet):
     try:
             result = t.favorites.create(_id=tweet['id'])
             return 1
     except TwitterHTTPError:
             return 0

def retweet(tweet):
     try:
             t.statuses.retweet._id(_id=tweet["id"])
             return 1
     except TwitterHTTPError:
             return 0

def quote_tweet(tweet, text): #may not work for long links because of 140-limit. Can be improved.
     id = tweet["id"]
     sn = tweet["user"]["screen_name"]
     link = "https://twitter.com/%s/status/%s" %(sn, id)
     try:
             string = text + " " + link
             t.statuses.update(status=string)
             return 1
     except TwitterHTTPError:
             return 0

def search_and_fav(keyword, num):
     tweets = t.search.tweets(q=keyword, result_type="recent", count=num, lang="en")["statuses"]
     first = tweets[0]["text"]
     last = tweets[-1]["text"]
     success = 0
     tweets.reverse()
     for tweet in tweets:
             if fav_tweet(tweet):
                     success += 1
     print "Favorited %i tweets." % success
     print "First's text:", first
     print "Last's text:", last

def search_and_follow(text, num): #improve this! Inaccurate feedback!
     tweets = t.search.tweets(q=text, lang="en", count=num)
     tweets = tweets["statuses"]
     success = 0
     for tweet in tweets:
             try:
                     t.friendships.create(_id=tweet["user"]["id"])
                     success += 1
             except:
                     pass
     print "Followed %i people." % success

def unfollow(iden):
        success = 0
        try:
            t.friendships.destroy(_id=iden)
            success += 1
        except:
            pass
        #print "Unfollowed %i people." % success

def print_tweet(tweet):
    print tweet["user"]["name"]
    print tweet["user"]["screen_name"]
    print tweet["created_at"]
    print tweet["text"]
    hashtags = []
    hs = tweet["entities"]["hashtags"]
    for h in hs:
        hashtags.append(h["text"])
    print hashtags

keywords = open("keywords.txt", "r")
words = [word.strip() for word in keywords.readlines()]
keywords.close()

while 1:
    tweets = t.search.tweets(q=random.choice(words)+' -from:arichduvet', count=199, lang="en")["statuses"] #understand OR operator
    fr = t.friends.ids(screen_name="arichduvet", count=199)["ids"]
    fr.reverse()
    for tweet in tweets:
        try:
            if re.search(offensive, tweet["text"]) == None:
                fav_tweet(tweet)
                retweet(tweet)
                prev_follow = tweet["user"]["following"]
                t.friendships.create(_id=tweet["user"]["id"])
                now_follow = t.users.lookup(user_id=tweet["user"]["id"])[0]["following"]
                if prev_follow==0 and now_follow==1:
                    unfollow(fr.pop())
                if "retweeted_status" in tweet:
                    op = tweet["retweeted_status"]["user"]
                    now_follow = op["following"]
                    t.friendships.create(_id=op["id"])
                    now_follow = t.users.lookup(user_id=op["id"])[0]["following"]
                    if prev_follow==0 and now_follow==1:
                        unfollow(fr.pop())
        except:
            pass
    #search_and_fav("python programming", 199)
    #t.statuses.update(status="Check check! Heroku testing! #python")
        time.sleep(31)
