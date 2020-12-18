import urllib
from urllib import request
import json
import sqlite3
import time
import schedule
from time import sleep
import socket
import random
from wfrpgame import tcChargen

global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()


def check_chatters():
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

    ulist = c.execute("select uname from users").fetchall()
    uliststr = str(ulist).replace(",)", ")").replace("(",'').replace(')','')

    # for each user returned in the viewer list check to see if they already exist in the database
    # print(uliststr)
    for usr in range(len(viewerlist)):
        viewer = "'" + viewerlist[usr] + "'"
        if viewer not in uliststr:
            # If the viewer does not exist in the database, add them with status viewer

            # Also assign a base character.
            base_char = tcChargen.base_char(viewerlist[usr])
            base_char_dict = base_char.get_char(viewerlist[usr])
            gchar_dict_to_sql = str(base_char_dict)
            c.execute("""insert into users values (?, ?, 0, ?, 0)""",(viewerlist[usr], 'viewer', gchar_dict_to_sql))
            conn.commit()
            print("user " + viewerlist[usr] + " has been added to the database")
        else:
            # print(c.execute("select status, exp from users where uname = ?", (str(viewerlist[usr]).lower(),)).fetchone())

            cquery = c.execute("select * from users where uname = ?", (str(viewerlist[usr]).lower(),)).fetchone()

            # if cquery == None:
            #     pass

            if cquery[1] != 'bot' and viewerlist[usr].lower() != 'rhyle_bot':
                # try:
                cxp = cquery[2]
                current_crowns = cquery[4]
                cxp += 5
                current_crowns += 1
                c.execute("update users set exp = ?, crowns = ? where uname = ?", (cxp, current_crowns, str(viewerlist[usr]).lower()))
                conn.commit()
                print(cquery[0] + ' has earned experience for being here.  Current XP: ' + str(cxp) + '\tCurrent crowns: ' + str(current_crowns))
                # except:
                # print('No exp added for ' + cquery[0])
    print('--------- \n')
    # return broadcaster

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

def get_chatters():
    print("Getting current chat list.")
    check_chatters()
    schedule.every(10).minutes.do(check_chatters)
    while 1:
        schedule.run_pending()
        time.sleep(1)

def social_ad():
    ads = ['Find me on twitter to get stream updates and notifications when I go live! @rhyle_ twitter.com/rhyle_',
    'You can join the discord server here discord.gg/qEsfAJS',
    'You can find my steam profile at this link steamcommunity.com/id/Rhyle/games/',
    'I am currently working on a semi-interactive chat based role playing game. The core ruleset is from and old pen and paper table top game called Warhammer Fantasy Roleplay. The game will be a stripped down and modified version of the rules because I do not want to be C&Dd by Games-Workshop or Fantasy Flight. Game commands !game !char !permadeath !retire !changerace',
    'If you\'re familiar with python and want to offer some suggestions I have a trello board setup for this bot at https://trello.com/b/CyeWbpNT/existing-rhylebot', 
    'The current project is here https://github.com/TheRealRhyle/TwitchBot_full_rebuild if I am not streaming then it should be up to date always check my chat or join my !discord for up to the commit information',
    'Don\'t forget that you can link your Twitch account to your Amazon prime account and sub to your favorite streamers for free once a month! Here\'s the link for more info twitch.amazon.com/prime',
    'Please remember that Twitch doesn\'t count a view if you have the video paused or the sound muted. If you came all this way to show some support, why not make sure it counts? If you don\'t want the sound on try muting the tab itself instead of the vid. All of your love and support is always appreciated!'
    ]
    return random.choice(ads)

if __name__ == "__main__":
    print("Started")
    check_chatters()
    schedule.every(10).minutes.do(check_chatters)

    while 1:
        schedule.run_pending()
        time.sleep(1)
