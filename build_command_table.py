import sqlite3
import ast
import random

global conn
global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()

# USER STATUS
# ('vips', [])
# ('moderators', [])
# ('staff', [])
# ('admins', [])
# ('global_mods', [])
# ('viewers', [])
# ('subs', []) - custom
# ('fots', []) - custom

# c.execute("""create table users (
#                 uname text,
#                 status text)""")
# conn.commit()

# c.execute("""insert into users values ('Zangeru13','fots')""")

# c.execute("""update users
#             set status = ''
#             where uname = 'spookeriffic'""")


# c.execute("""delete from users where uname = 'zangeru13'""")
# conn.commit()
# if (c.execute("""select gchar from users where uname='rhyle_'""").fetchone() == ("",)):
#     print("not")
# else:
#     print(c.execute("""select gchar from users where uname='rhyle_'""").fetchone())

# ulist = c.execute("""select * from users""").fetchall()
# print(ulist)
# c.execute('drop table commands')
# conn.commit()
#
# c.execute("""create table commands (
#                 ex_command text,
#                 target text,
#                 action text)""")
# conn.commit()
# #
# #
# c.execute("""insert into commands values ('!help', '',' the current commands are !help. If I do """ \
#     """not respond to an issued command it is because you are not in my preferred list of users.')""")
# conn.commit()


# tab = c.execute('select * from streamer').fetchall()
# print(len(tab))
# for i in range(len(tab)):
#     print(tab[i])
#
# c.execute("""update commands
#     set action = 'Find me on twitter to get stream updates and notifications when I go live! @dxstreaming twitter.com/dxstreaming'
#     where ex_command = '!twitter'""")
# conn.commit()

# c.execute("""update commands
#                 set action = ' this command is being worked on.  there are currently no user triggerable commands other than !help (or are there?)'
#                 where ex_command = '!help'""")
# conn.commit()

# c.execute('delete from commands where ex_command = "!discord"')
# conn.commit()


# print(type(c.execute("select count (*) from commands")))
# command_count = list(c.execute("select count (*) from commands"))
# command_count = int(command_count[0][0])
# for itr in range(command_count):
#
#
# print(command_count)
#
with open('beastdict.txt', 'r') as f:
    main_dict = f.read()
    main_dict = ast.literal_eval(main_dict)


for key in main_dict:
    # c.execute("""insert into users values ('Zangeru13','fots')""")
    # print((str(main_dict[key])))
    # print(f"""insert into mobs values ("{str(key).lower()}","{str(main_dict[key])}")""")
    c.execute(f"""insert into mobs values ("{str(key).lower()}","{str(main_dict[key])}")""")
    conn.commit()