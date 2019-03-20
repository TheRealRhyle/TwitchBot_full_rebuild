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
import bestiary

# Method for sending a message
def Send_message(message):
    time.sleep(0.1)
    s.send(("PRIVMSG #" + chan + " :" + message + "\r\n").encode('UTF-8'))
def get_user_exp(username):
    """
    Will get the user details for the database and return them as a dictionary
    :param username:
    :return current xp integer and available crowns:
    """
    user_info = c.execute("select * from users where uname = ?", (username,)).fetchone()
    return user_info[2], user_info[4]
def ret_char(username):
    try:
        char_to_return = c.execute("select gchar from users where uname = ?",(username,)).fetchone()[0]
        # print(char_to_return)
    except TypeError:
        print("User in channel that has not been added to the database yet: ", username)
        char_to_return = ''
    finally:
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
def random_encounter(*args):
    encounter_value = 100
    encounter_dictionary = bestiary.choose_mob()

    if not args:
        random_character = ret_char(choice(get_active_list()))
    else:
        user = args[0]
        random_character= ret_char(user)

    while random_character == 'None':
        random_character = ret_char(str(choice(get_active_list())))

    character_roll = (randint(2,100) + random_character['weapon_skill']) - int(encounter_dictionary['t'])
    mob_roll = (randint(2,100) + int(encounter_dictionary['ws'])) - random_character['toughness']

    # --------------------------------
    # BEGIN Random Encounter Rebuild
    # --------------------------------

    # random_roll = randint(1,101)
    # print("Random Roll: " + str(random_roll))
    # print(random_character['name'] + ' weapon skill: ' + str(random_character['weapon_skill']))
    # if random_roll <= random_character['weapon_skill']:
    #     print("this would be a hit")
    #     ranks = int((random_character['weapon_skill'] - random_roll) / 5)
    #     print("Degrees of success: " +str(ranks))
    #     if random_character['weapon'] == "Fists":
    #         dmg = (int(random_character['strength']/10)-4) + ranks
    #         if dmg < 1:
    #             dmg = 1
    #         print("Damage would be (SB-4): " + str(dmg))
    # else:
    #     print("miss")

    # --------------------------------
    # END Random Encounter Rebuild
    # --------------------------------



    if mob_roll > character_roll:
        loser = random_character['name'].lower()
    elif mob_roll == character_roll:
        loser = 'either of them.  Beaten and bloodied they each run off to fight another day.'
    else:
        loser = encounter_dictionary['name'].lower()
        exp, gc = get_user_exp(random_character['name'].lower())
        encounter_value += exp

        c.execute("update users set exp = ? where uname = ?", (encounter_value, random_character['name'].lower()))
        conn.commit()

    adj = choice(["walking", "running", "riding"])
    location = choice(["forest", "town", "desert"])
    if ' or ' in encounter_dictionary["weapon"]:
        mob_weapon = encounter_dictionary["weapon"].split(' or ')
        mob_weapon = choice(mob_weapon)
    else:
        mob_weapon = encounter_dictionary["weapon"]

    chatmessage = f'While {adj} through the {location} {random_character["name"]} '\
        f'encountered a {encounter_dictionary["name"]}.  There was a mighty battle: ' \
        f'{random_character["name"]} readied their {random_character["weapon"]} against the ' \
        f'{mob_weapon} of the {encounter_dictionary["name"]} the fight' \
        f' did not end well for {loser}. {character_roll} vs {mob_roll}'

    return chatmessage
def shop(username, *args):
    import itemlist
    shoplist = itemlist.load_shop()
    shop_items = []
    shop_message = ''
    if not args:
        shop_message = f"/w {username} Welcome to the shop!  The following commands are necessary for using the shop: " \
            f"!shop melee, ranged, or armor will show you the available weapons.  !shop buy followed by the item you would " \
            f"like to purchase will allow you to purchase that specific item assuming that you have the available crowns."
    elif args[0].lower() == 'melee' or args[0].lower() == 'ranged' or args[0].lower() == 'armor':
        [shop_items.append(f"[{item}] {shoplist[item]['type']} {shoplist[item]['cost']}") for item in shoplist if shoplist[item]['type'].lower() == args[0].lower()]
        shop_items = str(shop_items).replace('[\'','').replace(']\'','').replace("', '"," ").replace("']", "")
        shop_message = f"/w {username} The available items are as follows: {shop_items}"
    elif args[0].lower() == 'buy':
        shopper = ret_char(username)
        shopper_xp, shopper_purse = get_user_exp(username)
        print(len(args))
        if len(args) != 2:
            shop_message = "I'm sorry, I didn't understand that, please try again."
        else:
            new_weapon = args[1].lower()
            if new_weapon not in shoplist:
                shop_message = "No item exists that with that name, please look at the !shop melee, !shop armor or !shop ranged list again."
                return

            crown_cost = shoplist[args[1].lower()]['cost'].split(' ')
            # print(crown_cost[0], shopper_purse)

            if int(shopper_purse) >= int(crown_cost[0]):
                # TODO update character w/ purchased weapon
                # TODO deduct cost from user data
                if shoplist[new_weapon.lower()]['type'] == 'Melee' or shoplist[new_weapon.lower()]['type'] == 'Ranged':
                    shopper['weapon'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?",(int(shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper),username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You brandish your new {args[1]}.  It fits your hands " \
                        f"as though it was made for you."
                elif shoplist[new_weapon.lower()]['type'] == 'Armor':
                    shopper['armor'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?",(int(shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper),username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You don your new {args[1]}.  The armor fits " \
                        f"as though it was made for you."
            else:
                Send_message(f"/w {username} You do not have enough Crowns to buy the {args[1]}. " \
                    f"Your current purse is {shopper_purse}.")
                return

    Send_message(shop_message)
    # chatmessage = ''
def level_up(username, stat):
    if stat.lower() == 'ws':
        stat= 'weapon_skill'
    elif stat.lower() == "bs":
        stat = 'ballistic_skill'
    elif stat.lower() == "t":
        stat = 'toughness'
    elif stat.lower() == "s":
        stat = 'strength'
    else:
        Send_message(f"/w {username} {stat} is an unknown stat.  You may only levelup WS, BS, S, or T.")
        return

    cxp = c.execute("select exp from users where uname = ?",(username,)).fetchone()[0]
    if c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone() != ('',):
        gchar_dict_to_sql = c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
        gchar_dict = ast.literal_eval(gchar_dict_to_sql)
    else:
        whisper = f"/w {username} {username}, you do not currently have a character, create one with the !char command."
    
    if cxp >= 100 and gchar_dict[stat] < 75:
        cxp -= 100
        gchar_dict[stat] += 5
        c.execute("update users set exp = ?, gchar = ? where uname = ?",(cxp, str(gchar_dict), username))
        conn.commit()
        whisper = f"/w {username} Your {stat} has been increased by 5 points to {gchar_dict[stat]}"
        
    elif gchar_dict[stat] >= 75:
        whisper = f"/w {username} Your {stat} has is already maxed out."
    elif cxp < 100:
        whisper = f"/w {username} Sorry {username} you do not currently have enough experience to " \
            f"upgrade your character.  Current EXP: {cxp}"
    else:
        whisper = f"/w {username} Something strange happend, please alert Rhyle_.  tell him 'def level_up hit else'."
    # print(username, cxp, gchar_dict[stat] + 5)
    Send_message(whisper)


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
# s.send(bytes('CAP REQ :twitch.tv/membership\r\n', 'UTF-8'))
# s.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'UTF-8'))
# s.send(bytes('CAP REQ :twitch.tv/commands\r\n', 'UTF-8'))



Running = True
random_character = 'None'
readbuffer = ''
MODT = False
init_mesage = ''
slow = 'off'
Send_message(social_ad())
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
        # print(line)
        # Checks whether the message is PING because its a method of Twitch to check if you're afk

        if ("PING :" in line):
            s.send(bytes("PONG\r\n", "UTF-8"))
            if ad_iter == 0:
                Send_message(random_encounter())
                # //TODO: Exclude known bots - https://trello.com/c/fmeBaOuW/1-exclude-known-bots
                # random_encounter()
                ad_iter += 1
            elif ad_iter == 1:
                Send_message(choice([social_ad(), random_encounter()]))
                ad_iter = 0
        else:
            # TODO: botbody line 305, split on whitespace - 
            # https://trello.com/c/MmwQH2XG/24-botbody-line-305-split-on-whitespace# 
            # parts = line.split(" ",1)
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
                            if username.lower() in ['rhyle_', 'katiequixotic']:
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
                                elif "!givecrowns" in message:
                                    ex_com, user, amount = message.split(' ')
                                    gc_user = int(c.execute("select crowns from users where uname = ?", (user.lower(),)).fetchone()[0])
                                    gc_user += int(amount)
                                    c.execute("update users set crowns = ? where uname = ?",(gc_user, user.lower()))
                                    conn.commit()
                                elif message[0:4].lower() == '!rew':
                                    parts = message.split(' ', 3)
                                    parts += '' * (3 - len(parts))
                                    ex_com, viewer, amount = parts
                                    if '@' in viewer:
                                        viewer.replace('@', '')

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
                                elif ('!randomenc') in message.lower():
                                    try:
                                        ex_com, user = message.lower().split(' ')
                                        Send_message(random_encounter(user))
                                    except:
                                        Send_message(random_encounter())
                                    continue
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
                                elif '!vip' in message.lower():
                                    ex_com, user = message.lower().split(' ')
                                    Send_message('/vip ' + user)
                                elif '!join' in message.lower():
                                    ex_com, channel = message.split(' ')
                                    s.send(bytes("JOIN #" + channel.lower() + "\r\n", 'UTF-8'))
                                    time.sleep(1)
                                    message = "Just testing, dont Hz me"
                                    s.send(("PRIVMSG #" + channel.lower() + " :" + message + "\r\n").encode('UTF-8'))
                                elif '!part' in message.lower():
                                    ex_com, channel = message.split(' ')
                                    message = "Fine, I'm leaving."
                                    time.sleep(1)
                                    s.send(("PRIVMSG #" + channel.lower() + " :" + message + "\r\n").encode('UTF-8'))
                                    s.send(bytes("PART #" + channel.lower() + "\r\n", 'UTF-8'))

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


                            if message[0:4] not in ('!upd', '!del', '!add', '!rem', \
                                '!cre', '!upd', '!gun', '!slo', '!mtc', '!rew', '!ran'):
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
                                    #test if user in database
                                    try:
                                        user = c.execute("select * from users where uname = ?",(username.lower(),))
                                        print(user)
                                    except:
                                        c.execute("""insert into users values (?, ?, 0, '', 0)""",(username.lower(), 'viewer'))
                                        conn.commit()
                                        print(f"user {username} has been added to the database")
                                    finally:
                                        if c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone() != ('',):
                                            gchar_dict_to_sql = c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
                                            gchar_dict = ast.literal_eval(gchar_dict_to_sql)

                                            cxp, crowns = c.execute("select exp, crowns from users where uname = ?",(username,)).fetchone()
                                            # print(gchar_dict)
                                            article = 'a '
                                            if gchar_dict['race'] == 'elf':
                                                gchar_dict['race'] = 'elven'
                                                article = 'an '
                                            elif gchar_dict['race'] == 'dwarf':
                                                gchar_dict['race'] = 'dwarven'
                                            else:
                                                chat_race = gchar_dict['race']

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
                                                f" and armor.  Current available Exp: {cxp} Purse: {crowns}"

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
                                                chat_race = 'elf'
                                                article = 'an '
                                            elif gchar_dict['race'] == 'dwarf':
                                                chat_race = 'dwarf'
                                                gchar_dict['race'] = 'dwarven'
                                            else:
                                                chat_race = gchar_dict['race']
                                            cxp = c.execute("select exp from users where uname = ?",(username,)).fetchone()[0]

                                            # Stores character in SQL
                                            c.execute("""update users
                                                        set gchar = ?
                                                        where uname = ?""", (gchar_dict_to_sql, username.lower()))
                                            conn.commit()

                                            # Message to chat and /w to user the character information.
                                            chatmessage = f"{username} the {chat_race.capitalize()} has " \
                                                f"entered the game."

                                            # This is the whisper to user.
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
                                        target = target.lower()
                                        if '@' in target:
                                            target = target.replace('@','')
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
                                    elif absolute_amount > int(cxp[0]):
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
                                elif "levelup" in message.lower():
                                    chatmessage = ''
                                    if len(message) == 8:
                                        chatmessage = "The proper command for this includes one of the " \
                                            "four character stats: WS, BS, S, T."
                                    else:
                                        ex_com, stat = message.split(' ')
                                        level_up(username, stat)
                                elif "!shop" in message.lower():
                                    if len(message) == 5:
                                        shop(username)
                                    else:
                                        ex_com, *arg = message.split(' ')
                                        shop(username, *arg)
                                    chatmessage =""
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
                                    print(f'784: {chatmessage}')

                            # Gunter command
                            elif message[0:7].lower() == '!gunter':
                                commandlist = list(c.execute("select ex_command from commands"))
                                for itr in range(len(commandlist)):
                                    commandlist[itr] = commandlist[itr][0]
                                for item in ["!lurk", "!ban", "!change", "!char", "!retire", "!permadeath", \
                                    "!challenge", "!uptime", "!levelup", "!shop", "!gunter"]:
                                    commandlist.append(item)
                                Send_message(
                                    "You've found the (not so) hidden command list " + username + ". Command list: "
                                    + ', '.join(commandlist))

                            else:
                                print(f'846: {username}, {message}')
                                # print(chatmessage)
                                # Send_message(f'Hello {username} there is not currently a {message} command. ' \
                                #             f'If you would like to have one created, let me know. Subs take precedence for !commands.')
                    #
                    # End of bot processing
                    #

                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True
