from playsound import playsound

def playme(sound_name):
    if sound_name == "test":
        playsound(r"sounds\hello_motherfrucker.mp3")
    elif sound_name == "beaz":
        playsound(r"sounds\GNB-shortened.mp3")
    elif sound_name == "faerie":
        playsound(r"sounds\surprise-motherfucker.mp3")
    elif sound_name == "fts":
        playsound(r"sounds\fuck-this-shit-im-out.mp3")
    else:
        
        playsound(fr"sounds\Death\{sound_name}")

if __name__ == "__main__":
    playme("beaz")