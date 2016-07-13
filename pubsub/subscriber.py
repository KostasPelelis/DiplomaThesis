import argparse
from pwd import getpwnam, getpwuid
import os
import sys
import threading
import json
import logger
import time
import redis
import collections

log = logger.init_logging()
blockedIPs = collections.OrderedDict()

class TimerThread(threading.Thread):

    def __init__(self, debug, tick, dest):
        threading.Thread.__init__(self)
        self.debug = debug
        self.tick  = tick
        self.dest  = dest

    def run(self):
        while True:
            # The list conversion is needed because we are deleting a key-value pair during iterating the dictionary
            for (key,val) in list(blockedIPs.items()):
                blockedIPs[key] -= self.tick
                if (blockedIPs[key] <= 0):
                    announcement = "withdraw route {0}/32 next-hop {1}".format(key,self.dest)
                    log.warning(announcement)
                    printflush(announcement)
                    blockedIPs.pop(key, None)
            if self.debug:
                if not blockedIPs:
                    log.info("IP\t\t: Duration")
                for k,v in blockedIPs.items():
                    log.info("{0}\t: {1}".format(k,v))
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
            log.info("New message received -------------------")
            for (key,value) in sorted(event.items()):
                log.info("{0}\t\t: {1}".format(key,value))
            log.info("End of message--------------------------")

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
                log.info("New IP is about to be announced------------------------------")
                log.info("Source\t\t: {}:{}".format(event['src_ip'], event['src_port']))                      
                log.info("Destination\t: {}:{}".format(event['dest_ip'],event['dest_port']))
                log.info("Category\t\t: {}".format(event['alert']['category']))
                log.info("Signature_ID\t: {}".format(event['alert']['signature_id']))                      
                log.info("Signature\t\t: {}".format(event['alert']['signature']))                      
                log.info("Announcement is logged and about to be sent to exabgp--------")
                announcement = "announce route {}/32 next-hop {}".format(event['src_ip'], self.args['dest'])
                if event['src_ip'] not in blockedIPs:
                    log.warning(announcement)
                    printflush (announcement)
                blockedIPs[event['src_ip']] = self.args['duration']

def printflush(*args, file=sys.stdout):
    print (*args, flush=True, file=file)

def setupenvironment(args):    
    
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

if __name__ == '__main__':

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
    timerThread.start()
    pubsubThread.start()
    timerThread.join()
    pubsubThread.join()
