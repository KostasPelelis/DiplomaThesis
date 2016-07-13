import argparse
from pwd import getpwnam, getpwuid
import os
import sys
import threading
import json
import time
import redis
import collections
import logging
import signal
from logger import Style
log = logging.getLogger('noc-netmode')

blockedIPs = collections.OrderedDict()

def signal_handler(signal, frame):
    sys.exit(0)

class TimerThread(threading.Thread):

    def __init__(self, debug, tick, dest):
        threading.Thread.__init__(self)
        self.debug = debug
        self.tick  = tick
        self.dest  = dest

    def run(self):
        while True:
            # The list conversion is needed because we are deleting a key-value pair
            # during iterating the dictionary
            for (key,val) in list(blockedIPs.items()):
                blockedIPs[key] -= self.tick
                if (blockedIPs[key] <= 0):
                    announcement = "withdraw route {0}/32 next-hop {1}".format(key,self.dest)
                    log.warning(announcement)
                    printflush(announcement)
                    blockedIPs.pop(key, None)
            if self.debug:
                if blockedIPs:
                    log.info("|--------------TIMEOUT TABLE---------------|")
                    log.info("|{0}{2}{1}| {0}{3}{1}|".format(
                        Style.BOLD,
                        Style.ESCAPE,
                        "IP".ljust(20),
                        "Duration".ljust(20) 
                    ))
                    log.info("|------------------------------------------|")
                    for k,v in blockedIPs.items():
                        log.info("|{0}| {1}|".format(k.ljust(20),str(v).ljust(20)))
                    log.info("|------------------------------------------|")

            time.sleep(self.tick)

class SubThread(threading.Thread):
    
    def __init__(self, r, args):
        threading.Thread.__init__(self)
        self.redis  = r 
        self.pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        self.args   = args
        self.pubsub.subscribe(args['channel'])

    def run(self):

        # This is practically an infinite loop
        for data in  self.pubsub.listen():
            message = data['data'].decode('UTF-8')
            try:
                jsondata = json.loads(message)
            except Exception as e:
                printflush (e)
                continue
            event = jsondata['event']
            log.info(Style.BOLD + "--------------------- New message received ---------------------" + Style.ESCAPE)
            for (key,value) in sorted(event.items()):
                log.info("{0}: {1}".format(key.ljust(20),value))
            log.info(Style.BOLD + "--------------------- End of message ---------------------" + Style.ESCAPE)

            # Checking exclusions. If none matches then we proceed with the announcement 
            if event['alert']['severity'] > self.args['severity_thres']:
                log.info("Event excluded due to severity")    
            elif event['alert']['signature_id'] in self.args['exclude_sig']:
                log.info("Event excluded due to signature")
            elif event['src_ip'] in self.args['exclude_source']:
                log.info("Event excluded due to source IP")
            elif event['dest_ip'] in self.args['exclude_destination']:
                log.info("Event excluded due to destination IP")
            elif event['dest_port'] in self.args['exclude_dest_port']:
                log.info("Event excluded due to destination port number")
            elif event['src_port'] in self.args['exclude_src_port']:
                log.info("Event excluded due to src port number")
            else:
                log.info(Style.BOLD + "--------------------- New IP Announcement ---------------------" + Style.ESCAPE)
                log.info("|{0} |{1}|".format("Source".ljust(20), (str(event['src_ip']) + ':' + str(event['src_port'])).ljust(100)))
                log.info("|{0} |{1}|".format("Destination".ljust(20), (str(event['dest_ip']) + ':' + str(event['dest_port'])).ljust(100)))
                log.info("|{0} |{1}|".format("Category".ljust(20), str(event['alert']['category']).ljust(100)))
                log.info("|{0} |{1}|".format("Signature ID".ljust(20), str(event['alert']['signature_id']).ljust(100)))
                log.info("|{0} |{1}|".format("Announcement".ljust(20), str(event['alert']['signature']).ljust(100)))
                log.info(Style.BOLD + "--------------------- Annoncement is logged, sending to exabgp ---------------------" + Style.ESCAPE)
                announcement = "announce route {}/32 next-hop {}".format(event['src_ip'], self.args['dest'])
                if event['src_ip'] not in blockedIPs:
                    log.warning(announcement)
                    printflush (announcement)
                blockedIPs[event['src_ip']] = self.args['duration']

def printflush(*args, file=sys.stdout):
    print (*args, flush=True, file=file)

def setupenvironment(args):    
    signal.signal(signal.SIGINT, signal_handler)    
    if args['user'] is not None:
        try:
            uid, gid = getpwnam(args['user'])[2:4]
            printflush (uid, gid)
        except Exception as e:
            printflush (e)
            sys.exit(1)

        curruser = os.getuid()
        if curruser == 0:
            os.setgid(gid)
            os.setuid(uid)
        else:
            printflush ("Running as", getpwuid(curruser).pw_name, "and cannot switch to nobody", file=sys.stderr)
            sys.exit(1)
    if args['redis_host'] is None:
        printflush ("Please supply the redis server with the --redis_host option", file=sys.stderr)
        sys.exit(1)

""" Parsing arguments, checking the input values
    and setting up the environment
"""
parser = argparse.ArgumentParser(description='Subscriber parser')
parser.add_argument('--debug', '-d', help='Run in debug mode', default=False, action='store_true')
# TODO: add regex for IPv4
parser.add_argument('--redis_host', '-r', help='Connect to redis server and subscribe to an event channel')
parser.add_argument('--redis_port', '-p', help='Redis server port.The default value is 6379',type=int, default=6379)
parser.add_argument('--user', '-u', help='Drop privileges to supplied userid.The default user privileges is nobody\'s')
parser.add_argument('--duration', help='Duration of the BGP announcement. After that the announcement is withdrawn',type=int, default=60)
parser.add_argument('--tick', '-t', help='How often we will update the TTLs of BGP announcements',type=int, default=10)
parser.add_argument('--dest', help='Announce the next hop to be the supplied value.Default value \'self\'', default='self')
parser.add_argument('--severity-thres', help='Alerts with severity higher than the given threshold will be ignored.Defaults to 1.',type=int, default=1)
parser.add_argument('--exclude-sig', help='Exclude alerts with the given signature_id from processing.This can be used multiple times',type=int, nargs='*',default=[])
parser.add_argument('--exclude-source', help='Exclude alerts with given source IP CIDR.This can also be used multiple times', nargs='*', default=[])
parser.add_argument('--exclude-destination', help='Exclude alerts with given destination IP CIDR.This can also be used multiple times', nargs='*', default=[])
parser.add_argument('--exclude-dest-port', help='Exclude alerts with given destination port number.This can be used multiple times',type=int, nargs='*', default=[])
parser.add_argument('--exclude-src-port', help='Exclude alerts with given source port number.This can be used multiple times',type=int, nargs='*', default=[])
parser.add_argument('--channel', '-c', help='Name of channel to subscribe, defaults to \'suricata\' ', default='suricata')
args = vars(parser.parse_args())
setupenvironment(args)

# Initializing Redis and the appropriate threads
r = redis.StrictRedis(host=args['redis_host'], port=args['redis_port'], db=0)
timerThread = TimerThread(args['debug'], args['tick'], args['dest'])
pubsubThread = SubThread(r, args)
timerThread.daemon = True
timerThread.start()
pubsubThread.daemon = True
pubsubThread.start()

while threading.active_count() > 0:
    time.sleep(0.3)