import socket
import loader


# Method for sending a message
def Send_message(message):
    s.send(("PRIVMSG #" + chan + " :" + message + "\r\n").encode('UTF-8'))
    # print(nick + ": " + message)

# get connection a pointer for sqlite db
conn, c = loader.loading_seq()

# get connection info from db
streamr = c.execute('select * from streamer').fetchall()
streamr = list(streamr[0])
host, nick, port, oauth, readbuffer = streamr
TLD = ['com', 'org', 'net', 'int', 'edu', 'gov', 'mil', 'arpa', 'top', 'loan', 'xyz', 'club', 'online',
       'vip', 'win', 'shop', 'ltd', 'men', 'site', 'work', 'stream', 'bid', 'wang', 'app', 'review',
       'space', 'ooo', 'website', 'live', 'tech', 'life', 'blog', 'download', 'link', 'today', 'guru',
       'news', 'tokyo', 'london', 'nyc', 'berlin', 'amsterdam', 'hamburg', 'boston', 'paris', 'kiwi',
       'vegas', 'moscow', 'miami', 'istanbul', 'scot', 'melbourne', 'sydney', 'quebec', 'brussels',
       'capetown', 'rio']

# Set the channel to join for testing purposes:
chan = 'darkxilde'

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((host, port))
s.send(bytes('PASS %s\r\n' %oauth, 'UTF-8'))
s.send(bytes('NICK %s\r\n' %nick, 'UTF-8'))
s.send(("JOIN #" + chan + "\r\n").encode('UTF-8'))

Running = True
readbuffer = ''
MODT = False
init_mesage = ''
slow = 'off'

while Running == True:
    readbuffer = readbuffer + s.recv(1024).decode()
    temp = str(readbuffer).split("\n")
    readbuffer = temp.pop()

    #TODO Get user list
    #TODO Async
    #TODO API

    for line in temp:
        action=''
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if (line[0] == "PING"):
            print('recieved ping, sending pong.')
            print("PONG %s\r\n" % line[1])
            s.send("PONG %s\r\n" % line[1])
            print(line[0])
            line[0] = "twitchPing"
            print(line[0])
        else:
            parts = line.split(":")
            # print("Line = " + line)
            # print("Line = " + line[0])
            # print("Parts = " + str(parts))

            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1] and "PING" not in parts[0]:
                try:
                    # Sets the message variable to the actual message sent
                    # message = ': '.join(parts[2:])
                    if 'http' in parts[2]:
                        message = ':'.join(parts[2:])
                    else:
                        message = parts[2][:len(parts[2]) - 1]

                except:
                    message = ""
                # Sets the username variable to the actual username
                init_message = 'init_done'
                usernamesplit = parts[1].split("!")
                username = usernamesplit[0]


                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if MODT:
                    userfetch = c.execute("select * from users where uname = ?", (username.lower(),)).fetchall()
                    try:
                        user_status = userfetch[0][1]
                    except:
                        user_status = 'user'
                    # print(user_status)
                    print(username + " (" + user_status + "): " + message)

                    # testing for the Ping:Pong crash
                    if username == '':
                        print(message)
                        print('Ping:Pong')

                    # if init_message == 'init_done':
                    #     init_message = nick + ' has been initialized.  Awaiting commands.'
                    #     Send_message(init_mesage)

                    #
                    # The bulk of the processing goes down here!
                    #
                    if message == '':
                        continue

                    # TODO Setup some better handling / identification for link handling.
                    # Link detection and timeout
                    if 'http' in message:
                        # print(user_status)
                        if user_status not in ['admin', 'mod', 'sub', 'fots']:
                            Send_message(username + " links are not currently allowed.")
                            Send_message("/timeout " + username + " 1")

                    # Command processing
                    if message[0] == '!':
                        if username != '':
                            if username == 'darkxilde':
                                if message[0:8] == '!adduser':
                                    command, new_user, user_type = message.split(' ')
                                    c.execute("insert into users values (:user , :status)",{'user': new_user.lower(), 'status': user_type})
                                    conn.commit()

                                elif message[0:8] == '!deluser':
                                    command, new_user = message.split(' ')
                                    c.execute("delete from users where uname = ?",(new_user.lower(),))
                                    conn.commit()

                                elif message[0:8] == '!upduser':
                                    command, new_user, user_type = message.split(' ')
                                    c.execute("""update users 
                                            set status = ?
                                            where uname = ?""",(user_type, new_user.lower(),))
                                    conn.commit()

                                elif message[0:7] == '!create':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("insert into commands values (:command, :target, :action)",
                                              {'command': command, 'target': target, 'action': action})
                                    conn.commit()
                                    Send_message("Command " + command + " has been added.")

                                elif message[0:7] == '!update':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("update commands set action = :action where ex_command = :command",
                                              {'command': command, 'target': target, 'action': action.lstip(' ')})
                                    conn.commit()
                                    Send_message("Command " + command + " has been updated.")

                                elif message[0:7] == '!remove':
                                    # Parse the command to be removed
                                    ex_com, command = message.split(' ')
                                    command = '!' + command
                                    c.execute("delete from commands where ex_command = ?",(command,))
                                    conn.commit()
                                    Send_message("Command " + command + " has been removed.")

                                elif message == "!slow":
                                    if slow == "off":
                                        Send_message("Engaging Slow Chat Mode...")
                                        print("Engaging Slow Chat Mode...")
                                        s.send(("PRIVMSG #" + chan + " :.slow\r\n").encode('UTF-8'))
                                        slow = 'on'
                                        continue
                                    if slow == 'on':
                                        Send_message("Disengaging Slow Chat Mode...")
                                        print("Disengaging Slow Chat Mode...")
                                        s.send(("PRIVMSG #" + chan + " :.slowoff\r\n").encode('UTF-8'))
                                        slow = 'off'
                                        continue

                                # TODO: Figure out how to get the bot to mod someone

                                # elif message[0:4] == '!mod':
                                #     _cmd, mod_user = message.split(' ')
                                #     s.send(("PRIVMSG #" + chan + " :/mod " + mod_user + "\r\n").encode('UTF-8'))
                                #     print(mod_user + " should now be modded.")

                            if message[0:5] not in ('!updu', '!delu', '!addu', '!remo', '!crea', '!upda', '!gunt', '!slow'):
                                try:
                                    chatmessage = message
                                    if message == '!lurk':
                                        chatmessage = "It looks like we've lost " + username + " to the twitch void. " \
                                                    "Hopefully they will find their way back soon!"
                                    else:
                                        chatmessage = c.execute("select action from commands where ex_command = ?", (chatmessage,))
                                        chatmessage = chatmessage.fetchone()[0]
                                    Send_message(chatmessage)
                                except:
                                    Send_message('Hello ' + username + " there is not currently a " + message + " command. " +
                                                 "If you would like to have one created, let me know. Subs take precedence for !commands.")

                            # Gunter command
                            elif message[0:7] == '!gunter':
                                commandlist = list(c.execute("select ex_command from commands"))
                                for itr in range(len(commandlist)):
                                    commandlist[itr] = commandlist[itr][0]
                                Send_message("You've found the (not so) hidden command list " + username +". Command list: "
                                             + ', '.join(commandlist))
                            # else:
                            #     print("Hit else:")
                            #     print(username)
                            #     print(message[0:7])
                            #     print(list(c.execute("select * from commands")))




                    #
                    # End of bot processing
                    #


                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True