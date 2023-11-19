import socket
import struct
import time

def build_dns_request(domain):
    # Construct a DNS request payload
    transaction_id = 1234  # You can use any random number as the transaction ID
    flags = 0x0100  # Standard query, recursion desired
    questions = 0x0001  # Number of questions

    # Create the DNS query packet
    dns_query = struct.pack('!HHHHHH', transaction_id, flags, questions, 0, 0, 0)

    # Encode the domain name
    for part in domain.split('.'):
        dns_query += struct.pack('B', len(part))
        dns_query += struct.pack('!{}s'.format(len(part)), part.encode('utf-8'))

    # End of the domain name
    dns_query += struct.pack('B', 0)

    # Type A (IPv4 address)
    dns_query += struct.pack('!HH', 0x0001, 0x0001)

    return dns_query

def send_dns_request(dns_request, resolver_ip, resolver_port=53):
    # Send DNS request to resolver using UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(10)

        try:
            s.sendto(dns_request, (resolver_ip, resolver_port))
            response, _ = s.recvfrom(1024)
            return response
        except s.timeout:
            return None
        
def extract_ip_from_dns_response(response):
    # Extract IP address from DNS response
    ip_bytes = response[-4:]
    ip_address = '.'.join(str(byte) for byte in ip_bytes)
    return ip_address

def measure_rtt(start_time):
    # Measure Round-Trip Time (RTT)
    return time.time() - start_time

def make_http_request(ip_address, domain):
    # Construct and send an HTTP GET request
    http_request = f"GET / HTTP/1.1\r\nHost: {domain}\r\n\r\n"
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip_address, 80))
        s.sendall(http_request.encode('utf-8'))
        response = b''

        while True:
            buffer = s.recv(1024)
            response += buffer

            if len(buffer) < 1024:
                break

        return response

def save_html_content(html_content, filename="output.html"):
    # Save HTML content to a file
    with open(filename, "w", encoding="utf-8") as file:
        file.write(html_content.decode('utf-8'))


if __name__ == "__main__":
    domain = "tmz.com"
    resolvers = [
        '198.41.0.4', '199.9.14.201', '192.33.4.12', '199.7.91.13', '192.203.230.10', '192.5.5.241',
        '192.112.36.4', '198.97.190.53', '192.36.148.17', '192.58.128.30', '193.0.14.129',
        '199.7.83.42', '202.12.27.33'
    ]
    root_dns_resolver = ""

    # Step 1: Build DNS request
    dns_request = build_dns_request(domain)

    # Step 2: Send DNS request to root DNS resolver
    start_time = time.time()
    dns_response = None

    for root_resolver in resolvers:
        dns_response = send_dns_request(dns_request, root_resolver)
        
        if dns_response is not None:
            root_dns_resolver = root_resolver
            break

    rtt_resolver = measure_rtt(start_time)
    root_dns_ip = extract_ip_from_dns_response(dns_response)
    print(f"Root DNS Resolver IP: {root_dns_resolver}")
    print(f"RTT to Root DNS Resolver: {rtt_resolver} seconds")

    # Step 3: Extract TLD DNS resolver IP from DNS response
    tld_resolver_ip = extract_ip_from_dns_response(dns_response)
    print(f"TLD DNS Resolver IP: {tld_resolver_ip}")

    # Step 4: Send DNS request to TLD DNS resolver
    dns_request = build_dns_request(domain)
    start_time = time.time()
    dns_response = send_dns_request(dns_request, tld_resolver_ip)
    rtt_tld_resolver = measure_rtt(start_time)
    print(f"RTT to TLD DNS Resolver: {rtt_tld_resolver} seconds")

    # Step 5: Extract authoritative DNS server IP from DNS response
    authoritative_dns_ip = extract_ip_from_dns_response(dns_response)
    print(f"Authoritative DNS Server IP: {authoritative_dns_ip}")

    # Step 6: Send DNS request to authoritative DNS server
    dns_request = build_dns_request(domain)
    start_time_dns = time.time()
    dns_response = send_dns_request(dns_request, authoritative_dns_ip)
    rtt_authoritative_dns = measure_rtt(start_time_dns)
    print(f"RTT to Authoritative DNS Server: {rtt_authoritative_dns} seconds")

    # Step 7: Extract IP address from DNS response
    tmz_ip = extract_ip_from_dns_response(dns_response[37:41])
    print(f"Resolved IP for {domain}: {tmz_ip}")

    # Step 8: Make HTTP request to tmz.com server
    start_time_http = time.time()
    http_response = make_http_request(tmz_ip, domain)
    rtt_http = measure_rtt(start_time_http)
    print(f"RTT for HTTP Request: {rtt_http} seconds")

    # Print HTTP Response
    """ print("HTTP Response:")
    print(http_response.decode('utf-8')) """

    # Step 9: Save HTML content to a file
    save_html_content(http_response, "tmz_page.html")
    print("HTML content saved to tmz_page.html")
