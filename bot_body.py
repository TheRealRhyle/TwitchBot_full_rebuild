from random import randint
from random import choice
import ast
import socket
import json
import loader
import tcChargen
from urllib import request
import time
import datetime
from chattodb import social_ad, get_active_list
import beastiary

# TODO:
# TODO:
# TODO: For Challenges set a lower limit so characters do not go into the negative.
# TODO:
# TODO:

# Method for sending a message
def Send_message(message):
    s.send(("PRIVMSG #" + chan + " :" + message + "\r\n").encode('UTF-8'))
    # print(nick + ": " + message)

def get_user_exp(username):
    """
    Will get the user details for the database and return them as a dictionary
    :param username:
    :return:
    """
    user_info = c.execute("select * from users where uname = ?", (username,)).fetchone()
    return user_info[2]

def ret_char(username):
    char_to_return = c.execute("select gchar from users where uname = ?",(username,)).fetchone()[0]
    if char_to_return == '':
        return 'None'
    else:
        return ast.literal_eval(char_to_return)

def change_race(username, change_char):
    exp = int(c.execute('select exp from users where uname = ?',(username,)).fetchone()[0])-100
    c.execute("update users set gchar = ? where uname = ?",(change_char, username))
    c.execute("update users set exp = ? where uname = ?",(exp, username))
    conn.commit()

def get_elevated_users(target):
    resp = request.urlopen(f"http://tmi.twitch.tv/group/user/{target}/chatters")
    chatters_json = resp.read().decode("UTF-8")
    userlist = json.loads(chatters_json)
    bcaster = userlist['chatters']['broadcaster']
    vips = userlist['chatters']['vips']
    moderators = userlist['chatters']['moderators']
    eusers = bcaster, vips, moderators
    eaccess = set([user for sublist in eusers for user in sublist])

    return eaccess

def challenge(challenger, victim, amount):
    pass

def challenge_result(user, amount, *args):
    """
    Used to modify the XP as a result of a pvp challenge.
    :param user:
    :param amount:
    :param other_user:
    :return:
    """

    winner_exp = int(c.execute("select exp from users where uname = ?", (user,)).fetchone()[0])

    loser_exp = 0
    if not args:
        pass
    else:
        loser_exp = int(c.execute("select exp from users where uname = ?", (*args,)).fetchone()[0])
        loser_exp -= int(amount)
        if loser_exp < 0:
            loser_exp = 0
        c.execute("update users set exp = ? where uname = ?",(loser_exp, *args))
        conn.commit()
    winner_exp += int(amount)

    c.execute("update users set exp = ? where uname = ?",(winner_exp, user))
    conn.commit()

def uptime(at_command_time):
    return at_command_time - bot_start

def random_encounter():
    return beastiary.choose_mob()

def shop():
    pass

def level_up():
    pass

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
# Send_message(str(social_ad()))
bot_start = datetime.datetime.now().replace(microsecond=0)
pvp = {}
ad_iter = 0

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
            if ad_iter == 0:
                Send_message(str(social_ad()))
                print("Random encounter for: " + str(choice(get_active_list())))
                ad_iter += 1
            s.send(bytes("PONG\r\n", "UTF-8"))
            if ad_iter == 2:
                ad_iter = 0
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
                    print(user_status)
                    print(username + " (" + user_status + "): " + message)

                    #
                    # The bulk of the processing goes down here!
                    #
                    if message.lower() == '':
                        continue

                    # TODO Setup some better handling / identification for link handling.
                    # Link detection and timeout
                    # if any(word in 'some one long two phrase three' for word in list_):
                    if any(ext in message for ext in TLD):
                        # if any(text in 'www .com http' for text in message):
                        # print(user_status)
                        if username == nick:
                            pass
                        elif user_status not in ['admins', 'global_mods', 'moderators', 'subs', 'fots', 'vips', 'staff']:
                            Send_message(username + " links are not currently allowed.")
                            Send_message("/timeout " + username + " 1")

                    # Command processing
                    if message[0] == '!':
                        if username != '':
                            # TODO: Mod, Broadcaster, FOTS, VIP Commands
                            if username == 'rhyle_':
                                if message[0:8].lower() == '!adduser':
                                    command, new_user, user_type = message.split(' ')
                                    c.execute("insert into users values (:user , :status)",
                                              {'user': new_user.lower(), 'status': user_type})
                                    conn.commit()
                                elif message[0:8].lower() == '!deluser':
                                    command, new_user = message.split(' ')
                                    c.execute("delete from users where uname = ?", (new_user.lower(),))
                                    conn.commit()
                                elif message[0:8].lower() == '!upduser':
                                    command, new_user, user_type = message.split(' ')
                                    c.execute("""update users
                                            set status = ?
                                            where uname = ?""", (user_type, new_user.lower(),))
                                    conn.commit()
                                elif message[0:4].lower() == '!rew':
                                    
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
                                elif message[0:7].lower() == '!create':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("insert into commands values (:command, :target, :action)",
                                              {'command': command, 'target': target, 'action': action})
                                    conn.commit()
                                    Send_message("Command " + command + " has been added.")
                                elif message[0:7].lower() == '!update':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("update commands set action = :action where ex_command = :command",
                                              {'command': command, 'target': target, 'action': action.lstrip(' ')})
                                    conn.commit()
                                    Send_message("Command " + command + " has been updated.")
                                elif message[0:7].lower() == '!remove':
                                    # Parse the command to be removed
                                    ex_com, command = message.split(' ')
                                    command = '!' + command
                                    c.execute("delete from commands where ex_command = ?", (command,))
                                    conn.commit()
                                    Send_message("Command " + command + " has been removed.")
                                elif message[0:4].lower() == '!mtc':
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
                                elif message.lower() == "!slow":
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

                            elif username.lower() in get_elevated_users(chan):
                                if message[0:7].lower() == '!create':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("insert into commands values (:command, :target, :action)",
                                              {'command': command, 'target': target, 'action': action})
                                    conn.commit()
                                    Send_message("Command " + command + " has been added.")
                                elif message[0:7].lower() == '!update':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("update commands set action = :action where ex_command = :command",
                                              {'command': command, 'target': target, 'action': action.lstrip(' ')})
                                    conn.commit()
                                    Send_message("Command " + command + " has been updated.")
                                elif message[0:7].lower() == '!remove':
                                    # Parse the command to be removed
                                    ex_com, command = message.split(' ')
                                    command = '!' + command
                                    c.execute("delete from commands where ex_command = ?", (command,))
                                    conn.commit()
                                    Send_message("Command " + command + " has been removed.")
                                elif message[0:4].lower() == '!mtc':
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
                                elif message.lower() == "!slow":
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
                                chatmessage = message
                                if message.lower() == '!lurk':
                                    lurk_message = [
                                        f"It looks like we've lost {username} to the twitch void. Hopefully they will find their way back soon!",
                                        f"Seems like {username} has gone off to take care of.... business.",
                                        f"{username} has been eliminated by IOI-655321",
                                        "Thats no moon!", "ITS A TRAP!", f"{username} left for the greater unknown",
                                        f"{username.upper()} DID YOU PUT YOUR NAME IN THE HOT CUP?",f"{username.capitalize()} when someone asks " \
                                            "if you're a god you say yes.", "Well that certainly illustrates the diversity of the word."
                                    ]
                                    chatmessage = choice(lurk_message)
                                elif message.lower() == "!ban":
                                    chatmessage = "It looks like " + username + " no longer thinks they can be a " \
                                                "good member of the community and has requested to be banned."
                                    Send_message("/ban " + username + " Self exile")
                                elif message[0:6].lower() == "!chang":
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
                                elif message.lower() == "!char":
                                    if c.execute("select gchar from users where uname = ?",
                                                 (username.lower(),)).fetchone() != ('',):
                                        gchar_dict_to_sql = c.execute("select gchar from users where uname = ?",
                                                                      (username.lower(),)).fetchone()[0]
                                        gchar_dict = ast.literal_eval(gchar_dict_to_sql)

                                        cxp = c.execute("select exp from users where uname = ?",(username,)).fetchone()[0]
                                        # print(gchar_dict)
                                        article = 'a '
                                        if gchar_dict['race'] == 'elf':
                                            gchar_dict['race'] = 'elven'
                                            article = 'an '
                                        elif gchar_dict['race'] == 'dwarf':
                                            gchar_dict['race'] = 'dwarven'

                                        chatmessage = ""
                                        # chatmessage = f"{username} is {article} " \
                                        #     f"{str(gchar_dict['race']).capitalize()} {gchar_dict['prof']}"

                                        # print(*gchar_dict, sep='\n')

                                        build_whisper = f"{username} {username} is {article}" \
                                            f"{str(gchar_dict['race']).capitalize()} " \
                                            f"{gchar_dict['prof']} Weapon Skill: {gchar_dict['weapon_skill']} " \
                                            f"Ballistic Skill: {gchar_dict['ballistic_skill']} Strength: " \
                                            f"{gchar_dict['strength']} Toughness: {gchar_dict['toughness']} " \
                                            f" You are currently using your " \
                                            f"{str(gchar_dict['weapon']).capitalize()} as a weapon and " \
                                            f"{str(gchar_dict['armor']).capitalize()} for armor. If you would like to" \
                                            f" upgrade either you can !shop to spend your Exp to purchase new weapons" \
                                            f" and armor.  Current available Exp: {cxp}"

                                        Send_message(f"/w {build_whisper}")

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

                                        # Message to chat and /w to user the character information.
                                        chatmessage = f"{username} the {str(gchar_dict['race']).capitalize()} has " \
                                            f"entered the game."
                                        # This is the whisper to user.
                                elif message.lower() == "!retire":
                                    # TODO: Retired characters should output to HTML and be stored on a webserver.
                                    # TODO: should also provide link for download in whisper.
                                    chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                                                        "moment, please check back soon(tm)."
                                elif message.lower() == "!permadeath":
                                    # TODO: Permadeath command should just wipe the gchar data from the user table for
                                    # TODO: the command user.
                                    try:
                                        c.execute("update users set gchar = '' where uname = ?",(username.lower(),))
                                        conn.commit()
                                        chatmessage = username + " has chosen to permanently kill off their " \
                                                "character. You may issue the !char command to create a new one."

                                    except:
                                        chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                                                        "moment, please check back soon(tm)."
                                elif message.lower() == "!accept":
                                    for challenger, victim in pvp.items():
                                        if victim[0] == username:
                                            chall = ret_char(challenger[0])
                                            vic = ret_char(victim[0])

                                            Send_message(f"{str(chall['name']).capitalize()}, " \
                                                f"{str(vic['name']).capitalize()} has accepted your challenge.  Prepare for " \
                                                f"combat!")
                                            time.sleep(1)
                                            victim_random = randint(2, 100)
                                            vic_roll = (vic['weapon_skill'] + victim_random) - chall['toughness']
                                            if vic_roll < 0:
                                                vic_roll = 0
                                            Send_message(f"{victim[0]} hits {challenger[0]} with their {vic['weapon']} " \
                                                f"(({vic['weapon_skill']} + {victim_random})-{chall['toughness']}) ({vic_roll})")
                                            time.sleep(1)
                                            challenger_random = randint(2, 100)
                                            chall_roll = (chall['weapon_skill'] + challenger_random) - vic['toughness']
                                            if chall_roll < 0:
                                                chall_roll = 0
                                            Send_message(f"{challenger[0]} returns the blow with their {chall['weapon']} " \
                                                f"(({chall['weapon_skill']} + {challenger_random}) - {vic['toughness']}) ({chall_roll})")
                                            time.sleep(1)

                                            if vic_roll > chall_roll:
                                                Send_message(f'{victim[0]} has defeated their challenger {challenger[0]} and ' \
                                                    f'earned! {amount} exp.')
                                                challenge_result(victim[0], amount, challenger[0])
                                            elif vic_roll == chall_roll:
                                                Send_message(f'After a bloody fight {victim[0]} and {challenger[0]} call it a draw!')
                                            else:
                                                Send_message(f'{challenger[0]} has bested his victim, {victim[0]}, earning ' \
                                                    f'themselves {amount}')
                                                challenge_result(challenger[0], amount)
                                            chatmessage = ""
                                        else:
                                            chatmessage = f"There is not currently a pending challenge for {username}"
                                    del pvp[challenger]

                                elif message.lower() == '!decline':
                                    for challenger, victim in pvp.items():
                                        if victim[0] == username:
                                            chall = ret_char(challenger[0])
                                            vic = ret_char(victim[0])

                                            chatmessage = f"{str(chall['name']).capitalize()}, " \
                                                f"{str(vic['name']).capitalize()} has declined your challenge."
                                    del pvp[challenger]

                                elif message.lower() == "!challenge":
                                    chatmessage = "This command will allow you to challenge another viewer with a " \
                                        "game character to a quick PVP fight. The proper usage is !challenge username " \
                                        "amount  Please not that you may not challenge for an amount more than your " \
                                        "current exp.  Current exp can be found on your !char whisper, it updates every " \
                                        "10 minutes."
                                elif message[0:11].lower() == "!challenge ":
                                    # TODO: !challenge <target> <risk amount>
                                    try:
                                        ex_com, target, amount = message.split(' ')
                                    except ValueError:
                                        Send_message(f'Blast! {username} the proper command is !challenge >target< ' \
                                            f'>risk amount<')
                                        continue

                                    cxp = get_user_exp(username)
                                    challenger = ret_char(username)
                                    victim = ret_char(target)

                                    absolute_amount = int(amount)
                                    absolute_amount = abs(absolute_amount)

                                    if target == username:
                                        chatmessage = f"Nice try {username}, you can beat yourself on your own time."
                                    elif victim == 'None' or challenger == 'None':
                                        chatmessage = f'Sorry {username}, either you or {target} do not currently ' \
                                            f'have characters for the game. You can use the command !char to either ' \
                                            f'generate one or get your current character info whispered to you.'
                                    elif absolute_amount > int(cxp):
                                        chatmessage = f"{username} attempting to wager more exp than you have is " \
                                            f"not allowed. You may risk only the exp you've earned."
                                    else:
                                        chatmessage = f'hey @{target}, {username} has wagered {str(absolute_amount)} exp that they' \
                                            f' can take you down.  If you want to accept the fight type !accept or you can !decline.'
                                        pvp[(f'{username.lower()}',f'{time.time()}')] = (f'{target.lower()}', amount)
                                elif message.lower() == "!uptime":
                                    timenow = datetime.datetime.now().replace(microsecond=0)

                                    chatmessage = f'Rhyle_Bot has been running for {str(uptime(timenow))}, this is not ' \
                                        f'stream uptime.'
                                else:
                                    try:
                                        chatmessage = c.execute("select action from commands where ex_command = ?",
                                                                (chatmessage,)).fetchone()[0]
                                    except:
                                        chatmessage = f'Hello {username} there is not currently a {message} command. ' \
                                                    f'If you would like to have one created, let me know. Subs take precedence for !commands.'
                                        # print(f'504: {chatmessage}')

                                # send the assembled chatmessage variable
                                try:
                                    Send_message(chatmessage)
                                except:
                                    print(f'531: {chatmessage}')

                            # Gunter command
                            elif message[0:7].lower() == '!gunter':
                                commandlist = list(c.execute("select ex_command from commands"))
                                for itr in range(len(commandlist)):
                                    commandlist[itr] = commandlist[itr][0]
                                Send_message(
                                    "You've found the (not so) hidden command list " + username + ". Command list: "
                                    + ', '.join(commandlist))

                            else:
                                print(f'543: {username}, {message}')
                                # Send_message(f'Hello {username} there is not currently a {message} command. ' \
                                #             f'If you would like to have one created, let me know. Subs take precedence for !commands.')
                    #
                    # End of bot processing
                    #

                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True
