from logging import FATAL
from random import randint, choice
import socket
import json
from urllib import request
import datetime
import time
import ast

import loader
from anyascii import anyascii
from wfrpgame import tcChargen, game_manager, character_manager
from utils import twitter, commands, quotes, soundcommands, deathcounter, excuse
from chattodb import social_ad, get_active_list
import myTwitch
# import wfrpgame
# import song_request
# import playlist_maker

# Set deathcounter off at init.
death_counter = False

# Method for sending a message
def Send_message(message, *args):
    time.sleep(1)


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
        try:
            s.send(("PRIVMSG #" + chan + " :" + message + "\r\n").encode('UTF-8'))
        except ConnectionResetError:
            print("there was a connection reset error")
    else:
        s.send(("PRIVMSG #" + args[0] + " :" +
                message + "\r\n").encode('UTF-8'))

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

def shop(username, *args):
    from wfrpgame import itemlist
    shoplist = itemlist.load_shop()
    shop_items_list = []
    shop_message = ''

    if not args:
        shop_message = f"/w {username} Welcome to the shop!  The following commands are necessary for using the shop: " \
            f"(!)shop melee, ranged, armor, or healing will show you the available equipment.  (!)shop buy followed by the item you would " \
            f"like to purchase will allow you to purchase that specific item assuming that you have the available crowns."
    # elif 'melee' in args[0].lower().strip('\r').strip('\n') or 'ranged' in args[0].lower().strip('\r').strip('\n') or 'armor' in args[0].lower().strip('\r').strip('\n'):
    elif args[0].lower().strip('\r\n') == 'melee' or args[0].lower().strip('\r\n') == 'ranged' or args[0].lower().strip('\r\n') == 'armor' or args[0].lower().strip('\r\n') == 'healing':
        [shop_items_list.append(f"[{item}]: {shoplist[item]['cost']}") for item in shoplist if args[0].lower().strip('\r\n') in shoplist[item]['type'].lower()]
        shop_items = ' || '.join(shop_items_list)
        shop_message = f"/w {username} The available items are as follows: {shop_items}"

    elif 'buy' in args[0].lower():
        shopper = ret_char(username)
        _, shopper_purse, _ = game_manager.get_user_exp(c, username)

        if len(args) != 2:
            shop_message = "I'm sorry, I didn't understand that, please try again."
        else:
            new_item = args[1].lower().strip('\r\n')
            if new_item not in shoplist:
                shop_message = "No item exists that with that name, please look at the (!)shop melee, (!)shop armor or (!)shop ranged list again."
                return

            crown_cost = shoplist[args[1].lower().strip('\r\n')]['cost'].split(' ')
            
            if int(shopper_purse) >= int(crown_cost[0]):
                # Item can be purchased
                if shoplist[new_item.lower()]['type'] == 'Melee' or shoplist[new_item.lower()]['type'] == 'Ranged':
                    shopper['weapon'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?", (int(
                        shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper), username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You brandish your new {args[1]}.  It fits your hands " \
                        f"as though it was made for you."

                elif shoplist[new_item.lower()]['type'] == 'Armor':
                    shopper['armor'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?", (int(
                        shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper), username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You don your new {args[1]}.  The armor fits " \
                        f"as though it was made for you."
                
                elif shoplist[new_item.lower()]['type'] == 'Healing':
                    # Get Current and Max wounds
                    (current_wounds, max_wounds) = c.execute("select CurrentWounds, MaxWounds from users where uname = ?", (username,)).fetchone()
                    # print(shoplist[new_item.lower()]['damage'])
                    # Add potions healing to current wounds up to Max Wounds.
                    if current_wounds + int(shoplist[new_item.lower()]['damage'].split(' ')[0]) >= max_wounds:
                        current_wounds = max_wounds
                    else:
                        current_wounds += int(shoplist[new_item.lower()]['damage'].split(' ')[0])
                    
                    # Charge the purse
                    c.execute("update users set crowns = ? where uname = ?", (int(
                        shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper), username))
                    c.execute('update users set CurrentWounds = ? where uname = ?', (current_wounds, username))
                    conn.commit()
                    shop_message = f"/w {username} You quaff down the {args[1]}, you begin to feel much better. ({current_wounds}/{max_wounds}) "
                        
            else:
                # Charge NSF Fee.
                Send_message(f"/w {username} You do not have enough Crowns to buy the {args[1]}. Your current purse is {shopper_purse}.")
                return
    Send_message(shop_message)
    # chatmessage = ''

def retire(uname):
    if c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone() != ('',):
        # Is a character
        gchar_dict_to_sql = c.execute(
            "select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
        # converts the string to dictionary
        gchar_dict = ast.literal_eval(gchar_dict_to_sql)
    else:
        whisper = f"/w {username} {username}, you do not currently have a character, create one with the !char command."
    
    with open ('wfrpgame/character_template.html', 'r') as ct:
        template = ct.readlines()

    template = str(template).replace("$character", str(gchar_dict['name']).title())
    template = str(template).replace("$species", str(gchar_dict['race']).title())
    template = str(template).replace("$profession", str(gchar_dict['prof']).title())
    template = str(template).replace("$ws", str(gchar_dict['weapon_skill']))
    template = str(template).replace("$bs",str(gchar_dict['ballistic_skill']))
    template = str(template).replace("$s", str(gchar_dict['strength']))
    template = str(template).replace("$t", str(gchar_dict['toughness']))
    with open(f'wfrpgame/{uname}.html', 'w') as rc:
        rc.writelines(template)
        pass


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
    elif stat.lower().replace('\r\n', '') == "wound":
        stat = 'wound'
    else:
        Send_message(
            f"/w {username} {stat} is an unknown stat.  You may only levelup WS, BS, S, T or Wound.")
        return

    # Get users current XP
    cxp = c.execute("select exp from users where uname = ?",
                    (username,)).fetchone()[0]
    
    
    if c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone() != ('',):
        # Is a character
        gchar_dict_to_sql = c.execute(
            "select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
        # converts the string to dictionary
        gchar_dict = ast.literal_eval(gchar_dict_to_sql)
        # Get the Wounds characteristc
        char_wounds = c.execute(
            "select MaxWounds from users where uname = ?", (username.lower(),)).fetchone()[0]
    else:
        whisper = f"/w {username} {username}, you do not currently have a character, create one with the !char command."

    if stat.lower() != "wound":
        if cxp >= 100 and gchar_dict[stat] < 75:
            # Test if the user has more than 100 xp and less that 75 is specific characteristic
            cxp -= 100
            gchar_dict[stat] += 5
            c.execute("update users set exp = ?, gchar = ? where uname = ?", (cxp, str(gchar_dict), username))
            conn.commit()
            whisper = f"/w {username} Your {stat} has been increased by 5 points to {gchar_dict[stat]}"

        elif gchar_dict[stat] >= 75:
            # If stat is already over 75.
            whisper = f"/w {username} Your {stat} has is already maxed out."
        elif cxp < 100:
            # if Current xp is not sufficient.
            whisper = f"/w {username} Sorry {username} you do not currently have enough experience to " \
                f"upgrade your character.  Current EXP: {cxp}"
    elif stat.lower() == "wound":
        if cxp >= 100 and char_wounds < 20:
            cxp -= 100
            char_wounds += 1
            c.execute("update users set exp = ?, MaxWounds = ? where uname = ?", (cxp, str(char_wounds), username))
            conn.commit()
            whisper = f"/w {username} Your wounds have been increased by 1 point to {char_wounds}"
        else:
            whisper = f"/w {username} It looks like you either don't have enough experience or you're already capped out on wounds!"
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
# with open('songrequest\\current_song.txt', 'w') as cs:
#     cs.write('')
# starttime = datetime.datetime.now()

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
            
            # print(secondsDelta.seconds / 60)
            # print((currentTime - starttime) / 60)
            # if (((currentTime - starttime) / 60) >= 5):
            #     starttime = currentTime
            if ad_iter == 0:
                user, sm3 = game_manager.random_encounter(c, conn)
                if sm3:
                    Send_message(f"/w {user} {sm3}")
                # Send_message(sm1)
                # Send_message(sm2)
                # random_encounter()
                ad_iter += 1
            elif ad_iter == 1:
                user, sm3 = choice([(social_ad(),""), game_manager.random_encounter(c, conn)])
                if sm3:
                    Send_message(f"/w {user} {sm3}")
                
                ad_iter += 1
            elif ad_iter == 2:
                ad_iter = 0
        else:

            parts = line.split(":", 2)
            
            #
            # DEBUG INFO
            #
            # for attr in parts:
            #     print(attr)
            # print("Line = " + line)
            # print("Parts index 0 = " + parts[0])
            # try:
            #     print("Parts index 1 = " + parts[1])
            # except:
            #     print("No Parts index 1")
            # try:
            #     print("Parts index 2 = " + parts[2])
            # except:
            #     print("No parts index 2")
            # try:
            #     print("Parts index 3 = " + parts[3])
            # except:
            #     pass

            # print("Parts = " + str(parts))
            try:
                if "ROOMSTATE" not in parts[0] and "QUIT" not in parts[0] and "JOIN" not in parts[0] and "PART" not in parts[0] and "PING" not in parts[0]:
                    pass
            except:
                print("Expected Crash")


            if "ROOMSTATE" not in parts[0] and "QUIT" not in parts[0] and "JOIN" not in parts[0] and "PART" not in parts[0] and "PING" not in parts[0]:
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
                if "PRIVMSG" in parts[0]:
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
                        print(f"{datetime.datetime.now()} {username} ({user_status}): {message}")
                        with open("chatlog.txt", 'a') as log:
                            
                            log.write(f"{datetime.datetime.now()} {username} ({user_status}): {str(anyascii(message))}")
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



                    # if username.lower() in commands.get_elevated_users(chan) and username not in autoShoutOut:
                    #     shoutout = [
                    #         f"Big shout out to @{username}! Give them some love here and go follow their channel so you can get updates when they go live! (https://www.twitch.tv/{username.lower()})",
                    #         f"Go check out @{username} they were last streaming {myTwitch.get_raider_id(ClientID, oauth, username)}, check out their channel, if you like what you see toss them a follow. You never know, you may find your new favorite streamer. (https://www.twitch.tv/{username.lower()})",
                    #         f"A wild {myTwitch.get_raider_id(ClientID, oauth, username)} has appeared, prepare for battle! @{username}, I choose you! (https://www.twitch.tv/{username.lower()})",
                    #         f"According to @13thfaerie: 'potato' which I think means: go check out @{username}, last streaming: {myTwitch.get_raider_id(ClientID, oauth, username)}. (https://www.twitch.tv/{username.lower()})"]
                    #     Send_message(choice(shoutout))
                    #     autoShoutOut.append(username)
                                

                    if message[0] == '!':
                        message = message.strip('\r')
                        
                        # REFACTORING EVERYTHING AFTER THIS LINE OUT OF BOT_BODY!
                        # 
                        # commands.commands(username, message)

                        if username != '':
                            # TODO: Mod, Broadcaster, FOTS, VIP Commands.
                            # print(username)
                            if username.lower() in get_elevated_users(chan) and username.lower() != "rhyle_":
                                if message[0:7].lower() == '!create':
                                    # Parse the command to be added/created
                                    command, target, action = message.split(
                                        ', ')
                                    ex_com, command = command.split(' ')
                                    command = '!' + command
                                    c.execute("insert into commands values (:command, :target, :action)",
                                              {'command': command, 'target': target, 'action': action})
                                    conn.commit()
                                    Send_message("Command " + command + " has been added.")
                                elif message in ['!rip', '!youdied','!youdead', '!ded', '!udead', '!medic', '!mandown'] and death_counter is True:
                                    death_message = [
                                        f"Uh oh, looks like Rhyle_ died... again",
                                        f"Looks like Rhyle_ has gone the way of the dodo.",
                                        f'Rhyle_ has been eliminated by IOI-655321',
                                        f'MEDIC!!!',
                                        f'You have died, Returning to Bind point.  Loading....',
                                        f'You will not evade me %T!',
                                        f'Rhyle_ began casting Ranger Gate.'
                                    ]
                                    sounds = [
                                        'hes-dead-jim.mp3',
                                        'Price-is-right-losing-horn.mp3', 
                                        'run-bitch-ruun_part.mp3', 
                                        'super-mario-bros-ost-8-youre-dead.mp3', 
                                        'why-you-always-dying-destiny.mp3',
                                        'wilhelmscream.mp3',
                                        'gta-san-andreas-ah-shit-here-we-go-again_BWv0Gvc.mp3',
                                        'you-are-dead-2.mp3',
                                        
                                    ]
                                    Send_message(choice(death_message))
                                    soundcommands.playme(choice(sounds))
                                    deathcounter.increment_death_count(death_counter_character)
                                    
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
                                        f"Go check out {user} they were last streaming {myTwitch.get_raider_id(ClientID, Token, user)}, check out their channel, if you like what you see toss them a follow. You never know, you may find your new favorite streamer. (https://www.twitch.tv/{user.lower()})",
                                        f"A wild {myTwitch.get_raider_id(ClientID, Token, user)} has appeared, prepare for battle! {user}, I choose you! (https://www.twitch.tv/{user.lower()})",
                                        f"According to @13thfaerie: 'potato' which I think means: go check out {user}, last streaming: {myTwitch.get_raider_id(ClientID, Token, user)}. (https://www.twitch.tv/{user.lower()})"]
                                    Send_message(choice(shoutout))
                                elif '!randomenc' in message.lower():
                                    try:
                                        ex_com, user = message.lower().split(' ')
                                        user, sm3 = game_manager.random_encounter(c, conn, user.strip('@'))
                                        if sm3:
                                            Send_message(f"/w {user} {sm3}")
                                    except:
                                        user, sm3 = game_manager.random_encounter(c, conn)
                                        if sm3:
                                            Send_message(sm3)
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
                                
                            # Broadcaster
                            elif username.lower() in ['rhyle_']:
                                if '!goaway' in message.lower():
                                    Send_message("Shutting down now.")
                                    Running = False
                                elif '!setdc' in message:
                                    # used to set which character/game is being actively tracked in the deathcounter.
                                    # for EQ use Character_Name-Server
                                    # Any other game just use Character_Name
                                    if len(message.split(" ")) == 2:
                                        cmd, character = message.split(" ")
                                        death_counter_character = character
                                        deathcounter.create_death_counter_file(character, 0)
                                        Send_message(f"Death counter has been set to track deaths for: {character}")
                                        death_counter = True
                                    elif len(message.split(" ")) == 3:
                                        cmd, character, character_class = message.split(" ")
                                        death_counter_character = character
                                        deathcounter.create_death_counter_file(character, 0, character_class)
                                        Send_message(f"Death counter has been set to track deaths for: {character}")
                                        death_counter = True
                                    else:
                                        Send_message("You have not provided enough information to set the current death counter. " \
                                            "!setdc <character_name-server> optional: <character class>")

                                elif message in ['!rip', '!ded','!udead', '!medic', '!man down'] and death_counter is True:
                                    death_message = [
                                        f"Uh oh, looks like Rhyle_ died... again",
                                        f"Looks like Rhyle_ has gone the way of the dodo.",
                                        f'Rhyle_ has been eliminated by IOI-655321',
                                        f'MEDIC!!!',
                                        f'You have died, Returning to Bind point.  Loading....',
                                        f'You will not evade me %T!',
                                        f'Rhyle_ began casting Ranger Gate.'
                                    ]
                                    sounds = sounds = [
                                        'hes-dead-jim.mp3',
                                        'Price-is-right-losing-horn.mp3', 
                                        'run-bitch-ruun_part.mp3', 
                                        'super-mario-bros-ost-8-youre-dead.mp3', 
                                        'why-you-always-dying-destiny.mp3',
                                        'wilhelmscream.mp3',
                                        'gta-san-andreas-ah-shit-here-we-go-again_BWv0Gvc.mp3',
                                        'you-are-dead-2.mp3',
                                    ]
                                    Send_message(choice(death_message))
                                    soundcommands.playme(choice(sounds))
                                    deathcounter.increment_death_count(death_counter_character)

                                elif message[0:6].lower() == "!title":
                                    # !title <Title Text>; Game Name
                                    update_info = message.replace("!title ", "")
                                    # print(myTwitch.get_current_tags(ClientID, Token))
                                    print(myTwitch.get_status(ClientID, Token))
                                    # print(myTwitch.set_tags(ClientID, Token))
                                    print(myTwitch.update_twitch(ClientID, Token, update_info))
                                elif message[0:7].lower() == "!gameid":
                                    try:
                                        cmd, game_name = message.split(" ", 1)
                                    except:
                                        Send_message("Sorry, you did not supply a game name to check the ID of.")
                                        break
                                    gameid = myTwitch.get_games(ClientID, Token, game_name)
                                    print(f"You requested the ID of {game_name}: {gameid}")
                                elif message[0:8].lower() == '!adduser':
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
                                elif '!raid ' in message and len(message)>7:
                                    chatmessage, username = message.split(" ")
                                    chatmessage = c.execute("select action from commands where ex_command = ?",(chatmessage.strip(''),)).fetchone()[0]
                                    Send_message(chatmessage, username)
                                    chatmessage = c.execute("select action from commands where ex_command = '!calls'").fetchone()[0]
                                    Send_message(chatmessage, username)
                                    continue
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
                                        twoted = twitter.send_tweet(tweet)
                                        Send_message(twoted)
                                    else:
                                        Send_message("Sorry boss, that tweet is too long.")
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
                                # =====
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
                                        f"Go check out {user} they were last streaming {myTwitch.get_raider_id(ClientID, Token, user)}, check out their channel, if you like what you see toss them a follow. You never know, you may find your new favorite streamer. (https://www.twitch.tv/{user.lower()})",
                                        f"A wild {myTwitch.get_raider_id(ClientID, Token, user)} has appeared, prepare for battle! {user}, I choose you! (https://www.twitch.tv/{user.lower()})",
                                        f"According to @13thfaerie: 'potato' which I think means: go check out {user}, last streaming: {myTwitch.get_raider_id(ClientID, Token, user)}. (https://www.twitch.tv/{user.lower()})"]
                                    Send_message(choice(shoutout))
                                elif '!randomenc' in message.lower():
                                    try:
                                        ex_com, user = message.lower().split(' ')
                                        user = user.strip("@")
                                        user, sm3 = game_manager.random_encounter(c, conn, user)
                                        if sm3:
                                            Send_message(f"/w {user} {sm3}")
                                    except:
                                        user, sm3 = game_manager.random_encounter(c, conn)
                                        if sm3:
                                            Send_message(f"/w {user} {sm3}")
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

                            # viewer commands start here.

                            if message[:3].lower() not in ('!cm', '!de', '!gi','!rt', '!ra', '!hl', '!de', '!ad', '!go', '!gu', '!sl', '!mt', '!vi', '!st'):
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

                                elif "!quote" in message.lower():
                                    chatmessage = quotes.quote(message,c, conn)

                                elif "!excuse" in message.lower():
                                    chatmessage = f"Hello {username}.  Your excuse for the evening is: {' '.join(excuse.make_excuse())}" 

                                elif "!ban" in message.lower():
                                    chatmessage = f"It looks like {username} no longer thinks they can be a " \
                                        "productive member of the community and has requested to be banned."
                                    Send_message(f"/ban {username} Self exile")
                                    time.sleep(5)
                                    Send_message(f"/unban {username}")

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
                                            """insert into users values (?, ?, 0, '', 0, 0, 0, 0)""", (username.lower(), 'viewer'))
                                        conn.commit()
                                        print(
                                            f"user {username} has been added to the database")
                                    finally:
                                        # print(username.lower())
                                        if (c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone() != ('',)):
                                            gchar_dict_to_sql = c.execute(
                                                "select gchar from users where uname = ?", (username.lower(),)).fetchone()[0]
                                            gchar_dict = ast.literal_eval(gchar_dict_to_sql)

                                            cxp, crowns, max_wounds, current_wounds = c.execute(
                                                "select exp, crowns, MaxWounds, CurrentWounds from users where uname = ?", (username,)).fetchone()
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
                                                    f"{gchar_dict['strength']} Toughness: {gchar_dict['toughness']} Wounds: {current_wounds}/{max_wounds} " \
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
                                                    f"{gchar_dict['strength']} Toughness: {gchar_dict['toughness']} Wounds: {current_wounds}/{max_wounds} " \
                                                    f" You are currently using your " \
                                                    f"{str(gchar_dict['weapon']).capitalize()} as a weapon and " \
                                                    f"{str(gchar_dict['armor']).capitalize()} for armor. If you would like to" \
                                                    f" upgrade either you can (!)shop to spend your crowns to purchase new weapons" \
                                                    f" and armor.  Current available Exp: {cxp} Crown Purse: {crowns}."
                                                build_whisper2 = f"{username} You can level up your skills with !levelup and then one of the 4 skills or " \
                                                    f"wounds.  Skills will not go above 79 and Wounds is capped at 20."
                                                Send_message(f"/w {build_whisper}")
                                                Send_message(f"/w {build_whisper2}")
                                            chatmessage = ""

                                        else:
                                            # Generate character using the Character Class
                                            gchar = character_manager.chat_char(username)

                                            # Converts the Class to a dictionary
                                            gchar_dict = gchar.get_char(username)

                                            # Casts the dictionary to a string for storage in SQL
                                            gchar_dict_to_sql = str(gchar_dict)

                                            article = 'a '
                                            wounds = randint(1,11)
                                            if gchar_dict['race'] == 'elf':
                                                gchar_dict['race'] = 'elven'
                                                chat_race = 'elf'
                                                article = 'an '
                                                
                                                if wounds >= 1 and wounds <= 3:
                                                    wounds = 9
                                                elif wounds >= 4 and wounds <= 6:
                                                    wounds = 10
                                                elif wounds >= 7 and wounds <= 9:
                                                    wounds = 11
                                                else:
                                                    wounds = 12
                                            elif gchar_dict['race'] == 'dwarf':
                                                chat_race = 'dwarf'
                                                gchar_dict['race'] = 'dwarven'
                                                if wounds >= 1 and wounds <= 3:
                                                    wounds = 11
                                                elif wounds >= 4 and wounds <= 6:
                                                    wounds = 12
                                                elif wounds >= 7 and wounds <= 9:
                                                    wounds = 13
                                                else:
                                                    wounds = 14
                                            elif gchar_dict['race'] == 'halfling':
                                                chat_race = gchar_dict['race']
                                                if wounds >= 1 and wounds <= 3:
                                                    wounds = 8
                                                elif wounds >= 4 and wounds <= 6:
                                                    wounds = 9
                                                elif wounds >= 7 and wounds <= 9:
                                                    wounds = 10
                                                else:
                                                    wounds = 11
                                            elif gchar_dict['race'] == 'human':
                                                chat_race = gchar_dict['race']
                                                if wounds >= 1 and wounds <= 3:
                                                    wounds = 10
                                                elif wounds >= 4 and wounds <= 6:
                                                    wounds = 11
                                                elif wounds >= 7 and wounds <= 9:
                                                    wounds = 12
                                                else:
                                                    wounds = 13
                                            else:
                                                chat_race = gchar_dict['race']

                                            # cxp = c.execute(
                                            #     "select exp from users where uname = ?", (username,)).fetchone()[0]

                                            # Stores character in SQL
                                            c.execute("""update users
                                                        set gchar = ?,
                                                        MaxWounds = ?,
                                                        CurrentWounds = ?
                                                        where uname = ?""", (gchar_dict_to_sql, wounds, wounds, username.lower()))
                                            
                                            conn.commit()

                                            #Get current XP, Crowns, max and current wounds.
                                            cxp, crowns, max_wounds, current_wounds = c.execute(
                                                "select exp, crowns, MaxWounds, CurrentWounds from users where uname = ?", (username,)).fetchone()


                                            # Message to chat and /w to user the character information.
                                            chatmessage = f"{username} the {chat_race.capitalize()} has " \
                                                f"entered the game."

                                            # This is the whisper to user.
                                            build_whisper = f"{username} {username} is {article}" \
                                                f"{str(gchar_dict['race']).capitalize()} " \
                                                f"{gchar_dict['prof']} Weapon Skill: {gchar_dict['weapon_skill']} " \
                                                f"Ballistic Skill: {gchar_dict['ballistic_skill']} Strength: " \
                                                f"{gchar_dict['strength']} Toughness: {gchar_dict['toughness']} Wounds: {current_wounds}/{max_wounds}" \
                                                f" You are currently using your " \
                                                f"{str(gchar_dict['weapon']).capitalize()} as a weapon and " \
                                                f"{str(gchar_dict['armor']).capitalize()} for armor. If you would like to" \
                                                f" upgrade either you can (!)shop to spend your crowns to purchase new weapons" \
                                                f" and armor.  Current available Exp: {cxp} Coin Purse: {crowns}"

                                            Send_message(f"/w {build_whisper}")

                                elif "!retire" in message.lower():
                                    
                                    # TODO: Retired characters should output to HTML and be stored on a webserver.
                                    # TODO: should also provide link for download in whisper.
                                    print(retire(username.lower()))
                                    chatmessage = f"Hello {username}, this command is being worked on at the " \
                                        "moment, please check back soon(tm)."

                                elif "!permadeath" in message.lower():
                                    c.execute("update users set gchar = '' where uname = ?", (username.lower(),))
                                    conn.commit()
                                    chatmessage = f"{username} has chosen to permanently kill off their " \
                                        "character. You may issue the !char command to create a new one."

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

                                    cxp = game_manager.get_user_exp(c, username)
                                    challenger = game_manager.ret_char(c,username)
                                    victim = game_manager.ret_char(c,target)

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
                                            vic_roll = (vic['strength'] + victim_random) - chall['toughness']
                                            if vic_roll < 0:
                                                vic_roll = 0
                                            Send_message(f"{victim[0]} hits {challenger[0]} with their {vic['weapon']} (({vic['weapon_skill']} + {victim_random})-{chall['toughness']}) ({vic_roll})")
                                            time.sleep(1)
                                            challenger_random = randint(2, 100)
                                            chall_roll = (chall['strength'] + challenger_random) - vic['toughness']
                                            if chall_roll < 0:
                                                chall_roll = 0
                                            Send_message(f"{challenger[0]} returns the blow! (({chall['weapon_skill']} + {challenger_random}) - {vic['toughness']}) ({chall_roll})")
                                            time.sleep(1)

                                            if vic_roll > chall_roll:
                                                Send_message(f'{victim[0]} has defeated their challenger {challenger[0]} and earned! {amount} exp.')
                                                challenge_result(victim[0], amount, challenger[0])
                                            elif vic_roll == chall_roll:
                                                Send_message(
                                                    f'After a knock-down, drag-out fight both {victim[0]} and {challenger[0]} call it a draw!')
                                            else:
                                                Send_message(f'After a knock-down, drag-out fight both {challenger[0]}, and {victim[0]} have been ejected from the bar, {challenger[0]} clearly the victor, earning themselves {amount}.')
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
                                    time_started = myTwitch.get_uptime(ClientID, oauth, Token)
                                    time_started = time_started["data"][0]["started_at"]
                                    time_started = datetime.datetime.strptime(time_started,"%Y-%m-%dT%H:%M:%SZ")
                                    
                                    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
                                    now = datetime.datetime.strptime(now, "%Y-%m-%dT%H:%M:%SZ")
                                    chatmessage = f'Rhyle_ has been live for {now - time_started} hours.'

                                elif "!levelup" in message.lower().replace('\r\n', ''):
                                    chatmessage = ''
                                    if len(message) <= 9:
                                        chatmessage = f"/w {username} The proper command for this includes one of the " \
                                            "five character stats: WS, BS, S, T, Wounds."
                                    else:
                                        ex_com, stat = message.replace("  ", " ").strip('\r').split(' ')
                                        level_up(username, stat)

                                elif "!shop" in message.lower().strip('\r'):
                                    if len(message) == 5:
                                        shop(username)
                                    else:
                                        ex_com, *arg = message.strip('\r').split(' ')
                                        shop(username, *arg)
                                    chatmessage = ""

                                elif "!beaz" in message.lower().strip('\r') and (username.lower() == "big_beaz" or username.lower() == "rhyle_") :
                                    soundcommands.playme("beaz")
                                    chatmessage = ''

                                elif "!faerie" in message.lower().strip('\r') and username.lower() == "13thfaerie" :
                                    soundcommands.playme("faerie")
                                    chatmessage = ''

                                elif "!fts" in message.lower().strip('\r'):
                                    soundcommands.playme("fts")
                                    chatmessage = ''

                                # elif "!sr" in message.lower():
                                #     chatmessage = f"I'm sorry, {username}, song requests have been turned off indefinitely."
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
                            elif message.lower() == '!gunter' or message.lower() == "!cmd":
                                commandlist = list(
                                    c.execute("select ex_command from commands"))
                                for itr in range(len(commandlist)):
                                    commandlist[itr] = commandlist[itr][0]
                                for item in [
                                    "!ban", "!challenge", "!change", "!char", 
                                    "!excuse", "!gunter", "!levelup", "!lurk", 
                                    "!permadeath", "!quote", "!shop", "!uptime",
                                    ]:
                                    commandlist.append(item)
                                Send_message(
                                    f"You've found the (not so) hidden command list {username}. Command list: "
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
