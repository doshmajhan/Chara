"""
    File containing classes and functions to handle a DNS Query
    @author Doshmajhan
"""
import os
import sys
import struct
import base64
import answer

class DNSQuery:
    """
        Class to represent a DNS query
        along with functions to decode it.
    """
    def __init__(self):
        self.query_id = None
        self.query_count = None
        self.ans_count = None
        self.auth_count = None
        self.add_count = None
        self.names = []
        self.full_names = []
        self.entries = []
        self.query_count = None
        self.query_type = None
        self.is_file = False
        self.file_name = None

    def decode_header(self, query):
        """
            Decode the header of a DNS packet. First unpacks
            the data in certain sections at a time, then performs
            bitwise operations to get each field.

            :param query: the binary data received from the listening socket
        """
        #Read the data from the header, 12 bytes in total
        self.query_id, flags, self.query_count, self.ans_count, \
        self.auth_count, self.add_count = struct.unpack('!HHHHHH', query[:12])
        qr = flags >> 15
        opcode = (flags >> 11) & 0xf
        aa = (flags >> 10) & 0x1
        tc = (flags >> 9) & 0x1
        rd = (flags >> 8) & 0x1
        ra = (flags >> 7) & 0x1
        z = (flags >> 6) & 0x1
        ad = (flags >> 5) & 0x1
        cd = (flags >> 4) & 0x1
        rcode = flags & 0xf

        if z:
            self.is_file = True

        # print out flags, move in function later

        print "[QR {}] [OPC {}] [AA {}] [TC {}] [RD {}] [RA {}] " \
               "[Z {}] [AD {}] [CD {}] [RCODE {}]".format(
               qr, opcode, aa, tc, rd, ra, z, ad, cd, rcode)

        print "[# Questions: {}] [# Ans RR: {}] [# Auth RR: {}] [# Add RR: {}]".format(
                self.query_count, self.ans_count, self.auth_count, self.add_count)


    def decode_name(self, query, offset):
        """
            Decode the domain name sent in the query, unpack
            the first bit that tells the length of the name.
            Then continue to read each char until the terminating zero.

            :param query: the binary data received from the listening socket
            :param offset: the number of bits to offset by when unpacking the query

            :returns: the new offset
        """
        tmp = []    # tmp list to join names
        while True:
            #Get the length of the qName
            length, = struct.unpack_from("!B", query, offset)
            offset += 1
            if length == 0:
                break
            #Read the name from the data and store
            self.names += [struct.unpack_from("!%ds" % length, query, offset)]
            offset += length

        for char in self.names:
            tmp += [char[0]]
        self.full_names += ['.'.join(tmp)] # create the FQDN

        return offset


    def decode_question(self, query, offset):
        """
            Decode the question section of the DNS Query.
            Loop for the number represented by qCount, and unpack
            the data, calling decode_name each time. Creates a new entry
            consisting of the name, type and class.

            :param query: the binary data received from the listening socket
            :param offset: the number of bits to offset by when unpacking the query
        """
        query_format = struct.Struct("!HH")
        self.decode_header(query)
        count = 0
        #Read and decode each question
        for _ in range(self.query_count):
            offset = self.decode_name(query, offset)
            self.query_type, query_class = query_format.unpack_from(query, offset)
            offset += 4
            self.entries += [{"query_name": self.full_names[count],
                              "query_type": self.query_type,
                              "query_class": query_class}]
            count += 1


def handle_query(query, addr, server):
    """
        Function to handle a DNS query, creating a class
        for it and calling the necessary functions.

        :param query: the binary data receieved from the listening socket
        :param addr: the address the data was received from
        :param server: class representing the mini dns server
    """
    dns_query = DNSQuery()
    dns_query.decode_question(query, 12)
    entry = dns_query.entries[0]
    team = addr[0].split('.')[2]
    # names is a list of the domains queried for
    # each entry is a list of the different parts of the domain, subdomain, tld, etc.
    # format will be <base64 data>.file.doshmajhan.com
    if dns_query.names[1][0] == 'file':
        filename = base64.b64decode(dns_query.names[0][0])
        filedir = os.path.join(sys.path[0], "logs/team{}/{}".format(team, addr[0]))
        if not os.path.exists(filedir):
            os.makedirs(filedir)

        filename = os.path.join(filedir, "{}".format(filename))
        server.file_name = filename
        message = "Got file: {}".format(filename)
        server.loggerd.info(message, addr[0])

    elif dns_query.names[0][0] == 'end':
        tmpname = server.file_name
        server.file_name = ""
        message = "Finished writing file: {}".format(tmpname)
        server.loggerd.info(message, addr[0])

    # need to find way to maintain persistance through querys because the
    # data can be fragmented
    elif dns_query.is_file:
        # do file stuff here
        data = dns_query.names[0][0]
        unpacked_data = ""
        with open(server.file_name, 'ab') as file_name:
            for x in range(len(data)):
                unpacked_data += struct.unpack_from("c", data, x)[0]
            file_name.write(unpacked_data)

    print ""
    print "Recieved query from %s" % (str(addr[0]))
    message = "[Q Name : %s] [Q Type : %s] [Q Class : %s]" % \
                (entry["query_name"], entry["query_type"], entry["query_class"])
    print message
    #server.loggerd.info(message, addr)
    answer.send_response(addr, server, dns_query)
