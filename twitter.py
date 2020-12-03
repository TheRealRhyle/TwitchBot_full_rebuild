import twittercreds
import tweepy
# from tweepy.streaming import StreamListener
# from tweepy import OAuthHandler
# from tweepy import Stream

def OAuth():
    try:
        auth = tweepy.OAuthHandler(twittercreds.ACCESS_TOKEN, twittercreds.ACCESS_TOKEN_SECRET)
        auth.set_access_token(twittercreds.CONSUMER_KEY, twittercreds.CONSUMER_SECRET)
        return auth
    except Exception as e:
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

    # 1334329700806762501