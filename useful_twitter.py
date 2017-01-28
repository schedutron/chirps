from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import webbrowser, time

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

def unfollow(ids):
    success = 0
    for iden in ids:
        try:
            t.friendships.destroy(_id=iden)
            success += 1
        except:
            pass
    print "Unfollowed %i people." % success

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

while 1:
    tweets = t.search.tweets(q="#python", count=199)["statuses"]
    for tweet in tweets:
        retweet(tweet)
    #search_and_fav("python programming", 199)
    #t.statuses.update(status="Check check! Heroku testing! #python")
        time.sleep(5)
