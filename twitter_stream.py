import ConfigParser
import os

import redis
import tweepy

from twitter import Twitter


class MyStreamListener(tweepy.StreamListener):
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.abspath('config.ini'))
        self.r = redis.StrictRedis(host=self.config.get('DB', 'host'), port=self.config.get('DB', 'port'))

    def on_status(self, status):
        pass


if __name__ == '__main__':
    myStreamListener = MyStreamListener()
    twitter = Twitter()

    myStream = tweepy.Stream(auth=tweepy.api(twitter.auth()), listener=myStreamListener())

    myStream.filter(track=['#wifiisdown'])
