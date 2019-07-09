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

oauth = OAuth()
api = tweepy.API(oauth)

# api.update_status('This is a test, this is just a test.  If this was not a test I would say something else.')
mentions = api.mentions_timeline()
mentions[0].__dict__
print (mentions[0].author)