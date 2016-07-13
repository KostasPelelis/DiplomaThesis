import socket
import os
import json
import unittest
import sys
import _thread
import logging
import time
import random

sys.path.append(os.path.dirname(os.path.abspath(__file__ + '/..')))
from pubsub.publisher import Publisher

os.chdir(os.getcwd() + '/tests')
from logger import init_logging
log = init_logging('noc-netmode')

def wait_and_send(self, sock):
	log.info('Waiting for incoming connection')
	connection, client_address = sock.accept()
	try:
		for _ in range(1,10):
			rand_ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
			logging.info(rand_ip)
			message = {
				'timestamp' : '2016-06-08T22:29:16.250407+0300',
				'dest_port' : 53,
				'flow_id' : '35430576640',
				'vlan' : '',
				'src_ip' : rand_ip,
				'alert' : {
					'signature_id' : 2013357,
					'rev' : 1,
					'gid' : 1,
					'action' : 'allowed',
					'category' : 'Web Application Attack',
					'signature' : 'ET CURRENT_EVENTS Wordpress possible Malicious DNS-Requests - wordpress.com.* ',
					'severity'  :1
				},
				
				'dest_ip' : '',
				'proto' : 'UDP',
				'in_iface' : 'ix0',
				'event_type' : 'alert',
				'src_port' : 45417
			}
			payload = bytes(json.dumps(message), 'UTF-8')
			connection.sendall(payload)
			time.sleep(2)
		connection.close()
	except Exception as e:
		print(e)
		connection.close()

class TestPublisher(unittest.TestCase):

	ADDRESS = './a.sock'

	def test_data(self):
		
		try:
			os.unlink(self.ADDRESS)
		except os.error as e:
			raise
		sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

		self.assertTrue(type(sock) is socket.socket)
		self.assertEqual(sock.family, socket.AddressFamily.AF_UNIX)
		self.assertEqual(sock.type, socket.SocketKind.SOCK_STREAM)
		self.assertTrue(sock.fileno() > 2)
		
		sock.bind(self.ADDRESS)
		
		self.assertEqual(os.path.normpath(sock.getsockname()), os.path.normpath(self.ADDRESS))
		
		sock.listen(1)
		try:
			_thread.start_new_thread(wait_and_send, ("Test-and-Send-Thread", sock))
		except Exception as e:
			print(e)
			raise
		pub = Publisher(
			debug=True, 
			user='plkost', 
			redis='redis://:6379', 
			channel='suricata', 
			logstash=True, 
			sock=sock.getsockname()
		)
		self.assertIsInstance(pub, Publisher)
		pub.start()
		while len(pub.events) < 18:
			pass
		self.assertEqual(len(pub.events), 18)
		self.assertEqual(pub.events[0]["data"]["event"]["alert"]["signature_id"], 2013357)		
		self.assertEqual(pub.events[1]["data"]["signature_id"], 2013357)

if __name__ == "__main__":
	unittest.main()