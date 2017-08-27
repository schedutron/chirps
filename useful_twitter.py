"""
Script defining my Twitter bot, using sixohsix's Python wrapper for the
Twitter API.
"""
# Instead of searching tweets and then doing actions on them, why not try
# streaming interesting tweets in realtime and then performing actions on them?


from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream
import webbrowser, time, random, re, urllib, requests, HTMLParser, os
parser = HTMLParser.HTMLParser() #used in find_news

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

oauth = OAuth(os.environ['ACCESS_TOKEN'], os.environ['ACCESS_SECRET'], os.environ['CONSUMER_KEY'], os.environ['CONSUMER_SECRET'])

t = Twitter(auth=oauth)
ts = TwitterStream(auth=oauth)
tu = TwitterStream(auth=oauth, domain="userstream.twitter.com")

if __name__ == "__main__":
    webbrowser.open("http://twitter.com")

#useful Python functions

def print_followers(username):
    try:
        followers = t.followers.ids(screen_name=username)
        c = followers["next_cursor"]
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

def find_news():
    nyTech = requests.get('https://nytimes.com/section/technology')
    latest_patt = r'(?s)<ol class="story-menu theme-stream initial-set">(.*)</ol>'
    latest = re.search(latest_patt, nyTech.text)
    news = re.findall(r'(?s)<h2.*?>(.*?)</h2>', latest.group(1))
    news = [item.strip() for item in list(set(news))]
    for i in range(len(news)):
        item = news[i]
        if item.startswith('Daily Report: '):
            news[i] = item[14:]
    tv = requests.get('https://theverge.com', headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'})
    feed_patt = r'(?s)<div class="c-compact-river">(.*?)<div class="l-col__sidebar"'
    bunches = re.findall(feed_patt, tv.text)
    verge_news = []
    for cluster in bunches:
        snippets = re.findall(r'<h2.*?><a.*>(.*?)</a></h2>', cluster)
        verge_news.extend(snippets)
    for item in verge_news:
        news.append(parser.unescape(item))
    random.shuffle(news) #to bring a feel of randomness
    return news
#confused stuff happened during the initialization at Heroku on Saturday, 4 Feb, 2017: around 2 pm.
#see the confused_stuff snap.
#By the way, confused stuff happens in the middle as well.

news = []
while 1:
    keywords = urllib.urlopen("https://dl.dropboxusercontent.com/s/zq02iogqhx5x9j2/keywords.txt?dl=0")
    words = [word.strip() for word in keywords.readlines()]
    keywords.close()
    word = random.choice(words)
    tweets = t.search.tweets(q=word+' -from:arichduvet', count=199, lang="en")["statuses"] #understand OR operator
    fr = t.friends.ids(screen_name="arichduvet")["ids"]
    if len(fr) > 4990: #To unfollow old follows because Twitter doesn't allow a large following / followers ratio for people with less followers.
                       #Using 4990 instead of 5000 for 'safety', so that I'm able to follow some interesting people
                       #manually even after a bot crash.
        for i in xrange(2500): #probably this is the upper limit of mass unfollow in one go
            unfollow(fr.pop())

    for tweet in tweets:
        try:
            if re.search(offensive, tweet["text"]) == None:
                print "Search tag:", word
                print_tweet(tweet)
                print
                print "Heart =", fav_tweet(tweet)
                print "Retweet =", retweet(tweet)
                #prev_follow = tweet["user"]["following"]
                t.friendships.create(_id=tweet["user"]["id"])
                #now_follow = t.users.lookup(user_id=tweet["user"]["id"])[0]["following"]
                #if prev_follow==0 and now_follow==1:
                #    time.sleep(11)
                #    unfollow(fr.pop())
                if "retweeted_status" in tweet:
                    op = tweet["retweeted_status"]["user"]
                    #prev_follow_o = op["following"]
                    #time.sleep(11)
                    t.friendships.create(_id=op["id"])
                    #now_follow_o = t.users.lookup(user_id=op["id"])[0]["following"]
                    #if prev_follow_o==0 and now_follow_o==1:
                    #    time.sleep(11)
                    #    unfollow(fr.pop())
                print

                if not news:
                    news = find_news()
                item = news.pop()
                if not re.search(r'(?i)this|follow|search articles', item):
                    print "Scraped: ", item
                    t.statuses.update(status=item)
        except:
            pass

    #search_and_fav("python programming", 199)
    #t.statuses.update(status="Check check! Heroku testing! #python")
        time.sleep(61)
