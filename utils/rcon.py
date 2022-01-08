import socket
import struct
from time import sleep

if __name__ == "__main__":
    SERVERDATA_AUTH = 3
    reqid = 1
    s = socket.socket()
    s.connect(("localhost", 27015))
    data = struct.pack('<l', 9) + struct.pack('<l', 3) + bytes('asdf1234\x00\x00','UTF-8')
    godmod = struct.pack('<l', 10) + struct.pack('<l', 2) + bytes('servermsg rcon testing\x00\x00','UTF-8')
    
    s.send(struct.pack('<l', len(data)) + data)
        # s.send(b"1" + bytes("godmod asdf\r\n","UTF-8") + )
    # readbuffer = s.recv(1024)
    print(auth.decode("UTF-8"))
    s.send(struct.pack('<l', len(godmod)) + godmod)
    resp = s.recv(8)
    print(resp.decode("UTF-8"))
    # s.send(("godmod asdf").encode('UTF-8'))
    # readbuffer = s.recv(262144).decode("UTF-8")
    # print(readbuffer)
