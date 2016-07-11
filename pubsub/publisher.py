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

log = logging.getLogger('noc-netmode')

class AsyncSockListener(asyncore.dispatcher):

	def __init__(self, sock, master):
		self.map = {}
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM)
		self.connect(sock)
		self.master = master
		asyncore.loop()

	def readable(self):
		return True

	def writeable(self):
		return False

	def handle_close(self):
		self.close()

	def handle_read(self):
		try:
			data = self.recv(4096)
			self.master.handle_event(data)
		except socket.error:
			raise

class Publisher:

	VERSION = 1
	ID 		= 'suricata publisher'

	def __init__(self, debug=False, user=None, redis=None, sock=None, channel='suricata', logstash=False):

		if not user:
			print('A user under which the process is run must be specified')
			sys.exit(1)
		if not redis:
			print('A redis URL instance must be specified')
			sys.exit(1)
		if not sock:
			print('A socket must be specified')
			sys.exit(1)

		self.debug 		= debug
		self.user		= user
		self.redis 		= redis
		self.sock 		= sock
		self.channel 	= channel
		self.logstash 	= logstash

		self.events = []

		if debug:
			log.info('Created a new suricata publisher instance')
			log.info('DETAILS')
			log.info('user = {0} ,socket = {1} ,redis channel = {2}'.format(self.user, self.sock, self.channel))

		pwnam = pwd.getpwnam(self.user)
		self.uid = pwnam.pw_uid
		self.gid = pwnam.pw_gid

		if self.uid and self.gid:
			os.setgid(self.gid)
			os.setuid(self.uid)
		else:
			log.error("Cannot run proccess as user {0}".format(self.user))
			sys.exit(1)

		self.redis_client = rds.from_url(self.redis)

	def start(self):
		if self.debug:
			log.info("Initiating socket connection")
		AsyncSockListener(self.sock, self)

	def handle_event(self, data):
		data = data.decode('UTF-8')
		try:
			data_json = json.loads(data)
		except Exception as e:
			return
		if self.debug:
			log.warning('New Data from socket:')
			log.info("{0}:{1} , signature id = {1}".format(
				data_json["src_ip"],
				data_json["src_port"],
				data_json["alert"]["signature_id"]
			))
		
		message = {
			"version" 	: self.VERSION,
			"date"		: datetime.datetime.now().isoformat(),
			"id"		: self.ID,
			"host"		: socket.gethostname(),
			"event"		: data_json
		}
		self.events.append(message)
		self.redis_client.publish(self.channel, json.dumps(message))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Instanciate the publisher of the system')
	parser.add_argument('-d', '--debug', help='Enable debugging')
	parser.add_argument('-r', '--redis', help='Redis URL, example: redis://:password@hostname:port/db_number', required=True)
	parser.add_argument('-s', '--sock', help='The unix socket in which suricata publishes messages', default='/var/run/suricata.sock')
	parser.add_argument('-u', '--user', help='Run as a specific user', default='nobody')
	parser.add_argument('-c', '--channel', help='The pub/sub channel of redis', default='suricata')
	parser.add_argument('--logstash', help='Use this to produce messages for logstash as well')
	args = vars(parser.parse_args())
	p = Publisher(**args)
	p.start()

