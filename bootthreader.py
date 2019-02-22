import threading

def mainloop():
    import bot_body
    import chattodb

t= threading.Thread(target=mainloop, name='test thread')

t.start()
