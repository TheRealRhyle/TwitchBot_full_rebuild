import threading


def mainloop():
    import bot_body


t= threading.Thread(target=mainloop, name='test thread')

t.start()
