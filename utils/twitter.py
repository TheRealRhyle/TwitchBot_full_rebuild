import logging
import tweepy
import loader

# from tweepy.streaming import StreamListener
# from tweepy import OAuthHandler
# from tweepy import Stream

def getCreds():
    _, c = loader.loaddb()
    return c.execute("select * from twitter").fetchone()

def OAuth():
    (ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET) = getCreds()
    try:
        auth = tweepy.OAuthHandler(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        auth.set_access_token(CONSUMER_KEY, CONSUMER_SECRET)
        return auth
    except Exception as e:
        logging.basicConfig(filename="twitter.log", filemode='w', format='%(name)s - %(level)s - %(message)s')
        logging.warning(e)
        return None

def send_tweet(tweet_txt):
    oauth = OAuth()
    api = tweepy.API(oauth)
    api.update_status(tweet_txt)

def get_retweet():
    oauth = OAuth()
    api = tweepy.API(oauth)
    lastTweet = api.user_timeline(302662769, count=1)[0]
    return(lastTweet.id)

# if __name__=="__main__":
#     (ACCESS_TOKEN, ACCESS_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET) = getCreds()
#     print(f"{ACCESS_TOKEN}, {ACCESS_TOKEN_SECRET}, {CONSUMER_KEY}, {CONSUMER_SECRET}")