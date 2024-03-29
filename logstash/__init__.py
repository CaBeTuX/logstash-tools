__author__    = 'Michael Stella <michael@jwplayer.com>'
__copyright__ = "Copyright (c) 2013-2014 Long Tail Ad Solutions"
__version__   = "1.0"

import json
import logging
import os
import redis
import sys

log_output=logging.getLogger('output')

class Sink(object):
    """Output sink base class"""

    def log(self, **kwargs):
        """Overload this to log a message and handle errors"""
        pass


class StdoutSink(Sink):
    """Output to STDOUT in JSON format"""

    def log(self, **kwargs):
        """Log a message"""
        print(json.dumps(kwargs))


class RedisSink(Sink):
    """Output to Redis"""

    def __init__(self, host, key, port=6379):
        self.host = host
        self.port = port
        self.key = key
        self._connect()

    def _connect(self):
        self._conn = redis.StrictRedis(
                        host=self.host,
                        port=self.port,
                        db=0,
                        socket_timeout=30)
        self._conn.ping()


    def log(self, **kwargs):
        """Log a message"""
        try:
            self._conn.rpush(self.key, json.dumps(kwargs))
        except redis.exceptions.ConnectionError as e1:
            try:
                self._connect()
                log_output.info("Redis: reconnected to server {0}:{1}".format(self.host, self.port))
                self._conn.rpush(self.key, json.dumps(kwargs))
            except Exception as e2:
                log_output.error("Redis: {0}".format(e2))


    def ping(self):
        """Ping the server.  Boolean."""
        return self._conn.ping()


def read_config(cfgfile):
    # read config file
    cfg = {}
    inputs = []
    outputs = []

    with open(cfgfile, 'r') as f:
        try:
            cfg = json.loads(f.read())
        except ValueError as e:
            logging.error("Could not read config file: {0}".format(e))
            sys.exit(-1)

    return (cfg['input'], cfg['output'])
