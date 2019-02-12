import urllib
from urllib import request
import json
import sqlite3
import time
global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()
import schedule
import time
import socket
user = 'jtn2002'


# c.execute("insert into users values ('rhyle_', 'moderators')")
# conn.commit()
# c.execute("select * from commands where ex_command = '!multi'").fetchall() != []:

c.execute("update users set status = 'fots' where uname in ('orphenadler')")
conn.commit()

print(str(c.execute("select * from users where status not in ('bot', 'fots', 'moderators')").fetchall()).replace('),','\n'))

# if c.execute("select * from commands where ex_command = '!multi'").fetchall() != []:
#     print('not empty')
# print(c.execute("select * from commands where ex_command = '!multi'").fetchall())
# print(c.execute('select ex_command from commands').fetchall())
# streamr = c.execute('select * from streamer').fetchall()