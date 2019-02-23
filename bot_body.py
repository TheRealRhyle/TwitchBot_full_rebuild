import ast
import socket
import json
import loader
import tcChargen
from urllib import request


# from chattodb import check_chatters

# Method for sending a message
def Send_message(message):
    s.send(("PRIVMSG #" + chan + " :" + message + "\r\n").encode('UTF-8'))
    # print(nick + ": " + message)

def ret_char(username):
    char_to_return = c.execute("select gchar from users where uname = '{}'".format(username)).fetchone()[0]
    return ast.literal_eval(char_to_return)

def change_race(username, change_char):
    exp = int(c.execute('select exp from users where uname = ?',(username,)).fetchone()[0])-100
    c.execute("update users set gchar = ? where uname = ?",(change_char, username))
    c.execute("update users set exp = ? where uname = ?",(exp, username))
    conn.commit()

def get_bcaster(target):
    resp = request.urlopen(f"http://tmi.twitch.tv/group/user/{target}/chatters")
    chatters_json = resp.read().decode("UTF-8")
    userlist = json.loads(chatters_json)
    bcaster = userlist['chatters']['broadcaster'][0]
    return  bcaster

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
# s.send(bytes("ROOMSTATE #rhyle_\r\n", 'UTF-8'))

Running = True
readbuffer = ''
MODT = False
init_mesage = ''
slow = 'off'
Send_message("I'm awake, quit poking me already, try !commands or something.")

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
                                    parts = message.split(' ')
                                    ex_com, strm1, strm2, strm3, strm4 = [parts[i] if i < len(parts) else None for i in range(5)]
                                    command = '!multi'
                                    target = ''
                                    if strm3 == None:
                                        multi = strm1 + '/' + strm2
                                    elif strm4 == None:
                                        multi = strm1 + '/' + strm2 + '/' + strm3
                                    else:
                                        multi = strm1 + '/' + strm2 + '/' + strm3 + '/' + strm4

                                    action = "Access the multitwitch at http://multitwitch.tv/" + multi + " " \
                                             "or you can access kadgar at http://kadgar.net/live/" + multi

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
                                    rew_user = int(c.execute("select exp from users where uname = ?",(viewer.lower(),)).
                                                   fetchone()[0])
                                    print(rew_user)
                                    rew_user += int(amount)
                                    print(rew_user)
                                    c.execute("update users set exp = ? where uname = ?", (rew_user, viewer.lower()))
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

                            if message[0:4] not in ('!upd', '!del', '!add', '!rem', '!cre', '!upd', '!gun', '!slo',
                                                    '!mtc', '!rew'):
                                try:
                                    chatmessage = message
                                    if message == '!lurk':
                                        chatmessage = "It looks like we've lost " + username + " to the twitch void. " \
                                                        "Hopefully they will find their way back soon!"
                                    elif message[0:5] == '!chec':
                                        ex_com, tgt = message.split(' ')
                                        print(get_bcaster(tgt))

                                    elif message == "!ban":
                                        chatmessage = "It looks like " + username + " no longer thinks they can be a " \
                                                    "good member of the community and has requested to be banned."
                                        Send_message("/ban " + username + " Self exile")
                                    elif message[0:6] == "!chang":
                                        try:
                                            ex_com, race = message.split(" ")
                                            change_char = ret_char(username)
                                            cxp = int(c.execute('select exp from users where uname = ?',(username,)).fetchone()[0])
                                            if cxp < 100:
                                                chatmessage = f"Sorry {username}, you do not have enough accrued exp to" \
                                                    f" change your race at the moment, please try again later {cxp}/100."
                                            elif race.lower() not in ['human','elf','halfling','dwarf']:
                                                chatmessage = f'Sorry {username}, you must choose one of the 4 standard WFRP' \
                                                    f' races: Human, Elf, Dwarf, Halfling. Please try again.'
                                            elif race.lower() == 'human' and change_char['race'] != 'human':
                                                change_char['race']='human'
                                                change_race(username, str(change_char))
                                                chatmessage=f'{username} you race has been changed to {race}'
                                            elif race.lower() == 'elf' and change_char['race'] != 'elf':
                                                change_char['race']='elf'
                                                change_race(username, str(change_char))
                                                chatmessage=f'{username} you race has been changed to {race}'
                                            elif race.lower() == 'halfling' and change_char['race'] != 'halfling':
                                                change_char['race']='halfling'
                                                change_race(username, str(change_char))
                                                chatmessage=f'{username} you race has been changed to {race}'
                                            elif race.lower() == 'dwarf' and change_char['race'] != 'dwarf':
                                                change_char['race']='dwarf'
                                                change_race(username, str(change_char))
                                                chatmessage=f'{username} you race has been changed to {race}'


                                        except:
                                            chatmessage = f'Sorry {username}, you must choose one of the 4 standard WFRP' \
                                                f' races: Human, Elf, Dwarf, Halfling.'
                                    elif message == "!char":
                                        if c.execute("select gchar from users where uname = ?",
                                                     (username,)).fetchone() != ('',):
                                            gchar_dict_to_sql = c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
                                            gchar_dict = ast.literal_eval(gchar_dict_to_sql)
                                            article = 'a '
                                            if gchar_dict['race'] == 'elf':
                                                gchar_dict['race'] = 'elven'
                                                article = 'an '
                                            elif gchar_dict['race'] == 'dwarf':
                                                gchar_dict['race'] = 'dwarven'

                                            chatmessage = f"/w {username} {username} is {article} " \
                                                f"{str(gchar_dict['race']).capitalize()} {gchar_dict['prof']}"

                                        else:
                                            # Generate character using the Character Class
                                            gchar = tcChargen.chat_char(username)
                                            # Converts the Class to a dictionary
                                            gchar_dict = gchar.get_char(username)
                                            # Casts the dictionary to a string for storage in SQL
                                            gchar_dict_to_sql = str(gchar_dict)

                                            article = 'a '
                                            if gchar_dict['race'] == 'elf':
                                                gchar_dict['race'] = 'elven'
                                                article = 'an '
                                            elif gchar_dict['race'] == 'dwarf':
                                                gchar_dict['race'] = 'dwarven'


                                            # Stores character in SQL
                                            c.execute("""update users 
                                                        set gchar = ? 
                                                        where uname = ?""", (gchar_dict_to_sql, username.lower()))
                                            conn.commit()

                                            chatmessage = f"/w {username} {username} is {article} " \
                                                f"{str(gchar_dict['race']).capitalize()} {gchar_dict['prof']}"
                                            Send_message(f"{username} the {str(gchar_dict['race']).capitalize()} has "
                                                         f"entered the game.")
                                    elif message == "!retire":
                                        # TODO: Retired characters should output to HTML and be stored on a webserver.
                                        # TODO: should also provide link for download in whisper.
                                        chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                                                            "moment, please check back soon(tm)."
                                    elif message == "!permadeath":
                                        # TODO: Permadeath command should just wipe the gchar data from the user table for 
                                        # the command user.
                                        # c.execute("update commands set action = :action where ex_command = :command",
                                        #       {'command': command, 'target': target, 'action': action.lstrip(' ')})
                                        # conn.commit()
                                        try:
                                            c.execute("update users set gchar = '' where uname = ?",(username.lower(),))
                                            conn.commit()
                                            chatmessage = username + " has chosen to permanently kill off their " \
                                                    "character. You may issue the !char command to create a new one."

                                        except:
                                            chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                                                            "moment, please check back soon(tm)."
                                    elif message == "!accept":
                                        chatmessage = 'This command will be used to accepting viewer issued duels in ' \
                                                      'the future.  Right now it only gives this message.'
                                    elif message[0:10] == "!challenge":
                                        # !challange <target> <risk amount>
                                        try:
                                            ex_com, target, amount = message.split(' ')
                                            chatmessage = f'hey @{target}, {username} has wagered {amount} exp that they' \
                                                f' can take you down.  If you want to accept the fight type !accept.' \
                                                f' Don\'t worry though, this command doesnt actually do anything at'\
                                                ' this time.'
                                        except:
                                            chatmessage = f'Blast! {username} the proper command is !challenge <target> ' \
                                                f'<risk amount>'
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
