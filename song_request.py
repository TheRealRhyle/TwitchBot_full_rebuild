import vlc
import pafy
import time
import bot_body as b
play_list_status = False

vlcInstance = vlc.Instance()
mplayer = vlcInstance.media_player_new()

def start_playlist():
    play_list_status = True

    while True:

        with open('songrequest\\playlist.txt', 'r+') as cs:
            playlist = cs.readlines()

        with open('songrequest\\playlist.txt', 'w+') as cs:
            for song in playlist:
                if song.strip('\n') != playlist[0].strip('\n'):
                    cs.write(song)
        time.sleep(1)
        try:
            play(playlist[0])
        except:
            continue


def play(playlist0, *argv):
    # with open('songrequest\\playlist.txt', 'r+') as playlist:
    #     # playlist.seek(0)
    #     songs = playlist.readlines()

    for arg in argv:
        if arg == "skip":
            skip = True

    url = "https://www.youtube.com/watch?v="

    # creating pafy object of the video
    video = pafy.new(url + playlist0)

    # getting best stream
    best = video.getbest()

    # creating vlc media player object
    # media = vlc.MediaPlayer(best.url)
    # vlcInstance = vlc.Instance()
    media = vlcInstance.media_new(best.url)

    mplayer.set_media(media)
    mplayer.audio_set_volume(40)
    mplayer.play()

    # media.audio_set_volume(50)
    rawstring = video.title
    encoded_string = rawstring.encode("ascii", "ignore")
    decoded_string = encoded_string.decode()
    print(decoded_string)

    # start playing video
    # media.play()
    time.sleep(1)
    with open('songrequest\\current_song.txt', 'r+') as cs:
        cs.writelines("     ..." + decoded_string + "...", )

    # while mplayer.is_playing():
    b.Send_message("Now playing: " + decoded_string + " " + video.duration)

    while mplayer.is_playing() == True:
        continue

    played(playlist0)
    mplayer.stop()
    time.sleep(1)


# def update_playlist(songlink):
def played(songlink):
    with open('songrequest\\playlist.txt', 'r+') as cs:
        playlist = cs.readlines()

    with open('songrequest\\playlist.txt', 'w+') as cs:
        for song in playlist:
            if song.strip('\n') != songlink.strip('\n'):
                cs.write(song)


def skip():
    mplayer.stop()

# def add_to_playlist(songlink):
#     code = songlink
#     try:
#         while len(code) > 11:
#             code = songlink.split("=")[1]
#             code = code.split("&")[0]
#             code = code.replace('\r', '')
#     except:
#         pass
#     with open('songrequest\\playlist.txt', 'a+') as cs:
#         cs.writelines(code)
#     url = "https://www.youtube.com/watch?v="
#     # creating pafy object of the video
#     video = pafy.new(url + code)
#     rawstring = video.title
#     encoded_string = rawstring.encode("ascii", "ignore")
#     decoded_string = encoded_string.decode()

#     return ("The song " + decoded_string + " has been added to the playlist and will be played in order.")

# start_playlist()


def delete():
    pass


def ban():
    pass


if __name__ == '__main__':
    start_playlist()

    # # url of the video
    # url = "https://www.youtube.com/watch?v="

    # songs.append(code.replace("\r", ""))

    # # creating pafy object of the video
    # video = pafy.new(url + songs[0])

    # # getting best stream
    # best = video.getbest()

    # # creating vlc media player object
    # media = vlc.MediaPlayer(best.url)
    # media.audio_set_volume(50)
    # rawstring = video.title
    # encoded_string = rawstring.encode("ascii", "ignore")
    # decoded_string = encoded_string.decode()
    # print(decoded_string)

    # # start playing video
    # # media.play()

    # with open('songrequest\\current_song.txt', 'w+') as cs:
    #     cs.writelines("     ..." + decoded_string + "...", )

    # while media.is_playing():

    #     pass

    # return ("The song " + decoded_string + " has been added to the playlist and will be played in order.")

    # string = dir(vlc)
    # for x in string:
    #     print(x)
    # iHR8JsfzpdU
    # B9FzVhw8_bY
    # LOZuxwVk7TU
    # E07s5ZYygMg
