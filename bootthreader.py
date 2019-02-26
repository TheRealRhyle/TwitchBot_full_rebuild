import threading


def bot_body():
    import bot_body

def chatters_to_db():
    import chattodb
    chattodb.get_chatters()

t1 = threading.Thread(target=bot_body, name='main bot')
t2 = threading.Thread(target=chatters_to_db, name='currency')

t1.start()
t2.start()
