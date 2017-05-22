"""
    File containing classes and functions to create
    the DNS server and handle queries/repsonses
    @author Doshmajhan
"""
import socket
import threading
import sys
import query

class Server:
    """
        Initializes a new Server object

        port - the port for the server to listen on

    """
    def __init__(self, port, loggerd):
        self.port = port
        self.sock = None
        self.file = False
        self.file_name = None
        self.file_size = 0
        self.loggerd = loggerd

    def start(self):
        """
            Function to start the server with the information
            in the server

        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('', self.port))
        print "DNS Server started"
        while True:
            #Accept query and start a new thread
            dns_q, addr = self.sock.recvfrom(8192)
            query_handler = threading.Thread(target=query.handle_query, args=(dns_q, addr, self))
            query_handler.daemon = True
            try:
                query_handler.start()
            except (KeyboardInterrupt, SystemExit):
                self.sock.close()
                sys.exit()

if __name__ == '__main__':
    server = Server(53, None)
    server.start()
