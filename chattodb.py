import urllib
from urllib import request
import json
import sqlite3
import time
global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()
import schedule
from time import sleep
import time
import socket

def check_chatters():
    resp = request.urlopen("http://tmi.twitch.tv/group/user/rhyle_/chatters")
    chatters_json = resp.read().decode("UTF-8")
    userlist = json.loads(chatters_json)
    viewerlist = userlist['chatters']['viewers']

    for usr in range(len(userlist['chatters']['moderators'])):
        viewerlist.append(userlist['chatters']['moderators'][usr])
    for usr in range(len(userlist['chatters']['vips'])):
        viewerlist.append(userlist['chatters']['vips'][usr])

    ulist = c.execute("select uname from users").fetchall()
    uliststr = str(ulist).replace(",)", ")").replace("(",'').replace(')','')

    # for each user returned in the viewer list check to see if they already exist in the database
    for usr in range(len(viewerlist)):
        if viewerlist[usr] not in uliststr:
            # If the viewer does not exist in the database, add them with status viewer
            c.execute("""insert into users values (?, ?, 0, '')""",(viewerlist[usr], 'viewer'))
            conn.commit()
            print("user " + viewerlist[usr] + " has been added to the database")
        else:
            # print(c.execute("select status, exp from users where uname = ?", (str(viewerlist[usr]).lower(),)).fetchone())
            cquery = c.execute("select * from users where uname = ?", (str(viewerlist[usr]).lower(),)).fetchone()
            if cquery[1] != 'bot':
                # try:
                cxp = cquery[2]
                cxp += 5
                c.execute("update users set exp = ? where uname = ?", (cxp, str(viewerlist[usr]).lower()))
                conn.commit()
                print(cquery[0] + ' has earned experience for being here.  Current XP: ' + str(cxp))
                # except:
                #     print('No exp added for ' + cquery[0])
            # pass

if __name__ == "__main__":
    print("Started")
    check_chatters()
    schedule.every(5).minutes.do(check_chatters)

    while 1:
        schedule.run_pending()
        time.sleep(1)

print("Started")
check_chatters()
schedule.every(5).minutes.do(check_chatters)
while 1:
    schedule.run_pending()
    time.sleep(1)
