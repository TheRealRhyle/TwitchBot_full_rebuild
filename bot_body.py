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
            s.send("PONG %s\r\n" % line[1])
            line[0] = "twitchPing"
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
                usernamesplit = parts[1].split("!")
                username = usernamesplit[0]

                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if init_mesage == '':
                    init_message = nick + ' has been initialized.  Awaiting commands.'
                    # print(init_mesage)
                    Send_message(init_mesage)

                if MODT:
                    print(username + ": " + message)

                    # testing for the Ping:Pong crash
                    # if username == '':
                    #     print(message)
                    #     print('Ping:Pong')

                    #
                    # The bulk of the processing goes down here!
                    #
                    if message == '':
                        continue

                    if username != '' and message[0] == '!':
                        if username == 'darkxilde':
                            if message[0:7] == '!create':
                                # Parse the command to be added/created
                                command, target, action = message.split(', ')
                                ex_com, command = command.split(' ')
                                command = '!' + command
                                action = ' ' + action
                                c.execute("insert into commands values (:command, :target, :action)",
                                          {'command': command, 'target': target, 'action': action})
                                conn.commit()
                                Send_message("Command " + command + " has been added.")

                            elif message[0:7] == '!update':
                                # Parse the command to be added/created
                                command, target, action = message.split(', ')
                                ex_com, command = command.split(' ')
                                command = '!' + command
                                action = ' ' + action
                                c.execute("update commands set action = :action where ex_command = :command",
                                          {'command': command, 'target': target, 'action': action})
                                conn.commit()
                                Send_message("Command " + command + " has been updated.")

                            elif message[0:7] == '!remove':
                                # Parse the command to be removed
                                ex_com, command = message.split(' ')
                                command = '!' + command
                                c.execute("delete from commands where ex_command = ?",(command,))
                                conn.commit()
                                Send_message("Command " + command + " has been removed.")

                        if message[0] == '!' and message[0:4] not in ('!remo', '!crea', '!upda', '!gunt'):
                            try:
                                chatmessage = message
                                chatmessage = c.execute("select action from commands where ex_command = ?", (chatmessage,))
                                chatmessage = chatmessage.fetchone()[0]
                                Send_message('Hello ' + username + " " + chatmessage)
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
                        else:
                            print("Hit else:")
                            print(username)
                            print(message[0:7])
                            print(list(c.execute("select * from commands")))

                    #
                    # End of bot processing
                    #


                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True