import schedule
import time
import socket
import urllib
from urllib import request
import json
import sqlite3
import time
import tcChargen

global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()

username = 'rhyle_'
print(c.execute("select gchar from users where uname = ?", (username.lower(),)).fetchone()[0])

# c.execute("insert into users values ('rhyle_', 'moderators')")
# conn.commit()
# c.execute("select * from commands where ex_command = '!multi'").fetchall() != []:

# c.execute("update streamer set nick = 'rhyle_bot' where nick in ('darkxildebot')")
# conn.commit()
# c.execute("""alter table users add gchar text""")
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

