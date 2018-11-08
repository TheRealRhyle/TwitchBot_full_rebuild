import socket
import loader


# Method for sending a message
def Send_message(message):
    s.send(("PRIVMSG #" + chan + " :" + message + "\r\n").encode('UTF-8'))
    print(nick + ": " + message)

# get connection a pointer for sqlite db
conn, c = loader.loading_seq()

# get connection info from db
streamr = c.execute('select * from streamer').fetchall()
streamr = list(streamr[0])
host, nick, port, oauth, readbuffer = streamr

# Set the channel to join for testing purposes:
chan = 'krushnek'

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((host, port))
s.send(bytes('PASS %s\r\n' %oauth, 'UTF-8'))
s.send(bytes('NICK %s\r\n' %nick, 'UTF-8'))
s.send(("JOIN #" + chan + "\r\n").encode('UTF-8'))

Running = True
readbuffer = ''
MODT = False

while Running == True:
    readbuffer = readbuffer + s.recv(1024).decode()
    temp = str(readbuffer).split("\n")
    readbuffer = temp.pop()
    for line in temp:
        action=''
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if (line[0] == "PING"):
            s.send("PONG %s\r\n" % line[1])
        else:
            parts = line.split(":")
            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                try:
                    # Sets the message variable to the actual message sent
                    message = parts[2][:len(parts[2]) - 1]
                except:
                    message = ""
                # Sets the username variable to the actual username
                usernamesplit = parts[1].split("!")
                username = usernamesplit[0]

                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if MODT:
                    print(username + ": " + message)

                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True


# streamr = c.execute('select * from streamer').fetchall()
# streamr = list(streamr[0])
# print(streamr[1])
