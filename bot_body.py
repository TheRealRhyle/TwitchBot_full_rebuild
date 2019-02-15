import socket
import loader
import tcChargen


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
TLD = ['.com', '.org', '.net', '.int', '.edu', '.gov', '.mil', '.arpa', '.top', '.loan', '.xyz', '.club', '.online',
       '.vip', '.win', '.shop', '.ltd', '.men', '.site', '.work', '.stream', '.bid', '.wang', '.app', '.review',
       '.space', '.ooo', '.website', '.live', '.tech', '.life', '.blog', '.download', '.link', '.today', '.guru',
       '.news', '.tokyo', '.london', '.nyc', '.berlin', '.amsterdam', '.hamburg', '.boston', '.paris', '.kiwi',
       '.vegas', '.moscow', '.miami', '.istanbul', '.scot', '.melbourne', '.sydney', '.quebec', '.brussels',
       '.capetown', '.rio', '.tv']

# Set the channel to join for testing purposes:
chan = "rhyle_"

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((host, port))
s.send(bytes('PASS %s\r\n' % oauth, 'UTF-8'))
s.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))
s.send(bytes("JOIN #" + chan + "\r\n", 'UTF-8'))
# s.send(bytes("CAP REQ :twitch.tv/tags\r\n", 'UTF-8'))
# s.send(bytes("ROOMSTATE #darkxilde\r\n", 'UTF-8'))

Running = True
readbuffer = ''
MODT = False
init_mesage = ''
slow = 'off'
Send_message("I'm awake, quit poking me already!")

while Running == True:
    readbuffer = s.recv(1024).decode("UTF-8")
    temp = str(readbuffer).split("\n")
    readbuffer = temp.pop()

    # TODO Get user list
    # TODO Async
    # TODO API

    for line in temp:
        # action=''
        # Checks whether the message is PING because its a method of Twitch to check if you're afk

        if ("PING :" in line):
            s.send(bytes("PONG\r\n", "UTF-8"))
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
                    # testing for the Ping:Pong crash
                    # print(message)
                    if username == '':
                        print(message)
                        print('Ping:Pong')

                    userfetch = c.execute("select * from users where uname = ?", (username.lower(),)).fetchall()
                    try:
                        user_status = userfetch[0][1]
                    except:
                        user_status = 'user'
                    # print(user_status)
                    print(username + " (" + user_status + "): " + message)

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
                    # if any(word in 'some one long two phrase three' for word in list_):
                    if any(ext in message for ext in TLD):
                        # if any(text in 'www .com http' for text in message):
                        # print(user_status)
                        if user_status not in ['admins', 'global_mods', 'moderators', 'subs', 'fots', 'vips', 'staff']:
                            Send_message(username + " links are not currently allowed.")
                            Send_message("/timeout " + username + " 1")

                    # Command processing
                    if message[0] == '!':
                        if username != '':
                            if username == 'rhyle_':
                                if message[0:8] == '!adduser':
                                    command, new_user, user_type = message.split(' ')
                                    c.execute("insert into users values (:user , :status)",
                                              {'user': new_user.lower(), 'status': user_type})
                                    conn.commit()

                                elif message[0:8] == '!deluser':
                                    command, new_user = message.split(' ')
                                    c.execute("delete from users where uname = ?", (new_user.lower(),))
                                    conn.commit()

                                elif message[0:8] == '!upduser':
                                    command, new_user, user_type = message.split(' ')
                                    c.execute("""update users 
                                            set status = ?
                                            where uname = ?""", (user_type, new_user.lower(),))
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
                                              {'command': command, 'target': target, 'action': action.lstrip(' ')})
                                    conn.commit()
                                    Send_message("Command " + command + " has been updated.")

                                elif message[0:7] == '!remove':
                                    # Parse the command to be removed
                                    ex_com, command = message.split(' ')
                                    command = '!' + command
                                    c.execute("delete from commands where ex_command = ?", (command,))
                                    conn.commit()
                                    Send_message("Command " + command + " has been removed.")

                                elif message[0:4] == '!mtc':
                                    parts = message.split(' ', 3)
                                    parts += '' * (3 - len(parts))
                                    ex_com, strm1, strm2 = parts
                                    command = '!multi'
                                    target = ''
                                    action = "Access the multitwitch at http://multitwitch.tv/" + strm1 + '/' + strm2 + '/'
                                    if c.execute("select * from commands where ex_command = '!multi'").fetchall() != []:
                                        c.execute("update commands set action = :action where ex_command = :command",
                                                  {'command': command, 'action': action})
                                        conn.commit()
                                    else:
                                        c.execute("insert into commands values (:command, :target, :action)",
                                                  {'command': command, 'target': target, 'action': action})
                                        conn.commit()
                                    Send_message(action)

                                elif message[0:4] == '!rew':
                                    parts = message.split(' ', 3)
                                    parts += '' * (3 - len(parts))
                                    ex_com, viewer, amount = parts
                                    rew_user = c.execute("select * from users where uname = ?",
                                                         (viewer.lower(),)).fetchone()
                                    cxp = rew_user[2]
                                    cxp += int(amount)
                                    c.execute("update users set exp = ? where uname = ?", (cxp, viewer.lower()))
                                    conn.commit()

                                    # parts = s.split(" ", 4) # Will raise exception if too many options
                                    # parts += [None] * (4 - len(parts)) # Assume we can have max. 4 items.
                                    # Fill in missing entries with None.
                                    # value1, value2, optional_value, optional_value2 = parts

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

                            if message[0:4] not in ('!upd', '!del', '!add', '!rem', '!cre', '!upd', '!gun', '!slo',
                                                    '!mtc', '!rew'):
                                try:
                                    chatmessage = message
                                    if message == '!lurk':
                                        chatmessage = "It looks like we've lost " + username + " to the twitch void. " \
                                                        "Hopefully they will find their way back soon!"
                                    elif message == "!ban":
                                        chatmessage = "It looks like " + username + " no longer thinks they can be a " \
                                                    "good member of the community and has requested to be banned."
                                        Send_message("/ban " + username + " Self exile")
                                    elif message == "!char":
                                        if c.execute("select gchar from users where uname = ?",
                                                     (username.lower(),)).fetchone() != ('',):
                                            chatmessage = c.execute("select gchar from users where uname = ?",
                                                                    (username.lower(),)).fetchone()[0]
                                        else:
                                            chatmessage = str(tcChargen.chat_char(username))
                                            c.execute("""update users 
                                                        set gchar = ? 
                                                        where uname = ?""", (chatmessage, username.lower()))
                                            conn.commit()

                                    elif message == "!retire":
                                        chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                                                            "moment, please check back soon(tm)."
                                    elif message == "!permadeath":
                                        chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                                                            "moment, please check back soon(tm)."
                                    else:
                                        chatmessage = c.execute("select action from commands where ex_command = ?",
                                                                (chatmessage,))
                                        chatmessage = chatmessage.fetchone()[0]
                                    Send_message(chatmessage)
                                except:
                                    Send_message(
                                        'Hello ' + username + " there is not currently a " + message + " command. " +
                                        "If you would like to have one created, let me know. Subs take precedence for !commands.")

                            # Gunter command
                            elif message[0:7] == '!gunter':
                                commandlist = list(c.execute("select ex_command from commands"))
                                for itr in range(len(commandlist)):
                                    commandlist[itr] = commandlist[itr][0]
                                Send_message(
                                    "You've found the (not so) hidden command list " + username + ". Command list: "
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
