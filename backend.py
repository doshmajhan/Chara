"""
    Backend http server to recieve info sent from our agents

    3/22/2017
    @author Doshmajhan
"""

import os
import flask
import threading
import loggerd
from flask import Flask
from werkzeug.utils import secure_filename
from dns import dns_server

LOG_DIR = '/home/ubuntu/Chara/logs/'
LOGGER = loggerd.Loggerd()
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    """
        Index page for testing
    """
    return 'hey there, having fun?'


@app.route('/upload', methods=['POST'])
def recieve_file():
    """
        Function to recieve file uploads from our agents

    """
    addr = flask.request.remote_addr
    if 'file' not in flask.request.files:
        info = "No file in request"
        print info
        LOGGER.info(info, addr)
        return "No file"

    upload_file = flask.request.files['file']
    if upload_file.filename == '':
        temp_name = "tmpfile.1"
        info = "No file name, giving temp name: {}".format(temp_name)
        print info
        LOGGER.error(info, addr)
        return "No file name"

    if upload_file:
        team = addr.split('.')[2]
        fname = secure_filename(upload_file.filename)
        filedir = os.path.join(LOG_DIR, "team{}/{}".format(team, addr))
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        upload_file.save(os.path.join(filedir, fname))
        info = 'File {} uploaded successfully'.format(fname)
        print info
        LOGGER.info(info, addr)

    return "OK"

if __name__ == '__main__':
    dns_serv = dns_server.Server(53, LOGGER)
    dns_thread = threading.Thread(target=dns_serv.start)
    dns_thread.daemon = True
    dns_thread.start()
    app.run(host='0.0.0.0', port=80)

