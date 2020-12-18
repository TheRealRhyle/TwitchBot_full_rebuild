import os
import sqlite3
import installer

def loaddb():
    conn = sqlite3.connect("dxchatbot.db")
    c = conn.cursor()
    return conn, c

def closedb():
    conn.close()

def loading_seq():
    # Check if db file exists first
    if os.path.isfile('dxchatbot.db'):
        print('Database file exists')
        conn, c = loaddb()
    else:
        botnick = ''
        create = input('No database file currently exists would you like to create one? ').lower()
        if create == 'y' or create == 'yes':
            chathost = input("Enter the chat host(irc.twitch.tv): ").lower()
            botnick = input("Enter your bots name: ").lower()
            while botnick == '':
                botnick = input("You must provide your bots name: ").lower()
            port = input("Enter the port, leave blank if unsure: ")
            pwd = input("Enter your bots oauth token: ")
            while pwd == '':
                pwd = input("You must provide your bots oauth token: ")

            if chathost == "":
                chathost = 'irc.twitch.tv'
            if port == '':
                port = 6667
            if 'oauth:' in pwd:
                print('Thank you, initializing database.')
            else:
                pwd = 'oauth:' + pwd
            installer.installbot(chathost, botnick, port, pwd)

    conn = sqlite3.connect("dxchatbot.db")
    c = conn.cursor()
    lst = c.execute("select * from streamer").fetchall()
    varsx = ['chathost', 'botnick', 'port', 'pwd','readbuffer', 'ClientID', 'Token']
    lst = list(lst[0])
    dictaf = dict(zip(varsx, lst))

    print('Database initialized for {}.'.format(dictaf['botnick']))
    return conn, c

if __name__ == '__main__':
    conn, c = loading_seq()
    reintall_test = input('Do you want to reinitialize the database with different values? ')

    if reintall_test == 'yes':
        chathost = input("Enter the chat host(irc.twitch.tv): ").lower()
        botnick = input("Enter your bots name: ").lower()
        while botnick == '':
            botnick = input("You must provide your bots name: ").lower()
        port = input("Enter the port, leave blank if unsure: ")
        pwd = input("Enter your bots oauth token: ")
        while pwd == '':
            pwd = input("You must provide your bots oauth token: ")

        if chathost == "":
            chathost = 'irc.twitch.tv'
        if port == '':
            port = 6667
        if 'oauth:' in pwd:
            print('Thank you, initializing database.')
        else:
            print('Thank you, initializing database.')
            pwd = 'oauth:' + pwd
        installer.reinstall(chathost, botnick, port, pwd)
    closedb()