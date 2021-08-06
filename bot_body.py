from random import randint, choice
import math
import ast
import socket
import json
from urllib import request
import datetime
import time


import loader
from wfrpgame import tcChargen, bestiary
from utils import twitter, commands
from chattodb import social_ad, get_active_list
import myTwitch
import wfrpgame
# import song_request
# import playlist_maker



# Method for sending a message
def Send_message(message, *args):
    time.sleep(0.2)

    if " ^user " in message:
        # print("Message: ", message)
        # print(args[0])
        message = message.replace(" ^user ", " " + str(args[0]) + " ")
        args = []

    if " ^user.upper " in message:
        # print("Message: ", message)
        # print(args[0])
        message = message.replace(" ^user.upper", " " + str(args[0]).upper() + " ")
        args = []
    if "^target" in message:
        # print("Message:", message)
        # print(args[0])
        message = message.replace("^target", str(args[0]))
        args = []
    args = []

    if not args:
        s.send(("PRIVMSG #" + chan + " :" + message + "\r\n").encode('UTF-8'))
    else:
        s.send(("PRIVMSG #" + args[0] + " :" +
                message + "\r\n").encode('UTF-8'))

def get_user_exp(username):
    """
    Will get the user details for the database and return them as a dictionary
    :param username:
    :return current xp integer and available crowns:
    """
    user_info = c.execute(
        "select * from users where uname = ?", (username,)).fetchone()
    return user_info[2], user_info[4], user_info[5]

def ret_char(username):
    try:
        char_to_return = c.execute(
            "select gchar from users where uname = ?", (username,)).fetchone()[0]
        if c.execute("select status from users where uname = ?", (username,)).fetchone()[0] == 'bot':
            char_to_return = ''
    except TypeError:
        print("User in channel that has not been added to the database yet: ", username)
        char_to_return = ''
    finally:
        if char_to_return == '':
            return 'None'
        else:
            return ast.literal_eval(char_to_return)

def change_race(username, change_char):
    exp = int(c.execute('select exp from users where uname = ?',
                        (username,)).fetchone()[0])-100
    c.execute("update users set gchar = ? where uname = ?", (change_char, username))
    c.execute("update users set exp = ? where uname = ?", (exp, username))
    conn.commit()

def get_elevated_users(target):
    resp = request.urlopen(
        f"http://tmi.twitch.tv/group/user/{target}/chatters")
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

    winner_exp = int(
        c.execute("select exp from users where uname = ?", (user,)).fetchone()[0])

    loser_exp = 0
    if not args:
        pass
    else:
        loser_exp = int(
            c.execute("select exp from users where uname = ?", (*args,)).fetchone()[0])
        loser_exp -= int(amount)
        if loser_exp < 0:
            loser_exp = 0
        c.execute("update users set exp = ? where uname = ?",
                  (loser_exp, *args))
        conn.commit()
    winner_exp += int(amount)

    c.execute("update users set exp = ? where uname = ?", (winner_exp, user))
    conn.commit()

def uptime(at_command_time):
    return at_command_time - bot_start

def random_encounter(*args):
    from wfrpgame import itemlist
    shoplist = itemlist.load_shop()

    encounter_value = 100
    c_wins = 1
    encounter_dictionary = bestiary.choose_mob()
    hit_location, c_hit_location, m_hit_location = 0, 0, 0
    loser = ''

    if not args:
        random_character = ret_char(choice(get_active_list()))

    else:
        user = args[0].strip('\r\n')
        random_character = ret_char(user)

    while random_character == 'None':
        random_character = ret_char(str(choice(get_active_list())))

    # character_roll = (randint(2, 100) + random_character['weapon_skill']) - int(encounter_dictionary['t'])
    # mob_roll = (randint(2, 100) + int(encounter_dictionary['ws'])) - random_character['toughness']

    # --------------------------------
    # BEGIN Random Encounter Rebuild
    # --------------------------------

    # --------------------------------
    # WFRP Roll rules: Need to roll UNDER your WS/BS.  For each full
    # 10% you beat your chance by, you achieve one degree of success.
    # Roll to hit using percentile dice. Use Weapon Skill for melee
    # attacks and Ballistic Skill for ranged attacks. If the player rolls
    # equal to or less than the character’s Weapon Skill or Ballistic
    # Skill (as appropriate), a hit is scored.
    # --------------------------------

    character_weapon = random_character['weapon']
    try:
        print(shoplist[character_weapon])
        if shoplist[character_weapon]['damage'] == "SB":
            print(math.floor((random_character['strength'])/10))
    except:
        print(character_weapon)


    character_roll = (randint(2, 100))
    character_ws = random_character['weapon_skill']

    # print(f'Character: {character_ws} : {character_roll}')
    if character_roll > character_ws:
        character_gos = -1
    elif character_roll == character_ws:
        character_gos = 0
    else:
        c_hit_location = str(character_roll)[::-1]
        character_gos = math.floor((character_ws - character_roll) / 10)
    # print(f'Character Successes: {character_gos}')

    mob_roll = (randint(2, 100))
    mob_ws = int(encounter_dictionary['ws'])
    # print(f'Mob: {mob_ws}:{mob_roll}')
    if mob_roll > mob_ws:
        mob_gos = -1
    elif mob_roll == mob_ws:
        mob_gos = 0
    else:
        m_hit_location = str(mob_roll)[::-1]
        mob_gos = math.floor((mob_ws - mob_roll) / 10)
    # print(f'Monster Successes: {mob_gos}')

    if (character_gos > mob_gos) and (character_gos >= 0):
        hit_location = c_hit_location
        loser = encounter_dictionary['name'].lower()
        exp, _, wins = get_user_exp(random_character['name'].lower())
        encounter_value += exp
        c_wins += wins
        c.execute("update users set exp = ?, wins = ? where uname = ?", (encounter_value, c_wins, random_character['name'].lower()))
        conn.commit()
        # print('Point: Character!')
    elif (character_gos == mob_gos) and (character_gos >= 0):
        hit_location = c_hit_location
        loser = 'Beaten and bloodied they each ran off to fight another day.'
        # print('Point: Both!')
    elif (character_gos < mob_gos) and (mob_gos >= 0):
        hit_location = m_hit_location
        loser = random_character['name'].lower()
        # print('Point: Mob!')
    else:
        pass
        # print("BOTH MISS")

    # --------------------------------
    # Determine Hit Location. If a hit is scored the player determines
    # where the blow has landed. Take the attack roll, reverse the order
    # of the percentile dice (an attack roll of 37, for example, would
    # hit location 73), and consult the following chart:
    # hIT loCaTIon
    # % roll Location
    # 01-15 Head, 16-35 Right Arm, 36-55 Left Arm, 56-80 Body, 81-90 Right Leg, 91-00 Left Leg
    # --------------------------------
    # print("hit location: " + str(hit_location))
    if len(str(hit_location)) == 0:
        hit_location = hit_location * 10
        
    if int(hit_location) in range(0, 15):
        hit = "head"
    elif int(hit_location) in range(16, 35):
        hit = "right arm"
    elif int(hit_location) in range(36, 55):
        hit = "left arm"
    elif int(hit_location) in range(56, 80):
        hit = "body"
    elif int(hit_location) in range(81, 90):
        hit = "right leg"
    elif int(hit_location) in range(91, 101):
        hit = "left leg"
    else:
        hit="Debug"

    # print("Hit: " + hit)
    # --------------------------------
    # END Random Encounter Rebuild
    # --------------------------------

    # if mob_gos > character_gos:
    #     loser = random_character['name'].lower()
    # elif mob_gos == character_gos and mob_gos != -1:
    #     loser = 'Beaten and bloodied they each ran off to fight another day.'
    # else:
    #     loser = encounter_dictionary['name'].lower()
    #     exp, _ = get_user_exp(random_character['name'].lower())
    #     encounter_value += exp
    #     c.execute("update users set exp = ? where uname = ?", (encounter_value, random_character['name'].lower()))
    #     conn.commit()

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
        f'{mob_weapon.lower()} of the {encounter_dictionary["name"].lower()}.' 
    
    if len(loser) > 17:
        chatmessage2 = f'{loser}'
    else:
        if (loser != random_character["name"]):
            loser = "the " + encounter_dictionary["name"]
        lossmessage = [f'{loser.title()} was struck in the {hit} but managed to flee before a fatal blow was landed.',
            f'Someone will need to be digging a grave for {loser} after they lost their {hit}']
        chatmessage2 = choice(lossmessage)
        # f'the fight did not end well for {loser}. {character_roll} vs {mob_roll}'
    
    return chatmessage, chatmessage2

def shop(username, *args):
    from wfrpgame import itemlist
    shoplist = itemlist.load_shop()
    shop_items = []
    shop_message = ''

    if not args:
        shop_message = f"/w {username} Welcome to the shop!  The following commands are necessary for using the shop: " \
            f"(!)shop melee, ranged, or armor will show you the available weapons.  (!)shop buy followed by the item you would " \
            f"like to purchase will allow you to purchase that specific item assuming that you have the available crowns."
    # elif 'melee' in args[0].lower().strip('\r').strip('\n') or 'ranged' in args[0].lower().strip('\r').strip('\n') or 'armor' in args[0].lower().strip('\r').strip('\n'):
    elif args[0].lower().strip('\r\n') == 'melee' or args[0].lower().strip('\r\n') == 'ranged' or args[0].lower().strip('\r\n') == 'armor':
        [shop_items.append(f"[{item}] {shoplist[item]['type']} {shoplist[item]['cost']}") for item in shoplist if args[0].lower().strip('\r\n') in shoplist[item]['type'].lower()]
        shop_items = str(shop_items).replace('[\'', '').replace(
            ']\'', '').replace("', '", " ").replace("']", "")
        shop_message = f"/w {username} The available items are as follows: {shop_items}"
    elif 'buy' in args[0].lower():
        shopper = ret_char(username)
        _, shopper_purse, _ = get_user_exp(username)
        print(len(args))
        if len(args) != 2:
            shop_message = "I'm sorry, I didn't understand that, please try again."
        else:
            new_weapon = args[1].lower().strip('\r\n')
            if new_weapon not in shoplist:
                shop_message = "No item exists that with that name, please look at the (!)shop melee, (!)shop armor or (!)shop ranged list again."
                return

            crown_cost = shoplist[args[1].lower().strip(
                '\r\n')]['cost'].split(' ')
            # print(crown_cost[0], shopper_purse)

            if int(shopper_purse) >= int(crown_cost[0]):
                if shoplist[new_weapon.lower()]['type'] == 'Melee' or shoplist[new_weapon.lower()]['type'] == 'Ranged':
                    shopper['weapon'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?", (int(
                        shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper), username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You brandish your new {args[1]}.  It fits your hands " \
                        f"as though it was made for you."
                elif shoplist[new_weapon.lower()]['type'] == 'Armor':
                    shopper['armor'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?", (int(
                        shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper), username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You don your new {args[1]}.  The armor fits " \
                        f"as though it was made for you."
            else:
                Send_message(f"/w {username} You do not have enough Crowns to buy the {args[1]}. Your current purse is {shopper_purse}.")
                return
    Send_message(shop_message)
    # chatmessage = ''

def level_up(username, stat):
    gchar_dict = None
    if stat.lower().replace('\r\n', '') == 'ws':
        stat = 'weapon_skill'
    elif stat.lower().replace('\r\n', '') == "bs":
        stat = 'ballistic_skill'
    elif stat.lower().replace('\r\n', '') == "t":
        stat = 'toughness'
    elif stat.lower().replace('\r\n', '') == "s":
        stat = 'strength'
    else:
        Send_message(
            f"/w {username} {stat} is an unknown stat.  You may only levelup WS, BS, S, or T.")
        return

    cxp = c.execute("select exp from users where uname = ?",
                    (username,)).fetchone()[0]
    if c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone() != ('',):
        gchar_dict_to_sql = c.execute(
            "select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
        gchar_dict = ast.literal_eval(gchar_dict_to_sql)
    else:
        whisper = f"/w {username} {username}, you do not currently have a character, create one with the !char command."

    if cxp >= 100 and gchar_dict[stat] < 75:
        cxp -= 100
        gchar_dict[stat] += 5
        c.execute("update users set exp = ?, gchar = ? where uname = ?", (cxp, str(gchar_dict), username))
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
host, nick, port, oauth, readbuffer, ClientID, Token = streamr
TLD = ['.com', '.org', '.net', '.int', '.edu', '.gov', '.mil', '.arpa', '.top', '.loan',
       '.xyz', '.club', '.online', '.vip', '.win', '.shop', '.ltd', '.men', '.site',
       '.work', '.stream', '.bid', '.wang', '.app', '.review', '.space', '.ooo',
       '.website', '.live', '.tech', '.life', '.blog', '.download', '.link', '.today',
       '.guru', '.news', '.tokyo', '.london', '.nyc', '.berlin', '.amsterdam', '.hamburg',
       '.boston', '.paris', '.kiwi', '.vegas', '.moscow', '.miami', '.istanbul', '.scot',
       '.melbourne', '.sydney', '.quebec', '.brussels', '.capetown', '.rio', '.tv']

# Set the channel to join for testing purposes:
chan = "rhyle_"
# chan = 'commanderpulsar'

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((host, port))
s.send(bytes('PASS %s\r\n' % oauth, 'UTF-8'))
s.send(bytes('NICK %s\r\n' % nick, 'UTF-8'))
s.send(bytes('CAP REQ :twitch.tv/membership\r\n', 'UTF-8'))
s.send(bytes('CAP REQ :twitch.tv/tags\r\n', 'UTF-8'))
s.send(bytes('CAP REQ :twitch.tv/commands\r\n', 'UTF-8'))
s.send(bytes("JOIN #" + chan + "\r\n", 'UTF-8'))


Running = True
random_character = 'None'
readbuffer = ''
MODT = False
init_mesage = ''
slow = 'off'
Send_message(social_ad(),"")
bot_start = datetime.datetime.now().replace(microsecond=0)
pvp = {}
ad_iter = 0
autoShoutOut = ['rhyle_', 'rhyle_bot']

# Clear Currently playing file
with open('songrequest\\current_song.txt', 'w') as cs:
    cs.write('')
starttime = datetime.datetime.now()

while Running == True:

    readbuffer = s.recv(1024).decode("UTF-8")
    temp = str(readbuffer).split("\n")
    readbuffer = temp.pop()

    # TODO: Get user list
    # TODO: Async
    # TODO: API

    for line in temp:
        # print(line)
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if ("PING :" in line):
            s.send(bytes("PONG\r\n", "UTF-8"))
            currentTime = datetime.datetime.now()
            secondsDelta = currentTime - starttime
            # print(secondsDelta.seconds / 60)
            # print((currentTime - starttime) / 60)
            # if (((currentTime - starttime) / 60) >= 5):
            #     starttime = currentTime
            if ad_iter == 0:
                sm1, sm2 = random_encounter()
                Send_message(sm1)
                Send_message(sm2)
                # random_encounter()
                ad_iter += 1
            elif ad_iter == 1:
                sm1, sm2 = choice([(social_ad(),""), random_encounter()])
                Send_message(sm1)
                Send_message(sm2)
                ad_iter += 1
            elif ad_iter == 2:
                ad_iter = 0
        else:
            # TODO: botbody line 305, split on whitespace -
            # https://trello.com/c/MmwQH2XG/24-botbody-line-305-split-on-whitespace#
            # parts = line.split(" ", 1)
            # print(line)
            parts = line.split(":", 2)

            # for attr in parts:
            #     print(attr)
            # print("Line = " + line)
            # print("Parts index 0 = " + parts[0])
            # print("Parts index 1 = " + parts[1])
            # try:
            #     print("Parts index 2 = " + parts[2])
            # except:
            #     pass
            # try:
            #     print("Parts index 3 = " + parts[3])
            # except:
            #     pass

            # print("Parts = " + str(parts))

            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1] and "PING" not in parts[0]:
                message = None
                try:
                    # Sets the message variable to the actual message sent
                    message = ': '.join(parts[2:])
                    if 'http' in parts[3]:
                        message = ':'.join(parts[3:])
                    else:
                        message = parts[3][:len(parts[3]) - 1]

                except:
                    pass
                    # message = ""

                # print(message)
                # Sets the username variable to the actual username
                init_message = 'init_done'
                usernamesplit = parts[0].split(";")
                # print("Parts[1]: " + parts[1])
                # for i in usernamesplit:
                #     print("username = " + i)

                # TODO: Convert PARTS to a dictionary
                if (len(usernamesplit) > 3):
                    # TODO There is a bug here when someone gets timed out the bot crashes.  Fix it.
                    if 'display-name' in str(usernamesplit[3]):
                        username = usernamesplit[3].split('=')[1].lower()
                    elif 'display-name' in str(usernamesplit[2]):
                        username = usernamesplit[2].split('=')[1].lower()
                    elif 'display-name' in usernamesplit[4]:
                        username = usernamesplit[4].split('=')[1].lower()
                    else:
                        username = "rhyle_bot"
                else:
                    username = ''

                # username = usernamesplit[0]
                chan_name = []
                if "PRIVMSG" in parts[1]:
                    chan_name = (parts[1].split('#'))[1]

                # Only works after twitch is done announcing stuff (MOTD = Message of the day)
                if MODT:
                    # testing for the Ping:Pong crash
                    # print(message)
                    # if username == '':
                    #     print('Ping:Pong')
                    
                    userfetch = c.execute(
                        "select * from users where uname = ?", (username.lower(),)).fetchall()
                    try:
                        user_status = userfetch[0][1]
                    except:
                        user_status = 'user'
                    # print(user_status)
                    if "twitch.tv" not in username:
                        print(username + " (" + user_status + "): " + message)
                    # if username != None:

                    #
                    # The bulk of the processing goes down here!
                    #
                    if message.lower() == '':
                        continue

                    # TODO: Setup some better handling / identification for link handling.
                    # Link detection and timeout
                    # if any(ext in message for ext in TLD):
                    #     print("Line 457: " + str(message))
                    #     # if any(text in 'www .com http' for text in message):
                    #     # print(user_status)
                    #     if username.lower() == nick.lower():
                    #         pass
                    #     elif user_status not in ['broadcaster', 'admins', 'global_mods', 'moderators', 'subs', 'fots', 'vips', 'staff']:
                    #         pass
                    #         # Send_message(username + " links are not currently allowed.")
                    #         # Send_message("/timeout " + username + " 1")

                    # Command processing
                    if username.lower() in commands.get_elevated_users(chan) and username not in autoShoutOut:
                        shoutout = [
                            f"Big shout out to @{username}! Give them some love here and go follow their channel so you can get updates when they go live! (https://www.twitch.tv/{username.lower()})",
                            f"Go check out @{username} they were last streaming {myTwitch.get_raider_id(ClientID, oauth, username)}, check out their channel, if you like what you see toss them a follow. You never know, you may find your new favorite streamer. (https://www.twitch.tv/{username.lower()})",
                            f"A wild {myTwitch.get_raider_id(ClientID, oauth, username)} has appeared, prepare for battle! @{username}, I choose you! (https://www.twitch.tv/{username.lower()})",
                            f"According to @13thfaerie: 'potato' which I think means: go check out @{username}, last streaming: {myTwitch.get_raider_id(ClientID, oauth, username)}. (https://www.twitch.tv/{username.lower()})"]
                        Send_message(choice(shoutout))
                        autoShoutOut.append(username)
                                

                    if message[0] == '!':
                        
                        # REFACTORING EVERYTHING AFTER THIS LINE OUT OF BOT_BODY!
                        # 
                        # commands.commands(username, message)

                        if username != '':
                            # TODO: Mod, Broadcaster, FOTS, VIP Commands.
                            
                            # Broadcaster
                            if username.lower() in ['rhyle_']:
                                if '!goaway' in message.lower():
                                    Send_message("Shutting down now.")
                                    Running = False
                                if message[0:8].lower() == '!adduser':
                                    command, new_user, user_type = message.split(
                                        ' ')
                                    c.execute("insert into users values (:user , :status)", {'user': new_user.lower(), 'status': user_type})
                                    conn.commit()
                                elif message[0:8].lower() == '!deluser':
                                    command, new_user = message.split(' ')
                                    c.execute(
                                        "delete from users where uname = ?", (new_user.lower(),))
                                    conn.commit()
                                elif message[0:8].lower() == '!upduser':
                                    command, new_user, user_type = message.replace(
                                        '\r', '').split(' ')
                                    c.execute("""update users
                                            set status = ?
                                            where uname = ?""", (user_type, new_user.lower(),))
                                    conn.commit()
                                elif message.lower() == "!slow":
                                    if slow == "off":
                                        Send_message(
                                            "Engaging Slow Chat Mode...")
                                        print("Engaging Slow Chat Mode...")
                                        s.send(("PRIVMSG #" + chan +
                                                " :.slow\r\n").encode('UTF-8'))
                                        slow = 'on'
                                        continue
                                    if slow == 'on':
                                        Send_message(
                                            "Disengaging Slow Chat Mode...")
                                        print("Disengaging Slow Chat Mode...")
                                        s.send(
                                            ("PRIVMSG #" + chan + " :.slowoff\r\n").encode('UTF-8'))
                                        slow = 'off'
                                        continue
                                elif '!raiderinfo ' in message:
                                    chatmessage, username = message.replace('\r', '').split(' ')
                                    print(myTwitch.get_raider_id(ClientID, oauth, username))
                                elif '!raid ' in message and len(message)>7:
                                    chatmessage, username = message.split(" ")
                                    chatmessage = c.execute("select action from commands where ex_command = ?",(chatmessage.strip(''),)).fetchone()[0]
                                    Send_message(chatmessage, username)
                                    chatmessage = c.execute("select action from commands where ex_command = '!calls'").fetchone()[0]
                                    Send_message(chatmessage, username)
                                    continue
                                elif '!raidcall' in message:
                                    chatmessage = message.strip('\r')
                                    if " " in chatmessage:
                                        chatmessage, username = chatmessage.split(" ")
                                        
                                    print(chatmessage)
                                    chatmessage = c.execute("select action from commands where ex_command = ?", (chatmessage,)).fetchone()[0]
                                    Send_message(chatmessage, username)
                                    continue
                                elif '!join' in message.lower():
                                    ex_com, channel = message.split(' ')
                                    s.send(
                                        bytes("JOIN #" + channel.lower() + "\r\n", 'UTF-8'))
                                    time.sleep(1)
                                    s.send(
                                        ("PRIVMSG #" + channel.lower() + " :Just testing, don't Hz me\r\n").encode('UTF-8'))
                                elif '!part' in message.lower():
                                    ex_com, channel = message.split(' ')
                                    message = "Fine, I'm leaving."
                                    time.sleep(1)
                                    s.send(
                                        ("PRIVMSG #" + channel.lower() + " :Fine, I'm leaving.\r\n").encode('UTF-8'))
                                    s.send(
                                        bytes("PART #" + channel.lower() + "\r\n", 'UTF-8'))
                                elif '!lt3 ' in message.lower():
                                    ex_com, user = message.replace('\r', '').split(' ')
                                    if ('@' in user):
                                        user = user.replace("@", "")
                                    lessthan3 = [
                                        f'You really should go check out {user} sometime (https://www.twitch.tv/{user.lower()}). They are a member of the Less than 3 streaming community and one of the streamers that I enjoy watching.',
                                        f'Ooh, look its {user}! Show them some love and kindness in the chat! Also check out their page at (https://www.twitch.tv/{user.lower()})'
                                    ]
                                    Send_message(choice(lessthan3))
                                elif '!st ' in message.lower():
                                    ex_com, tweet = message.split(' ', 1)
                                    if len(tweet) <= 280:
                                        print(tweet)
                                        twitter.send_tweet(tweet)
                                    else:
                                        Send_message(
                                            "Sorry boss, that tweet is too long.")
                                elif '!title ' in message.lower():
                                    ex_com, update_info = message.split(' ', 1)
                                    # "select * from users where uname = ?", (username.lower(),)).fetchall()
                                    myTwitch.update_twitch(ClientID, oauth, update_info)
                                elif '!beanlist' in message.lower():
                                    try:
                                        ex_com, poopie_head, bean = message.split(' ')
                                    except:
                                        with open(r"F:\Google Drive\Stream Assets\Bean list.txt", "r") as bean_list:
                                            lines = bean_list.readlines()
                                            for line in lines:
                                                print(line)
                                    try:
                                        poopie_head = poopie_head.replace("@","")
                                        with open (r"F:\Google Drive\Stream Assets\Bean list.txt", "a") as bean_list:
                                            bean_list.write(f'\n{poopie_head}: {bean}')
                                    except:
                                        pass
                                elif message[0:7].lower() == '!create':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(
                                        ', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("insert into commands values (:command, :target, :action)",
                                              {'command': command, 'target': target, 'action': action})
                                    conn.commit()
                                    Send_message(
                                        "Command " + command + " has been added.")
                                elif message[0:7].lower() == '!update':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(
                                        ', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("update commands set action = :action where ex_command = :command", {'command': command, 'target': target, 'action': action.lstrip(' ')})
                                    conn.commit()
                                    Send_message(
                                        "Command " + command + " has been updated.")
                                elif message[0:7].lower() == '!remove':
                                    # Parse the command to be removed
                                    ex_com, command = message.split(' ')
                                    command = '!' + command
                                    c.execute(
                                        "delete from commands where ex_command = ?", (command,))
                                    conn.commit()
                                    Send_message(
                                        "Command " + command + " has been removed.")
                                elif message[0:4].lower() == '!mtc':
                                    # no longer give credit to the other streamers.
                                    parts = message.split(' ')
                                    ex_com, strm1, strm2, strm3, strm4 = [
                                        parts[i] if i < len(parts) else None for i in range(5)]
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
                                        Send_message(
                                            "Engaging Slow Chat Mode...")
                                        print("Engaging Slow Chat Mode...")
                                        s.send(("PRIVMSG #" + chan +
                                                " :.slow\r\n").encode('UTF-8'))
                                        slow = 'on'
                                        continue
                                    if slow == 'on':
                                        Send_message(
                                            "Disengaging Slow Chat Mode...")
                                        print("Disengaging Slow Chat Mode...")
                                        s.send(
                                            ("PRIVMSG #" + chan + " :.slowoff\r\n").encode('UTF-8'))
                                        slow = 'off'
                                        continue
                                elif '!so ' in message.lower():
                                    ex_com, user = message.replace('\r', '').split(' ')
                                    if ('@' in user):
                                        user = user.replace("@", "")
                                    shoutout = [
                                        f"Big shout out to {user}! Give them some love here and go follow their channel so you can get updates when they go live! (https://www.twitch.tv/{user.lower()})",
                                        f"Go check out {user} they were last streaming {myTwitch.get_raider_id(ClientID, oauth, user)}, check out their channel, if you like what you see toss them a follow. You never know, you may find your new favorite streamer. (https://www.twitch.tv/{user.lower()})",
                                        f"A wild {myTwitch.get_raider_id(ClientID, oauth, user)} has appeared, prepare for battle! {user}, I choose you! (https://www.twitch.tv/{user.lower()})",
                                        f"According to @13thfaerie: 'potato' which I think means: go check out {user}, last streaming: {myTwitch.get_raider_id(ClientID, oauth, user)}. (https://www.twitch.tv/{user.lower()})"]
                                    Send_message(choice(shoutout))
                                elif '!randomenc' in message.lower():
                                    try:
                                        ex_com, user = message.lower().split(' ')
                                        if ('@' in user):
                                            user = user.replace("@","")
                                        sm1, sm2 = random_encounter(user)
                                        Send_message(sm1)
                                        Send_message(sm2)
                                    except:
                                        sm1, sm2 = random_encounter()
                                        Send_message(sm1)
                                        Send_message(sm2)
                                    continue
                                elif "!givecrowns" in message:
                                    ex_com, viewer, amount = message.split(' ')
                                    if '@' in viewer:
                                        viewer = viewer.strip('@')
                                    gc_user = int(c.execute(
                                        "select crowns from users where uname = ?", (viewer.lower(),)).fetchone()[0])
                                    gc_user += int(amount)
                                    c.execute(
                                        "update users set crowns = ? where uname = ?", (gc_user, viewer.lower()))
                                    conn.commit()
                                    Send_message(f"{viewer} was awarded {amount} crowns.")
                                elif '!givexp' in message.lower():
                                    parts = message.split(' ', 3)
                                    parts += '' * (3 - len(parts))
                                    ex_com, viewer, amount = parts
                                    if '@' in viewer:
                                        viewer = viewer.strip("@")
                                    print(viewer)
                                    rew_user = int(c.execute("select exp from users where uname = ?", (viewer.lower(),)).fetchone()[0])
                                    
                                    rew_user += int(amount)
                                    
                                    c.execute(
                                        "update users set exp = ? where uname = ?", (rew_user, viewer.lower()))
                                    conn.commit()
                                    Send_message(f"Added {amount} xp to {viewer}.")
                                elif '!rt' in message.lower():
                                    Send_message(f'Click this link to retweet https://twitter.com/intent/retweet?tweet_id={twitter.get_retweet()}')
                                elif '!mtc' in message.lower():
                                    parts = message.split(' ')
                                    ex_com, strm1, strm2, strm3, strm4 = [
                                        parts[i] if i < len(parts) else None for i in range(5)]
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
                                elif '!ded' in message.lower():
                                    with open(r"F:\Google Drive\Stream Assets\EQCounter.txt", "r+") as cfile:
                                        lines = cfile.readlines()
                                        cfile.seek(0)
                                        cfile.truncate()
                                        for line in lines:
                                            if "Death Counter:" in line:
                                                you_died = line.split(": ")
                                                you_died = int(you_died[1])
                                                you_died += 1
                                                line = f"Death Counter: {you_died}"
                                            cfile.write(line)
                                elif '!reset' in message.lower():
                                    parts = message.split(' ')
                                    ex_com, person_to_reset = parts
                                    reset_character = str(tcChargen.base_char(person_to_reset.strip('\r')).__dict__)
                                    person_to_reset = person_to_reset.strip('\r')
                                    # c.execute('update users set gchar = ? where uname = ?',(gchar, character['name']))
                                    # conn.commit()
                                    c.execute(
                                        'update users set gchar = ?, wins = 0 where uname = ?',(reset_character, person_to_reset)
                                    )
                                    conn.commit()
                                    # c.execute(
                                    #     "update users set wins = 0 where wins > 0"
                                    # )
                                    # conn.commit()
                                    # Send_message('The leaderboard has been RESET')
                                elif '!eom' in message.lower():
                                    for user in c.execute("select * from users where status = 'viewer'").fetchall():
                                        # print(user[0])
                                        update_user = str(tcChargen.base_char(user[0]))
                                        c.execute(
                                            'update users set gchar = ?, wins = 0 where uname = ?',(update_user, user[0])
                                        )
                                    conn.commit()

                            elif username.lower() in get_elevated_users(chan):
                                if message[0:7].lower() == '!create':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(
                                        ', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("insert into commands values (:command, :target, :action)",
                                              {'command': command, 'target': target, 'action': action})
                                    conn.commit()
                                    Send_message(
                                        "Command " + command + " has been added.")
                                elif message[0:7].lower() == '!update':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(
                                        ', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("update commands set action = :action where ex_command = :command", {'command': command, 'target': target, 'action': action.lstrip(' ')})
                                    conn.commit()
                                    Send_message(
                                        "Command " + command + " has been updated.")
                                elif message[0:7].lower() == '!remove':
                                    # Parse the command to be removed
                                    ex_com, command = message.split(' ')
                                    command = '!' + command
                                    c.execute(
                                        "delete from commands where ex_command = ?", (command,))
                                    conn.commit()
                                    Send_message(
                                        "Command " + command + " has been removed.")
                                elif message[0:4].lower() == '!mtc':
                                    # no longer give credit to the other streamers.
                                    parts = message.split(' ')
                                    ex_com, strm1, strm2, strm3, strm4 = [
                                        parts[i] if i < len(parts) else None for i in range(5)]
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
                                        Send_message(
                                            "Engaging Slow Chat Mode...")
                                        print("Engaging Slow Chat Mode...")
                                        s.send(("PRIVMSG #" + chan +
                                                " :.slow\r\n").encode('UTF-8'))
                                        slow = 'on'
                                        continue
                                    if slow == 'on':
                                        Send_message(
                                            "Disengaging Slow Chat Mode...")
                                        print("Disengaging Slow Chat Mode...")
                                        s.send(
                                            ("PRIVMSG #" + chan + " :.slowoff\r\n").encode('UTF-8'))
                                        slow = 'off'
                                        continue
                                elif '!so ' in message.lower():
                                    ex_com, user = message.replace('\r', '').split(' ')
                                    if ('@' in user):
                                        user = user.replace("@", "")
                                    shoutout = [
                                        f"Big shout out to {user}! Give them some love here and go follow their channel so you can get updates when they go live! (https://www.twitch.tv/{user.lower()})",
                                        f"Go check out {user} they were last streaming {myTwitch.get_raider_id(ClientID, oauth, user)}, check out their channel, if you like what you see toss them a follow. You never know, you may find your new favorite streamer. (https://www.twitch.tv/{user.lower()})",
                                        f"A wild {myTwitch.get_raider_id(ClientID, oauth, user)} has appeared, prepare for battle! {user}, I choose you! (https://www.twitch.tv/{user.lower()})",
                                        f"According to @13thfaerie: 'potato' which I think means: go check out {user}, last streaming: {myTwitch.get_raider_id(ClientID, oauth, user)}. (https://www.twitch.tv/{user.lower()})"]
                                    Send_message(choice(shoutout))
                                elif '!randomenc' in message.lower():
                                    try:
                                        ex_com, user = message.lower().split(' ')
                                        sm1, sm2 = random_encounter(user)
                                        Send_message(sm1)
                                        Send_message(sm2)
                                    except:
                                        sm1, sm2 = random_encounter()
                                        Send_message(sm1)
                                        Send_message(sm2)
                                    continue
                                elif "!givecrowns" in message:
                                    ex_com, viewer, amount = message.split(' ')
                                    if '@' in viewer:
                                        viewer = viewer.strip('@')
                                    gc_user = int(c.execute(
                                        "select crowns from users where uname = ?", (viewer.lower(),)).fetchone()[0])
                                    gc_user += int(amount)
                                    c.execute(
                                        "update users set crowns = ? where uname = ?", (gc_user, viewer.lower()))
                                    conn.commit()
                                    Send_message(f"{viewer} was awarded {amount} crowns.")
                                elif '!givexp' in message.lower():
                                    parts = message.split(' ', 3)
                                    parts += '' * (3 - len(parts))
                                    ex_com, viewer, amount = parts
                                    if '@' in viewer:
                                        viewer = viewer.strip("@")
                                    print(viewer)
                                    rew_user = int(c.execute("select exp from users where uname = ?", (viewer.lower(),)).fetchone()[0])
                                    
                                    rew_user += int(amount)
                                    
                                    c.execute(
                                        "update users set exp = ? where uname = ?", (rew_user, viewer.lower()))
                                    conn.commit()
                                    Send_message(f"Added {amount} xp to {viewer}.")
                                elif '!rt' in message.lower():
                                    Send_message(f'Click this link to retweet https://twitter.com/intent/retweet?tweet_id={twitter.get_retweet()}')
                                elif '!mtc' in message.lower():
                                    parts = message.split(' ')
                                    ex_com, strm1, strm2, strm3, strm4 = [
                                        parts[i] if i < len(parts) else None for i in range(5)]
                                    command = '!multi'
                                    target = ''
                                    if strm3 == None:
                                        multi = strm1 + '/' + strm2
                                    elif strm4 == None:
                                        multi = strm1 + '/' + strm2 + '/' + strm3
                                    else:
                                        multi = strm1 + '/' + strm2 + '/' + strm3 + '/' + strm4

                                    action = "Access the multitwitch at http://multitwitch.tv/" + multi + " "                                              "or you can access kadgar at http://kadgar.net/live/" + multi

                                    if c.execute("select * from commands where ex_command = '!multi'").fetchall() != []:
                                        c.execute("update commands set action = :action where ex_command = :command",
                                                {'command': command, 'action': action})
                                        conn.commit()
                                    else:
                                        c.execute("insert into commands values (:command, :target, :action)",
                                                {'command': command, 'target': target, 'action': action})
                                        conn.commit()
                                    Send_message(action)
                                elif '!ded' in message.lower():
                                    with open(r"F:\Google Drive\Stream Assets\EQCounter.txt", "r+") as cfile:
                                        lines = cfile.readlines()
                                        cfile.seek(0)
                                        cfile.truncate()
                                        for line in lines:
                                            if "Death Counter:" in line:
                                                you_died = line.split(": ")
                                                you_died = int(you_died[1])
                                                you_died += 1
                                                line = f"Death Counter: {you_died}"
                                            cfile.write(line)
                                        

                            if message[:3].lower() not in ('!de','!be', '!gi','!rt', '!ra', '!hl', '!up', '!de', '!ad', '!go', '!up', '!gu', '!sl', '!mt', '!vi', '!so', '!st'):
                                chatmessage = message.strip().lower()
                                if '!lurk' in message.lower():
                                    lurk_message = [
                                        f"It looks like we've lost {username} to the twitch void. Hopefully they will find their way back soon!",
                                        f"Seems like {username} has gone off to take care of.... business.",
                                        f"{username} has been eliminated by IOI-655321",
                                        f"{username.title()} left for the greater unknown",
                                        f"{username.upper()} DID YOU PUT YOUR NAME IN THE CHALICE OF BURNING?",
                                        f"{username.title()} when someone asks if you're a god you say yes."
                                    ]
                                    chatmessage = choice(lurk_message)
                                elif "!ban" in message.lower():
                                    chatmessage = "It looks like " + username + " no longer thinks they can be a " \
                                        "productive member of the community and has requested to be banned."
                                    Send_message("/ban " + username + " Self exile")
                                    Send_message("/unban " + username)
                                elif "!change" in message.lower():
                                    try:
                                        ex_com, race = message.strip('\r').split(" ")
                                        change_char = ret_char(username)
                                        cxp = int(
                                            c.execute('select exp from users where uname = ?', (username,)).fetchone()[0])
                                        if cxp < 100:
                                            chatmessage = f"Sorry {username}, you do not have enough accrued exp to" \
                                                f" change your race at the moment, please try again later {cxp}/100."
                                        elif race.lower() not in ['human', 'elf', 'halfling', 'dwarf']:
                                            chatmessage = f'Sorry {username}, you must choose one of the 4 standard WFRP' \
                                                f' races: Human, Elf, Dwarf, Halfling. Please try again.'
                                        elif race.lower() == 'human' and change_char['race'] != 'human':
                                            change_char['race'] = 'human'
                                            change_race(
                                                username, str(change_char))
                                            chatmessage = f'{username} you race has been changed to {race}'
                                        elif race.lower() == 'elf' and change_char['race'] != 'elf':
                                            change_char['race'] = 'elf'
                                            change_race(
                                                username, str(change_char))
                                            chatmessage = f'{username} your race has been changed to {race}'
                                        elif race.lower() == 'halfling' and change_char['race'] != 'halfling':
                                            change_char['race'] = 'halfling'
                                            change_race(
                                                username, str(change_char))
                                            chatmessage = f'{username} your race has been changed to {race}'
                                        elif race.lower() == 'dwarf' and change_char['race'] != 'dwarf':
                                            change_char['race'] = 'dwarf'
                                            change_race(
                                                username, str(change_char))
                                            chatmessage = f'{username} your race has been changed to {race}'
                                    except:
                                        chatmessage = f'Sorry {username}, you must choose one of the 4 standard WFRP' \
                                            f' races: Human, Elf, Dwarf, Halfling.'
                                elif "!char" in message.lower():
                                    # test if user in database
                                    try:
                                        user = c.execute("select * from users where uname = ?", (username.lower(),))
                                    except:
                                        c.execute(
                                            """insert into users values (?, ?, 0, '', 0)""", (username.lower(), 'viewer'))
                                        conn.commit()
                                        print(
                                            f"user {username} has been added to the database")
                                    finally:
                                        print(username.lower())
                                        if (c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone() != ('',)):
                                            gchar_dict_to_sql = c.execute(
                                                "select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
                                            gchar_dict = ast.literal_eval(
                                                gchar_dict_to_sql)

                                            cxp, crowns = c.execute(
                                                "select exp, crowns from users where uname = ?", (username,)).fetchone()
                                            # print(gchar_dict)
                                            article = 'a '
                                            if gchar_dict['race'] == 'elf':
                                                gchar_dict['race'] = 'elven'
                                                article = 'an '
                                            elif gchar_dict['race'] == 'dwarf':
                                                gchar_dict['race'] = 'dwarven'
                                            else:
                                                chat_race = gchar_dict['race']

                                            if gchar_dict['prof'] == 'peasant':
                                                build_whisper = f"{username} {username} is {article}" \
                                                    f"{str(gchar_dict['race']).capitalize()} " \
                                                    f"{gchar_dict['prof']} Weapon Skill: {gchar_dict['weapon_skill']} " \
                                                    f"Ballistic Skill: {gchar_dict['ballistic_skill']} Strength: " \
                                                    f"{gchar_dict['strength']} Toughness: {gchar_dict['toughness']} " \
                                                    f"This is a generic assigned character.  You can !permadeath and then !char " \
                                                    f"in order to get one that is not a Human Peasant." \
                                                    f"Current available Exp: {cxp} Crown Purse: {crowns}" \

                                                Send_message(
                                                    f"/w {build_whisper}")
                                            else:
                                                build_whisper = f"{username} {username} is {article}" \
                                                    f"{str(gchar_dict['race']).capitalize()} " \
                                                    f"{gchar_dict['prof']} Weapon Skill: {gchar_dict['weapon_skill']} " \
                                                    f"Ballistic Skill: {gchar_dict['ballistic_skill']} Strength: " \
                                                    f"{gchar_dict['strength']} Toughness: {gchar_dict['toughness']} " \
                                                    f" You are currently using your " \
                                                    f"{str(gchar_dict['weapon']).capitalize()} as a weapon and " \
                                                    f"{str(gchar_dict['armor']).capitalize()} for armor. If you would like to" \
                                                    f" upgrade either you can (!)shop to spend your crowns to purchase new weapons" \
                                                    f" and armor.  Current available Exp: {cxp} Crown Purse: {crowns}"

                                                Send_message(
                                                    f"/w {build_whisper}")
                                            chatmessage = ""

                                        else:
                                            # Generate character using the Character Class
                                            gchar = tcChargen.chat_char(
                                                username)

                                            # Converts the Class to a dictionary
                                            gchar_dict = gchar.get_char(
                                                username)

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

                                            cxp = c.execute(
                                                "select exp from users where uname = ?", (username,)).fetchone()[0]

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
                                                f" upgrade either you can (!)shop to spend your crowns to purchase new weapons" \
                                                f" and armor.  Current available Exp: {cxp}"

                                            Send_message(f"/w {build_whisper}")
                                elif "!retire" in message.lower():
                                    # TODO: Retired characters should output to HTML and be stored on a webserver.
                                    # TODO: should also provide link for download in whisper.
                                    chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                        "moment, please check back soon(tm)."
                                elif "!permadeath" in message.lower():
                                    try:
                                        c.execute(
                                            "update users set gchar = '' where uname = ?", (username.lower(),))
                                        conn.commit()
                                        chatmessage = username + " has chosen to permanently kill off their " \
                                            "character. You may issue the !char command to create a new one."

                                    except:
                                        chatmessage = "Hello " + username + ", this command is being worked on at the " \
                                            "moment, please check back soon(tm)."
                                elif message[0:11].lower() == "!challenge ":
                                    amount = None
                                    try:
                                        ex_com, target, amount = message.split(
                                            ' ')
                                        target = target.lower()
                                        if '@' in target:
                                            target = target.replace('@', '')
                                    except ValueError:
                                        Send_message(f'Blast! {username} the proper command is !challenge >target< >risk amount<')
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
                                        pvp[(f'{username.lower()}', f'{time.time()}')] = (
                                            f'{target.lower()}', amount)
                                elif "!accept" in message.lower():
                                    for challenger, victim in pvp.items():
                                        if victim[0] == username:
                                            chall = ret_char(challenger[0])
                                            vic = ret_char(victim[0])

                                            Send_message(f"{str(chall['name']).capitalize()}, {str(vic['name']).capitalize()} has accepted your challenge.  Prepare for combat!")
                                            time.sleep(1)
                                            victim_random = randint(2, 100)
                                            vic_roll = (
                                                vic['weapon_skill'] + victim_random) - chall['toughness']
                                            if vic_roll < 0:
                                                vic_roll = 0
                                            Send_message(f"{victim[0]} hits {challenger[0]} with their {vic['weapon']} (({vic['weapon_skill']} + {victim_random})-{chall['toughness']}) ({vic_roll})")
                                            time.sleep(1)
                                            challenger_random = randint(2, 100)
                                            chall_roll = (
                                                chall['weapon_skill'] + challenger_random) - vic['toughness']
                                            if chall_roll < 0:
                                                chall_roll = 0
                                            Send_message(f"{challenger[0]} returns the blow with their {chall['weapon']} (({chall['weapon_skill']} + {challenger_random}) - {vic['toughness']}) ({chall_roll})")
                                            time.sleep(1)

                                            if vic_roll > chall_roll:
                                                Send_message(f'{victim[0]} has defeated their challenger {challenger[0]} and earned! {amount} exp.')
                                                challenge_result(
                                                    victim[0], amount, challenger[0])
                                            elif vic_roll == chall_roll:
                                                Send_message(
                                                    f'After a bloody fight {victim[0]} and {challenger[0]} call it a draw!')
                                            else:
                                                Send_message(f'{challenger[0]} has bested his victim, {victim[0]}, earning themselves {amount}')
                                                challenge_result(
                                                    challenger[0], amount)
                                            chatmessage = ""
                                        else:
                                            chatmessage = f"There is not currently a pending challenge for {username}"
                                    del pvp[challenger]
                                elif '!decline' in message.lower():
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
                                elif message.lower() == "!uptime":
                                    timenow = datetime.datetime.now().replace(microsecond=0)

                                    chatmessage = f'Rhyle_Bot has been running for {str(uptime(timenow))}, this is not ' \
                                        f'stream uptime.'
                                elif "!levelup" in message.lower().replace('\r\n', ''):
                                    chatmessage = ''
                                    if len(message) <= 9:
                                        chatmessage = "The proper command for this includes one of the " \
                                            "four character stats: WS, BS, S, T."
                                    else:
                                        ex_com, stat = message.strip(
                                            '\r').split(' ')
                                        level_up(username, stat)
                                elif "!shop" in message.lower().strip('\r'):
                                    if len(message) == 5:
                                        shop(username)
                                    else:
                                        ex_com, *arg = message.strip('\r').split(' ')
                                        shop(username, *arg)
                                    chatmessage = ""
                                elif "!sr" in message.lower():
                                    chatmessage = f"I'm sorry, {username}, song requests have been turned off indefinitely."
                                    # if len(message) < 3:
                                    #     chatmessage = "To use the song request feature either provide the 11 character video code or the full address to the youtube video."
                                    # else:
                                    #     command, code = message.split(" ")
                                    #     # song_request.sr(code)
                                    #     playlist_maker.add_to_playlist(code)
                                    #     chatmessage = ""
                                else:
                                    try:
                                        chatmessage = c.execute("select action from commands where ex_command = ?",
                                                                (chatmessage.strip(''),)).fetchone()[0]
                                    except:
                                        chatmessage = f'/w {username} Hello {username} there is not currently a {message} command. ' \
                                            f'If you would like to have one created, let me know. Subs take precedence for !commands.'
                                        # print(f'504: {chatmessage}')

                                # send the assembled chatmessage variable
                                try:
                                    Send_message(chatmessage, username)
                                except:
                                    print(f'1026: {chatmessage}')

                            # Gunter command
                            elif message[0:7].lower() == '!gunter':
                                commandlist = list(
                                    c.execute("select ex_command from commands"))
                                for itr in range(len(commandlist)):
                                    commandlist[itr] = commandlist[itr][0]
                                for item in ["!lurk", "!ban", "!change", "!char", "!retire", "!permadeath", "!challenge", "!uptime", "!levelup", "!shop", "!gunter"]:
                                    commandlist.append(item)
                                Send_message(
                                    "You've found the (not so) hidden command list " +
                                    username + ". Command list: "
                                    + ', '.join(commandlist))
                            else:
                                pass
                                # print(f'846: {username}, {message}')
                                # print(chatmessage)
                                # Send_message(f'Hello {username} there is not currently a {message} command. ' \
                                #             f'If you would like to have one created, let me know. Subs take precedence for !commands.')
                    #
                    # End of bot processing
                    #

                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True
