import sqlite3
import time
import requests
import schedule
import random
from wfrpgame import tcChargen

global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()
streamr = c.execute("select * from streamer").fetchall()
streamr = list(streamr[0])
_, _, _, oauth, _, ClientID, Token, bcasterId, moderatorId, OAuthBearer = streamr


def check_chatters():
    """
    this is a doc string, now you can lint away!

    """
    chatters_all = f"https://api.twitch.tv/helix/chat/chatters?broadcaster_id={bcasterId}&moderator_id={moderatorId}"
    h1 = {
        "Client-ID": ClientID,
        "Accept": "application/vnd.twitchtv.v5+json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + Token,
    }
    resp = requests.get(url=chatters_all, headers=h1)

    viewerlist = [
        user[1]["user_name"].lower()
        for user in enumerate(eval(resp.content.decode("utf-8"))["data"])
    ]
    ulist = c.execute("select uname from users").fetchall()
    uliststr = []
    uliststr.append([name[1][0].lower() for name in enumerate(ulist)])
    uliststr = uliststr[0]
    # for each user returned in the viewer list check to see if they already exist in the database
    # print(uliststr)
    for usr in enumerate(viewerlist):
        if usr[1] not in uliststr:
            base_char = tcChargen.base_char(usr[1])
            # base_char_dict = base_char.get_char(viewerlist[usr])
            gchar_dict_to_sql = str(base_char)
            c.execute(
                """insert into users values (?, ?, 0, ?, 0, 0, 11, 11)""",
                (usr[1], "viewer", gchar_dict_to_sql),
            )
            conn.commit()
            print("user " + usr[1] + " has been added to the database")
        else:
            cquery = c.execute(
                "select * from users where uname = ?", (str(usr[1]).lower(),)
            ).fetchone()
            if cquery[1] != "bot" and usr[1].lower() != "rhyle_bot":
                cxp = cquery[2]
                current_crowns = cquery[4]
                cxp += 5
                current_crowns += 1
                c.execute(
                    "update users set exp = ?, crowns = ? where uname = ?",
                    (cxp, current_crowns, str(usr[1]).lower()),
                )
                conn.commit()
                print(
                    cquery[0]
                    + " has earned experience for being here.  Current XP: "
                    + str(cxp)
                    + "    Current crowns: "
                    + str(current_crowns)
                )
    print("--------- \n")
    # return broadcaster


def get_active_list():
    chatters_all = f"https://api.twitch.tv/helix/chat/chatters?broadcaster_id={bcasterId}&moderator_id={moderatorId}"
    h1 = {
        "Client-ID": ClientID,
        "Accept": "application/vnd.twitchtv.v5+json",
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": "Bearer " + Token,
    }
    resp = requests.get(url=chatters_all, headers=h1)
    userlist = [
        user[1]["user_name"].lower()
        for user in enumerate(eval(resp.content.decode("utf-8"))["data"])
    ]

    return userlist


def get_chatters():
    print("Getting current chat list.")
    check_chatters()
    schedule.every(10).minutes.do(check_chatters)
    while 1:
        schedule.run_pending()
        time.sleep(1)


def social_ad():
    ads = [
        "Find me on twitter to get stream updates and notifications when I go live! @rhyle_ twitter.com/rhyle_",
        "You can join the discord server here discord.gg/qEsfAJS",
        "You can find my steam profile at this link steamcommunity.com/id/Rhyle/games/",
        "I am currently working on a semi-interactive chat based RPG. The core ruleset is from Warhammer Fantasy Roleplay 2nd Edition. The game is a stripped down and modified version of the rules for legal reasons. Game commands !game !char !permadeath !retire !changerace",
        "If you're familiar with python and want to offer some suggestions I have a trello board setup for this bot at https://trello.com/b/CyeWbpNT/existing-rhylebot",
        "The current project is here https://github.com/TheRealRhyle/TwitchBot_full_rebuild if I am not streaming then it should be up to date always check my chat or join my !discord for up to the commit information",
        "Don't forget that you can link your Twitch account to your Amazon prime account and sub to your favorite streamers for free once a month! Here's the link for more info twitch.amazon.com/prime",
        "Please remember that Twitch doesn't count a view if you have the video paused or the sound muted. If you came all this way to show some support, why not make sure it counts? If you don't want the sound on try muting the tab itself instead of the vid. All of your love and support is always appreciated!",
    ]
    return random.choice(ads)


if __name__ == "__main__":
    print("Started")
    get_active_list()
    # schedule.every(10).minutes.do(check_chatters)

    # while 1:
    #     schedule.run_pending()
    #     time.sleep(1)
