/*
 * File containing struct and function definitions for a DNS query
 * @author Doshmajhan
 */

#ifndef QUERY_H
#define QUERY_H

struct DNS_HEADER {
    unsigned short id;              // id of the query
    unsigned char qr        :1;     // query or response
    unsigned char opcode    :4;     // field to specify what kind of query
    unsigned char aa        :1;     // Authoritive answer, only useful in responses
    unsigned char tc        :1;     // if the message was truncated
    unsigned char rd        :1;     // if recursion is desired or not
    unsigned char ra        :1;     // if recursion is available, only in responses
    unsigned char z         :4;     // bit reserved, but we use it for fragmenting
    unsigned char rcode     :4;     // response code
    unsigned short qdcount;         // number of entries in question section
    unsigned short ancount;         // number of resource records in answer section
    unsigned short nscount;         // number of nameserver records in answer section
    unsigned short arcount;         // number of resource records in additional section
};

struct DNS_QUESTION {
    unsigned short qtype;           // type of query being sent
    unsigned short qclass;          // class of the query
};

#endif
