import struct 

ZERO_BYTES =b'\x00\x00'

class DNSMessage:
    def __init__(self, domain):
        self.id = b'\x04\xd2'               # ID = 39158
        self.flags = b'\x00\x00'

        self.question =  b'\x00\x01'        
        self.answers = ZERO_BYTES
        self.authority = ZERO_BYTES
        self.additional = ZERO_BYTES

        # domain + QType + QClass domain.encode()
        self.query =  domain + b'\x00' + b'\x00\x01' + b'\x00\x01'  

    def get_message(self):
        return self.id + self.flags + self.question + self.answers + self.authority + self.additional + self.query
    
    def set_message(self, message):
        self.id, self.flags, self.question, self.answers, self.authority, self.additional = struct.unpack('!HHHHHH', message)

    def getAnswer(self, answer):
        # 12:16 -> represents the 4bytes that maps to the 4 decimals of the IP address
        return answer[12:16]