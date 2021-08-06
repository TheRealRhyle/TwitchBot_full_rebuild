from urllib import request
import json 
from random import choice

def get_elevated_users(target):
    """ Supply this function with the name of your twitch channel to return a list of
    users who are VIPs, Mods, or the Broadcaster.  Essentially returns anyone with
    elevated channel rights.

    Args:
        target (string): Your twitch channel name

    Returns:
        {set}: Users who have elevated rights.
    """
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

def commands(username, message):
    """Takes in the username and the message to parse
    will return the results of the command.

    Args:
        username (string): The name of the person who issued the command.
        message (string): The command string.
    
    Returns:
        result (string): the result of the issued command.
    """        

    # Broadcaster
    
    if username.lower() in get_elevated_users("rhyle_"):
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
        elif '!so ' in message.lower():
            ex_com, user = message.replace('\r', '').split(' ')
            if ('@' in user):
                user = user.replace("@", "")
            shoutout = [
                f"Big shout out to {user}! Give them some love here and go follow their channel so you can get updates when they go live! (https://www.twitch.tv/{user.lower()})",
                f"Go check out {user} they were last streaming {myTwitch.get_raider_id(ClientID, oauth, user)}, check out their channel, if you like what you see toss them a follow. You never know, you may find your new favorite streamer. (https://www.twitch.tv/{user.lower()})",
                f"A wild {myTwitch.get_raider_id(ClientID, oauth, user)} has appeared, prepare for battle! {user}, I choose you! (https://www.twitch.tv/{user.lower()})",
                f"According to @13thfaerie: 'potato' which I think means: go check out {user}, last streaming: {myTwitch.get_raider_id(ClientID, oauth, user)}. (https://www.twitch.tv/{user.lower()})"]
            return(choice(shoutout))
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


if __name__ == "__main__":
    print(get_elevated_users("rhyle_"))