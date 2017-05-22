"""
    File containing classes and functions to handle a DNS Response
    @author Doshmajhan
"""
import struct
import base64
import time


class DNSResponse:
    """
        Init function to create the class

        addr - the address to send the packet too.
        txt - boolean value whether it's a txt record or not
        server - the server sending the query
        chk - if the beacon checking in has commands queued up
    """
    def __init__(self, addr, server):
        self.addr = addr
        self.packet = None
        self.server = server


    def create_packet(self, url, qID):
        """
            Packs data into a binary struct to send as a
            response to the original query.

            url - the address of the answer
            qID - the queryID of the origina query
        """
        self.packet = struct.pack("!H", qID) # Q ID
        self.packet += struct.pack("!H", 34176) # Flags
        self.packet += struct.pack("!H", 1) # Questions
        self.packet += struct.pack("!H", 1) # Answers
        self.packet += struct.pack("!H", 0) # Authorities
        self.packet += struct.pack("!H", 0) # Additional
        tmp_url = url.split(".")
        for x in tmp_url:
            self.packet += struct.pack("B", len(x)) # Store length of name
            self.packet += ''.join(struct.pack("c", byte) for byte in bytes(x)) # Loop & store name
        self.packet += struct.pack("B", 0) # Terminate name
        self.packet += struct.pack("!H", 1) # Q A Type
        self.packet += struct.pack("!H", 1) # Q Class
        self.create_answer(url)


    def create_answer(self, record):
        """
            Creates the answer section of the DNS response

            record - the record to include in the name section
        """
        tmp_record = record.split(".")
        for x in tmp_record:
            self.packet += struct.pack("B", len(x)) # Store length of name
            self.packet += ''.join(struct.pack("c", byte) for byte in bytes(x)) # Loop & store name
        self.packet += struct.pack("B", 0) # Terminate name
        self.packet += struct.pack("!H", 1) # A Type 2 bytes
        self.packet += struct.pack("!H", 1) # Class 2 bytes
        self.packet += struct.pack("!I", 1) # TTL 4 bytes
        self.packet += struct.pack("!H", 4) # RDLENGTH 2 bytes
        #self.packet += struct.pack("!I", 2165670612)  # RDATA, should be IP address from A record
        self.packet += struct.pack("!I", 1082779956)


def send_response(addr, server, dnsQuery):
    """
        Function to answer a DNS query with the correct record.

        addr - the address to send the response to
        server - the class representing the mini dns server
        dnsQuery - the class represnting the query being answered
        txt - boolean value for if its a txt record or not
    """
    response = DNSResponse(addr, server)
    response.create_packet(dnsQuery.full_names[0], dnsQuery.query_id)
    server.sock.sendto(bytes(response.packet), addr)
    print "Response sent"

