import ConfigParser
import os
import time
from datetime import datetime

import redis
import tweepy


class Twitter:
    def __init__(self):
        self.token = self.auth()
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.abspath('config.ini'))
        self.r = redis.StrictRedis(host=self.config.get('DB', 'host'), port=self.config.get('DB', 'port'))

    def auth(self):
        """
        Sets up OAuth token for use with Twitter's API
        :return:
        """
        token = tweepy.OAuthHandler(self.config.get('Twitter_Keys', 'consumer_key'),
                                    self.config.get('Twitter_Keys', 'consumer_secret'))
        token.set_access_token(self.config.get('Twitter_Keys', 'access_token'),
                               self.config.get('Twitter_Keys', 'access_secret'))
        return token

    def down_search(self, q, geocode, epoch_time):
        """
        A search function that will search twitter and return a boolean value based upon if
        it meets certain criteria
        :param q: string, search criteria
        :param geocode: tuple, latitude, longitude, radius (either mi or km)
        :param epoch_time: int, the epoch time
        :return: boolean
        """
        token = tweepy.API(self.token)
        time_format = '%a %b %d %H:%M:%S &z %Y'
        count = 0
        results = token.search(q, geocode=geocode, count=100, result_type='recent')
        for status in results['statuses']:
            utc_time = datetime.strptime(status['created_at'], time_format)
            tweet_epoch = (utc_time - datetime(1970, 1, 1)).total_seconds()
            if tweet_epoch <= epoch_time:
                count += 1

        if count > 4:
            self.insert_redis('%s: WiFi is DOWN' % geocode)

    def backup_search(self, q, geocode, epoch_time):
        """
        A search function that will search twitter and return a boolean value based upon if
        it meets certain criteria
        :param q: string, search criteria
        :param geocode: tuple, latitude, longitude, radius (either mi or km)
        :param epoch_time: int, the epoch time
        :return: boolean
        """
        token = tweepy.API(self.token)
        time_format = '%a %b %d %H:%M:%S &z %Y'
        count = 0
        results = token.search(q, geocode=geocode, count=100, result_type='recent')
        for status in results['statuses']:
            utc_time = datetime.strptime(status['created_at'], time_format)
            tweet_epoch = (utc_time - datetime(1970, 1, 1)).total_seconds()
            if tweet_epoch <= epoch_time:
                count += 1

        if count > 4:
            self.insert_redis('%s: WiFi is UP' % geocode)

    def insert_redis(self, value):
        self.r.set(time.time(), value)
