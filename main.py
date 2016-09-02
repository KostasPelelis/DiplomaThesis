# from logger import init_logging
# init_logging()
# from pubsub import subscriber
from webservice.server import app

if __name__ == "__main__":
	app.run()