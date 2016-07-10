import argparse
import socket
import pwd
import os
import sys
import redis
import asyncore
import json
import datetime

class AsyncSockListener(asyncore.dispatcher):


	def __init__(self, sock, master):
		self.map = {}
		asyncore.dispatcher.__init__(self, map=self.map)
		self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.bind(sock)
		self.listen(1)
		asyncore.loop(map=self.map)

	def readable(self):
		return True

	def writeable(self):
		return False

	def handle_read(self):
		try:
			data = self.recv()
			master.handle_event(data)
		except socket.error:
			raise

class Publisher(object):


	def __init__(self, *args):
		parser = argparse.ArgumentParser(description='Instanciate the publisher of the system')
		parser.add_argument('-d', '--debug', help='Enable debugging')
		parser.add_argument('-r', '--redis', help='Redis URL, example: redis://:password@hostname:port/db_number', required=True)
		parser.add_argument('-s', '--sock', help='The unix socket in which suricata publishes messages', default='/var/run/suricata.sock')
		parser.add_argument('-u', '--user', help='Run as a specific user', default='nobody')
		parser.add_argument('-c', '--channel', help='The pub/sub channel of redis', default='suricata')
		parser.add_argument('--logstash', help='Use this to produce messages for logstash as well')
		self.args = vars(parser.parse_args(*args));

		pwnam = pwd.getpwnam(self.args['user'])
		self.uid = pwnam.pw_uid
		self.gid = pwnam.pw_gid

		if self.uid and self.gid:
			os.setgid(self.gid)
			os.setuid(self.uid)
		else:
			print("Cannot run proccess as user {0}".format(self.args['user']))
			sys.exit(1)

		self.redis_client = redis.from_url(url=self.args['redis'])
		AsyncSockListener(self.args['sock'], self)

	def handle_event(data):
		data = data.rstrip('\n')
		data_json = json.loads(data)
		print(data_json["src_ip"] + ' ' + data_json["src_ip"]["signature"] + ' ' + data_json["alert"]["signature_id"])
		message = {
			"version" : 1,
			"date": datetime.now().isoformat(),
			"id": "suricata publisher",
			"host": socket.gethostname(),
			"event": data_json
		}
		## LOGSTASH MESSAGE HERE
		self.redis_client.publish(self.channel, json.dumps(message))

if __name__ == "__main__":
	Publisher(sys.argv[1:])

