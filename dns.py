import socket
import time

from  utils import DNSMessage


RESOLVERS_IP = [
    '198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13', '192.203.230.10', '192.5.5.241', 
    '192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30', '193.0.14.129', 
    '199.7.83.42', '202.12.27.33'
]

DNS_PORT = 53
HTTP_PORT = 80
IP = '127.0.0.1'
# Byte format of tmz.com
TMZ_DOMAIN = b'\x03\x74\x6d\x7a\x03\x63\x6f\x6d'



def sendToResolver(message, resolver_ip):
    # Starting counter before request
    starting_time = time.time()

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.settimeout(10)

        try:
            udp_socket.sendto(message, (resolver_ip, DNS_PORT))
            response, _ = udp_socket.recvfrom(1024)
        except socket.timeout:
            return None
        
    return response, starting_time


# Sends first request to root dns 
# returns a response with a list of tld ip resolvers
def tldResponse(message):
    for resolver in RESOLVERS_IP:
        response, start_time = sendToResolver(message, resolver)

        if response is not None:
            print("Resolver IP:       ", resolver)
            return response, start_time

    return None

# Converts four bytes into an decimal representation
# of an IP address
def convertIP(ip):
    newIp = ''
    for hexa in ip:
        newIp += str(hexa) + '.'
    
    return newIp[:-1]

def main():
    # Constructing the dns message
    message = DNSMessage(TMZ_DOMAIN)
    
    # Sendind message to root dns resolver to obtain the tld IPs
    tld_response, start_time = tldResponse(message.get_message())
    end_time = time.time() - start_time  
    print("Root RTT:           %.4f" % end_time)
    print()

    # tld_response[-4:] -> get last four bytes of additional records
    # which represent section of IP address for tld resolver
    tld_ip = convertIP(tld_response[-4:])

    # Send query to tld resolver ip
    auth_response, start_time = sendToResolver(message.get_message(), tld_ip)
    end_time = time.time() - start_time    
    print("TLD:               ", tld_ip)
    print("TLD RTT:            %.4f" % end_time)
    print()

    # auth_response[-4:] -> get last four bytes of additional records
    # which represent section of IP address for authoritative resolver
    auth_ip = convertIP(auth_response[-4:])

    # Send query to authoritative resolver ip
    tmz_response, start_time = sendToResolver(message.get_message(), auth_ip)
    end_time = time.time() - start_time    
    print("Authoritative:     ", auth_ip)   
    print("Authoritative RTT:  %.4f" % end_time)
    print()
    
    # After dns packet analysis in wireshare, it seems that the answer 
    # starts at the position 25 of the bytes in tmz_response
    # Starting at position 25, we are omitting the header -> 12bytes
    # and the question we turned out to be from bytes 12 to 24
    tmz_ip = convertIP(message.getAnswer(tmz_response[25:]))
    print("tmz.com IP address")
    print("tmz.com:           ", tmz_ip)
    print()


    # Strating counter for HTTP RTT calculation
    start_time = time.time()

    # Making HTTP request to tmz.com IP address using TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        # connect to the server
        tcp_socket.connect((tmz_ip, HTTP_PORT))
        
        # HTTP request format
        request = ("GET / HTTP/1.1\r\nHost:%s\r\n\r\n" % "tmz.com").encode()

        # Sending the HTTP request
        tcp_socket.sendall(request)

        # receive HTTP response from server
        http_response = b""
        while True:
            buffer = tcp_socket.recv(1024)
            http_response += buffer
            
            if len(buffer) < 1024:
                break
        
        # Printing the Round Trip Time for the HTTP request
        end_time = time.time() - start_time
        print("RTT for HTTP request using TCP:  %.4f" % end_time)
        
        # Extracting html body from response 
        _, _, html_content = http_response.partition(b'\r\n\r\n')

        # Saving HTML file from HTTP response:
        with open('tmz_response.html', 'w') as f:
            f.write(html_content.decode())

    
if __name__ == "__main__":
    main()
