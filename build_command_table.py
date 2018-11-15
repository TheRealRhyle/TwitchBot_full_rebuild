import sqlite3

global conn
global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()

# c.execute('drop table commands')
# conn.commit()
#
# c.execute("""create table commands (
#                 ex_command text,
#                 target text,
#                 action text)""")
# conn.commit()
#
#
# c.execute("""insert into commands values ('!help', '',' the current commands are !insult, !sso, !so, !permit. If I do """ \
#     """not respond to an issued command it is because you are not in my preferred list of users.')""")
# conn.commit()

print(c.execute('select * from commands').fetchall())

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
