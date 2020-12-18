import threading


def bot_body():
    import bot_body


def chatters_to_db():
    import chattodb
    chattodb.get_chatters()


# def start_playlist():
#     import song_request
#     song_request.start_playlist()

t1 = threading.Thread(target=bot_body, name='main bot')
t2 = threading.Thread(target=chatters_to_db, name='currency')
# t3 = threading.Thread(target=start_playlist, name='playlist')

t1.start()
t2.start()
# t3.start()
