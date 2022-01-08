from playsound import playsound

def playme(sound_name):
    if sound_name == "test":
        playsound(r"F:\Google Drive\Stream Assets\Sounds\Good night Beaz.mp4")
    elif sound_name == "beaz":
        playsound(r"F:\Google Drive\Stream Assets\Sounds\hello_motherfrucker.mp3")
    elif sound_name == "faerie":
        playsound(r"F:\Google Drive\Stream Assets\Sounds\surprise-motherfucker.mp3")
    elif sound_name == "fts":
        playsound(r"F:\Google Drive\Stream Assets\Sounds\fuck-this-shit-im-out.mp3")
    else:
        
        playsound(fr"F:\Google Drive\Stream Assets\Sounds\Death\{sound_name}")

if __name__ == "__main__":
    playme("chips")