#!/app/venv/bin/python3

from flup.server.fcgi import WSGIServer
from app import *

if __name__ == '__main__':
    WSGIServer(app).run()
