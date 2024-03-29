from wfrpgame import itemlist, bestiary
from random import randint, choice
from urllib import request
import math
import json
import ast

def get_user_exp(c, username):
    """Gets stats from  the selected user

    Args:
        c (pointer): database pointer
        username (string): viewer name

    Returns:
        exp, crowns, max_wounds
    """
    user_info = c.execute("select * from users where uname = ?", (username,)).fetchone()
    return user_info[2], user_info[4], user_info[5]

def get_active_list():
    resp = request.urlopen("http://tmi.twitch.tv/group/user/rhyle_/chatters")
    chatters_json = resp.read().decode("UTF-8")
    userlist = json.loads(chatters_json)
    viewerlist = userlist['chatters']['viewers']
    # broadcaster = userlist['chatters']['broadcaster'][0]

    for usr in range(len(userlist['chatters']['moderators'])):
        viewerlist.append(userlist['chatters']['moderators'][usr])
    for usr in range(len(userlist['chatters']['vips'])):
        viewerlist.append(userlist['chatters']['vips'][usr])
    for usr in range(len(userlist['chatters']['broadcaster'])):
        viewerlist.append(userlist['chatters']['broadcaster'][usr])
    return viewerlist

def ret_char(c, username):
    """Get character from database.

    Args:
        c (pointer): Database pointer
        username (string): viewer name

    Returns:
        Either returns none or a dictionary
    """
    try:
        char_to_return, Status = c.execute("select gchar, status from users where uname = ?", (username,)).fetchone()
        # If the selected viewer is a known bot, bypass that user
        if Status == 'bot':
            char_to_return = ''
        # if c.execute("select status from users where uname = ?", (username,)).fetchone()[0] == 'bot':
        #     char_to_return = ''
    except TypeError:
        print("User in channel that has not been added to the database yet: ", username)
        char_to_return = ''
    finally:
        if char_to_return == '':
            return 'None'
        else:
            return ast.literal_eval(char_to_return)

def random_encounter(c, conn, *args):
    shoplist = itemlist.load_shop()
    base_damage = 0
    encounter_value = 100
    won_crowns = randint(1, 10)
    robbers = .10 # If someone looses to a Pickpocket, Bandit, or Footpat they lose this percentage of their current purse.
    c_wins = 1
    encounter_dictionary = bestiary.choose_mob()
    hit_location, c_hit_location, m_hit_location = 0, 0, 0
    loser = ''
    new_damage = 0
    chatmessage, chatmessage2, chatmessage3 = "","",""

    # if no character was submitted with the randomenc request, grab a random viewer
    if not args:
        user = choice(get_active_list())
        random_character = ret_char(c, user)

    # Strip the @ if it was supplied, and get the requested user
    else:
        user = args[0].strip('\r\n').strip('@')
        random_character = ret_char(c, user)

    while random_character == 'None':
        user = choice(get_active_list())
        random_character = ret_char(c, user)

    
    # Get selected users current Crowns, Max_ and Current_ wounds.
    # crowns, max_wounds, current_wounds  = c.execute("select crowns, MaxWounds, CurrentWounds from users where uname = ?", (str(random_character['name']).lower(), )).fetchone()
    crowns = c.execute("select crowns from users where uname = ?", (str(random_character['name']).lower(), )).fetchone()[0]
    
    current_wounds = random_character["current_wounds"]

    
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
    character_armor = random_character['armor']
    try:
        if shoplist[character_weapon]['type'] == "Melee":
            damage_mod = shoplist[character_weapon]['damage']
            base_damage = math.floor((random_character['strength'])/10)
            if "+" in damage_mod:
                base_damage += int(damage_mod.split("+")[1])
            elif "-" in damage_mod:
                base_damage -= int(damage_mod.split("-")[1])
            else:
                base_damage = int(damage_mod)
        elif shoplist[character_weapon]['type'] == "Ranged":
            damage_mod = shoplist[character_weapon]['damage']
            
            if 'SB' in shoplist[character_weapon]['damage']:
                base_damage = math.floor((random_character['strength'])/10) - int(damage_mod.split("-")[1])
            else:
                base_damage = int(damage_mod)
            
    except:
        if math.floor((random_character['strength'])/10) - 4 < 0:
            base_damage = 0
        else:
            base_damage = math.floor((random_character['strength'])/10) - 4

    # Determin which skill to use based on wielded weapon
    try:
        if shoplist[character_weapon]['type'] == 'Melee':
            character_ws = random_character['weapon_skill']    
        elif shoplist[character_weapon]['type'] == 'Ranged':
            character_ws = random_character['ballistic_skill']
        else:
            character_ws = random_character['weapon_skill']    
    except:
        character_ws = random_character['weapon_skill']    
    # character_ws = random_character['weapon_skill']

    # Generate a pseudo random number to represend the 2d10 weaponskill check.
    character_roll = (randint(2, 100))
    # print(f'Character: {character_ws} : {character_roll}')
    if character_roll > character_ws:
        character_gos = -1  
    elif character_roll <= character_ws:
        character_gos = 1
    else:
        c_hit_location = str(character_roll)[::-1]
        new_damage = randint(1,11) + base_damage
        character_gos = math.floor(character_ws / 10) - math.floor(character_roll / 10)
    
    mob_roll = (randint(2, 100))
    mob_ws = int(encounter_dictionary['ws'])
    # print(f'Mob: {mob_ws}:{mob_roll}')
    if mob_roll > mob_ws:
        mob_gos = -1
    elif mob_roll <= mob_ws:
        mob_gos = 1
    else:
        m_hit_location = str(mob_roll)[::-1]
        mob_gos = math.floor(mob_ws / 10) - math.floor(mob_roll / 10)
    # print(f'Monster Successes: {mob_gos}')

    
    if (character_gos > mob_gos) and (character_gos >= 0):
        # Viewer wins!
        hit_location = c_hit_location
        base_damage += character_gos
        loser = encounter_dictionary['name'].lower()
        exp, _, wins = get_user_exp(c, random_character['name'].lower())
        exp += encounter_value
        c_wins += wins
        crowns += won_crowns
        c.execute("update users set exp = ?, crowns = ?, wins = ? where uname = ?", (encounter_value, crowns, c_wins, random_character['name'].lower()))
        conn.commit()
        chatmessage3 = f"You've earned {encounter_value} experience, and found {won_crowns} crowns in the aftermath!"
    elif (character_gos == mob_gos) and (character_gos >= 0):
        # Draw
        hit_location = c_hit_location
        loser = 'Beaten and bloodied they each ran off to fight another day.'
        # print('Point: Both!')
    elif (character_gos < mob_gos) and (mob_gos >= 0):
        # Random monster wins
        hit_location = m_hit_location
        base_damage += mob_gos
        loser = random_character['name'].lower()
        
        mitigation = int(shoplist[character_armor]['damage'].split(" ")[0])
        base_damage -= mitigation
        if (current_wounds - base_damage) <= 0:
            current_wounds = 0
        else:
            current_wounds -= base_damage

        # Set new CurrentWounds
        c.execute("update users set CurrentWounds = ? where uname = ?",(current_wounds, random_character['name'].lower()))
        conn.commit()

        if encounter_dictionary["name"] in ["Pickpocket", "Bandit", "Footpad"]:
            chatmessage3 = f"@{random_character['name']}, you might want to check your purse after that encounter."
            new_crowns = int(crowns - (crowns * robbers))
            c.execute("update users set crowns = ? where uname = ?", (new_crowns, random_character['name'].lower()))
            conn.commit()
            
        
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
        f'{random_character["name"]}'

    if "fists" not in character_weapon:
        if shoplist[character_weapon]['type'] == "Melee":
            chatmessage= chatmessage + f' readied their {random_character["weapon"]} against the ' \
            f'{mob_weapon.lower()} of the {encounter_dictionary["name"].lower()}.' 
        elif shoplist[character_weapon]['type'] == "Ranged":
            chatmessage= chatmessage + f' fired their {random_character["weapon"]} toward the ' \
            f'oncoming {encounter_dictionary["name"].lower()}.'
    else:
        chatmessage= chatmessage + f' tried to make peace with their gods and readied their {character_weapon} ' \
        f'against the {mob_weapon.lower()} of the {encounter_dictionary["name"].lower()}.'
    
    if len(loser) > 17:
        chatmessage2 = f'{loser}'
    else:
        if (loser != random_character["name"]):
            loser = "the " + encounter_dictionary["name"]
            damage = f" for {base_damage}(New rolls: {new_damage}) wounds, "
            lossmessage = [f'{loser.title()} was struck in the {hit} but managed to flee before a fatal blow was landed.',
            f'Someone will need to be digging a grave for {loser} after they lost their {hit}.']
        else:
            damage = f" for {base_damage}(New rolls: {new_damage}) wounds, "
            if current_wounds == 0:
                lossmessage = [f"Unfortunately our hero, {loser.title()}, has succumb and shuffled off this mortal coil."]
            else:
                lossmessage = [f"Narrowly avoiding the {encounter_dictionary['name']}, {loser.title()} was has been able to cheat death once more."]

        # If fighter lived or died
        
        # lossmessage = [f'{loser.title()} was struck in the {hit} {damage} but managed to flee before a fatal blow was landed.',
        #     f'Someone will need to be digging a grave for {loser} after they lost their {hit}']
        chatmessage2 = choice(lossmessage)
        # f'the fight did not end well for {loser}. {character_roll} vs {mob_roll}'
    
    with open("F:\Google Drive\May 2020\TwitchBot_full_rebuild\wfrpgame\encounter.txt", "w") as f:
        text = ' '.join([chatmessage, chatmessage2 + "  || ", "\t"])
        f.write(text)
    
    if chatmessage3:
        return user, chatmessage3
    else:
        return user, False


if __name__ == "__main__":
    print(get_active_list())