import sqlite3

global conn
global c
conn = sqlite3.connect("dxchatbot.db")
c = conn.cursor()

def installbot(host, nick, port, pwd):
    conn = sqlite3.connect("dxchatbot.db")
    readbuff = ''
    c = conn.cursor()
    c.execute("""create table streamer (
                host text,
                nick text,
                port integer,
                pass text,
                readbuffer text)""")
    conn.commit()

    c.execute("insert into streamer values (:host, :nick, :port, :pwd, :readbuff)",
              {'host':host, 'nick':nick, 'port':port, 'pwd':pwd, 'readbuff':readbuff})
    conn.commit()

    oput = c.execute('select * from streamer').fetchall()
    print(oput)
    conn.close()
    print("Database has been created for " + nick + '.')

def build_tables():
    c.execute("""create table mods_subs (
                uname text,
                status text)""")

    c.execute("""create table commands (
                ex_command text,
                target text,
                action text)""")
    conn.commit()

def reinstall(host, nick, port, pwd):
    conn = sqlite3.connect("dxchatbot.db")
    readbuff = ''
    c = conn.cursor()
    c.execute("drop table streamer")
    conn.commit()
    installbot(host, nick, port, pwd)


if __name__ == '__main__':
    build_tables()
    print(c.execute("select * from mods_subs").fetchall())
    print(c.execute("select * from commands").fetchall())