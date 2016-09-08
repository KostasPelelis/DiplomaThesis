import argparse
import socket
import pwd
import os
import sys
import redis as rds
import asyncore
import json
import datetime
import logging
import signal
from logger import Style
import threading
import signal


def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


log = logging.getLogger('noc-netmode')


class SockListenerThread(threading.Thread):

    def __init__(self, sock, master):
        threading.Thread.__init__(self)
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.connect(sock)
        self.master = master

    def run(self):
        try:
            while True:
                data = self.socket.recv(4096)
                self.master.handle_event(data)
        except socket.error:
            socket.close()
            raise


class Publisher:

    VERSION = 1
    ID = 'suricata publisher'

    def __init__(self, debug=False, user=None, redis=None, sock=None,
                 channel='suricata', logstash=False):

        if not user:
            print('A user under which the process is run must be specified')
            sys.exit(1)
        if not redis:
            print('A redis URL instance must be specified')
            sys.exit(1)
        if not sock:
            print('A socket must be specified')
            sys.exit(1)

        self.debug = debug
        self.user = user
        self.redis = redis
        self.sock = sock
        self.channel = channel
        self.logstash = logstash

        self.events = []

        if debug:
            log.info('Created a new suricata publisher instance -> user = {0} ,socket = {1} ,redis channel = {2}'.format(
                self.user, self.sock, self.channel))

        self.uid, self.gid = pwd.getpwnam(self.user)[2:4]

        if self.uid and self.gid:
            try:
                os.setgid(self.gid)
                os.setuid(self.uid)
            except Exception as e:
                print(e)
                raise
        else:
            log.error("Cannot run proccess as user {0}".format(self.user))
            sys.exit(1)

        self.redis_client = rds.from_url(self.redis)

    def start(self):
        if self.debug:
            log.info("Initiating socket connection")
        self.socket_thread = SockListenerThread(self.sock, self)
        self.socket_thread.daemon = True
        self.socket_thread.start()

    def handle_event(self, data):
        data = data.decode('UTF-8')
        try:
            data_json = json.loads(data)
        except Exception as e:
            return
        if self.debug:
            log.warning(
                '■  {0}New Data from socket{1}'.format(Style.BOLD, Style.ESCAPE))
            log.info("├─ {0}Source{1}: {2}:{3}".format(
                Style.UNDERLINE,
                Style.ESCAPE,
                data_json["src_ip"],
                data_json["src_port"]
            ))
            log.info("├─ {0}Signature ID{1}: {2}".format(
                Style.UNDERLINE,
                Style.ESCAPE,
                data_json["alert"]["signature_id"]
            ))
            log.info("└─ {0}Description{1}: {2}".format(
                Style.UNDERLINE,
                Style.ESCAPE,
                data_json["alert"]["signature"]
            ))

        message = {
            "version"   : self.VERSION,
            "date"      : datetime.datetime.now().isoformat(),
            "id"        : self.ID,
            "host"      : socket.gethostname(),
            "event"     : data_json
        }
        self.events.append({
            "event_type": "subscriber",
            "data": message
        })
        self.redis_client.publish(self.channel, json.dumps(message))
        data_copy = {k: v for k, v in data_json.items()}
        if self.logstash:
            if data_copy["alert"] is not None:
                for k, v in data_copy["alert"].items():
                    data_copy[k] = v
                del(data_copy["alert"])
                self.events.append({
                    "event_type": "logstash",
                    "data": data_copy
                })
            self.redis_client.publish("logstash-{0}".format(self.channel),
                                      json.dumps(data_copy))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Instanciate the publisher of the system')
    parser.add_argument('-d', '--debug', help='Enable debugging')
    parser.add_argument(
        '-r', '--redis', help='Redis URL, example: redis://:password@hostname:port/db_number', required=True)
    parser.add_argument(
        '-s', '--sock', help='The unix socket in which suricata publishes messages', default='/var/run/suricata.sock')
    parser.add_argument(
        '-u', '--user', help='Run as a specific user', default='nobody')
    parser.add_argument(
        '-c', '--channel', help='The pub/sub channel of redis', default='suricata')
    parser.add_argument(
        '--logstash', help='Use this to produce messages for logstash as well')
    args = vars(parser.parse_args())
    p = Publisher(**args)
    p.start()
