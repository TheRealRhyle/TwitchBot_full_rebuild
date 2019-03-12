# import schedule
import time
import socket
import urllib
from urllib import request
import json
import sqlite3
import time
import ast
# import tcChargen

global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()

# Random Roll: 25
# tstallis weapon skill: 36
# this would be a hit
# Degrees of success: 2.2


uname = 'rhyle_'

xp, crowns = c.execute("select exp, crowns from users where uname = ?",(uname,)).fetchone()

print(xp, crowns)
# print(c.execute("select crowns from users where uname = ?", ("rhyle_",)).fetchone())

# change_char="'name': 'rhyle_', 'race': 'human', 'prof': 'Camp Follower', 'weapon_skill': 36, 'ballistic_skill': 38, 'strength': 26, 'toughness': 45}"
# username='rhyle_'
# print((change_char))

# c.execute('update users set crowns = 0')
# conn.commit()
# print(c.execute('select * from users where gchar = ""').fetchall())
# print(c.execute(f"select name, exp from users").fetchall())
# print(*c.execute("select uname, exp from users where uname = 'rhyle_bot'").fetchall(), sep='\n')
# c.execute("update users set exp = 3475 where uname = 'rhyle_'")
# conn.commit()
# cxp = c.execute(f"select exp from users where uname = {username}")

# c.execute("update users set exp = 200 where uname = 'ceacelion'")
# conn.commit()

# Clear all characters
# c.execute("update users set gchar = '' where gchar <> ''")
# conn.commit()

# print(*c.execute("select * from users").fetchall(), sep='\n')
# print(c.execute('select * from streamer').fetchall())
# print(str(c.execute("select * from users where gchar != ''").fetchall()).replace("), (",'\n'))
#
# c.execute("update users set gchar = '' where gchar != ''")
# conn.commit()
# print(str(c.execute("select * from users where gchar != ''").fetchall()).replace("), (",'\n'))


# username = 'rhyle_'
# print(c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone()[0])


# if c.execute("select gchar from users where uname = ?", (username,)).fetchone() != ('',):

# c.execute("insert into users values ('rhyle_', 'moderators')")
# conn.commit()
# c.execute("select * from commands where ex_command = '!multi'").fetchall() != []:

# c.execute("update streamer set nick = 'rhyle_bot' where nick in ('rhyle_bot')")
# conn.commit()
# c.execute("""alter table users add crowns integer""")
# conn.commit()

# print(c.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())
# print(c.execute("SELECT * FROM users where uname = 'n3td3v'").fetchall())
# c.execute("update users set status = 'bot' where uname = 'rhyle_bot'")
# conn.commit()


# conn.commit()

# print(str(c.execute("select * from users").fetchall()).replace('),','\n'))




# if c.execute("select * from commands where ex_command = '!multi'").fetchall() != []:
#     print('not empty')
# print(c.execute("select * from commands where ex_command = '!multi'").fetchall())
# print(c.execute('select ex_command from commands').fetchall())
# streamr = c.execute('select * from streamer').fetchall()

# parts = 'a b c'.split(' ')
# var1, var2, var3, var4 = [parts[i] if i < len(parts) else None for i in range(4)]
#
# if var4 ==  None:
#     mtc = 'http://multitwitch.tv/' + var1 + '/' + var2 + '/' + var3 + '/'
# else:
#     mtc = 'http://multitwitch.tv/' + var1 + '/' + var2 + '/' + var3 + '/' + var4
#
# print(mtc)