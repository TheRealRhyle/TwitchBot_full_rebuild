
import pafy
import time
import bot_body as b


def add_to_playlist(songlink):
    code = songlink
    try:
        while len(code) > 11:
            code = code.replace('\r', '')
            code = songlink.split("=")[1]
            code = code.split("&")[0]
            
    except:
        pass
    with open('songrequest\\playlist.txt', 'a+') as cs:
        cs.writelines(code)
    url = "https://www.youtube.com/watch?v="
    # creating pafy object of the video
    video = pafy.new(url + code)
    rawstring = video.title
    encoded_string = rawstring.encode("ascii", "ignore")
    decoded_string = encoded_string.decode()

    b.Send_message("The song " + decoded_string + " has been added to the playlist and will be played in order.")
