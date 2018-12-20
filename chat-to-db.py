import urllib
from urllib import request
import json
import sqlite3
import time
global conn
global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()
import schedule
import time

def check_chatters():
    print("Checking chatters on twitch.tv/DarkXilde")
    resp = request.urlopen("http://tmi.twitch.tv/group/user/darkxilde/chatters")
    chatters_json = resp.read().decode("UTF-8")
    userlist = json.loads(chatters_json)
    viewerlist = userlist['chatters']['viewers']

    ulist = c.execute("select uname from users").fetchall()
    uliststr = str(ulist).replace(",)", ")").replace("(",'').replace(')','')

    # for each user returned in the viewer list check to see if they already exist in the database
    for usr in range(len(viewerlist)):
        if viewerlist[usr] not in uliststr:
            # If the viewer does not exist in the database, add them with status viewer
            c.execute("""insert into users values (?, ?)""",(viewerlist[usr], 'viewer'))
            conn.commit()
            print("user " + viewerlist[usr] + " has been added to the database")
        else:
            pass

if __name__ == "__main__":
    check_chatters()
    schedule.every(10).minutes.do(check_chatters)

    while 1:
        schedule.run_pending()
        time.sleep(1)
