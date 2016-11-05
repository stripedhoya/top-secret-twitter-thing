#!/usr/bin/env python 
import ConfigParser
import os
import time
from datetime import datetime

import pytz
import redis
import tweepy


class Twitter:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.abspath('config.ini'))
        self.r = redis.StrictRedis(host=self.config.get('DB', 'host'), port=self.config.get('DB', 'port'))
        self.token = self.auth()

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
        A search function that will search twitter and insert into redis the result
        :param q: string, search criteria
        :param geocode: tuple, latitude, longitude, radius (either mi or km)
        :param epoch_time: int, the epoch time
        :return: boolean
        """
        token = tweepy.API(self.token)
        count = 0
        results = token.search(q, geocode=geocode, count=100, result_type='recent')
        for status in results:
            utc_time = datetime.strptime(str(status._json['created_at']), '%a %b %d %H:%M:%S +0000 %Y').replace(
                tzinfo=pytz.UTC)
            tweet_epoch = (utc_time - datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()
            if tweet_epoch <= epoch_time:
                count += 1

        if count > 4:
            self.insert_redis('%s: WiFi is DOWN' % str(geocode))
            print('Inserted into redis.')

    def backup_search(self, q, geocode, epoch_time):
        """
        A search function that will search twitter and insert into redis the result
        :param q: string, search criteria
        :param geocode: tuple, latitude, longitude, radius (either mi or km)
        :param epoch_time: int, the epoch time
        :return: boolean
        """
        token = tweepy.API(self.token)
        count = 0
        results = token.search(q, geocode=geocode, count=100, result_type='recent')
        for status in results:
            utc_time = datetime.strptime(str(status._json['created_at']), '%a %b %d %H:%M:%S +0000 %Y').replace(
                tzinfo=pytz.UTC)
            tweet_epoch = (utc_time - datetime(1970, 1, 1).replace(tzinfo=pytz.UTC)).total_seconds()
            if tweet_epoch <= epoch_time:
                count += 1

        if count > 4:
            self.insert_redis('%s: WiFi is UP' % str(geocode))
            print('Inserted into redis.')

    def insert_redis(self, value):
        """
        Inserts into a redis database
        :param value: string
        :return:
        """
        self.r.set(time.time(), value)


if __name__ == '__main__':
    twt = Twitter()
    twt.down_search('wifi down', None, time.time())
