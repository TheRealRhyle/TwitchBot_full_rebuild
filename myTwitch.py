import requests
import loader
import json
# import othercreds

# curl -X PATCH 'https://api.twitch.tv/helix/channels?broadcaster_id=41245072' \
# -H 'Authorization: Bearer 2gbdx6oar67tqtcmt49t3wpcgycthx' \
# -H 'Client-Id: wbmytr93xzw8zbg0p1izqyzzc5mbiz' \
# -H 'Content-Type: application/json' \
# --data-raw '{"game_id":"33214", "title":"there are helicopters in the game? REASON TO PLAY FORTNITE found", "broadcaster_language":"en"}'

def update_twitch(ClientID, Token, update_info):
    url = 'https://api.twitch.tv/helix/channels?broadcaster_id=38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':'Bearer ' + Token }
    title, game = update_info.split("; ")
    title = title + " | !game !character !crypto"
    game = game.replace("\r",'')
    game_id = get_games(ClientID, Token, game)
    # game_id = 1469308723
    gamedata = f'"title":"{title}", "game_id":"{game_id}"'
    gamedata = "{" + gamedata + "}"
    x = json.loads(gamedata)
    r = requests.patch(url=url, headers=headers, data=x)
    print (r)

def get_games(ClientID, OAuth, Game_Name):
    url = f"https://api.twitch.tv/helix/games?name={Game_Name}"
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + OAuth }
    r = requests.get(url=url, headers=headers).json()
    return r['data'][0]['id']
    
    
def get_status(ClientID, OAuth):
    url = 'https://api.twitch.tv/helix/channels?broadcaster_id=38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + OAuth }
    # title, category = update_info.split(";")
    # title = title.replace(" ", "+")
    # category = category.replace(" ", "+").replace("&","&amp;")
    # gamedata = f'channel[status]={title}&channel[game]={category}&channel[channel_feed_enabled]=false'
    r = requests.get(url=url, headers=headers).json()
    return r

def get_uptime(ClientID, OAuth, Token):
    url = "https://api.twitch.tv/helix/streams?user_login=rhyle_"
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':'Bearer ' + Token}
    r = requests.get(url=url, headers=headers).json()
    return r

def get_current_tags(ClientID, Token):
    url = 'https://api.twitch.tv/helix/streams/tags?broadcaster_id=38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':'Bearer ' + Token }
        # 'Authorization':OAuth
    # r = requests.get(url = url, headers = headers)
    r = requests.get(url = url, headers = headers).json()
    return r

def set_tags(ClientID, Token):
    url = 'https://api.twitch.tv/helix/streams/tags?broadcaster_id=38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/json', 'Authorization':'Bearer ' + Token}
    tags = '{"tag_ids": ["cea7bc0c-75a5-4446-8743-6db031b71550","a59f1e4e-257b-4bd0-90c7-189c3efbf917", \
        "6f86127d-6051-4a38-94bb-f7b475dde109"]}'
    # r = requests.put(url=url, headers=headers, data=tags)
    requests.put(url=url, headers=headers, data=tags)
    
def get_raider_id(ClientID, Token, raider):
    # url = f"https://api.twitch.tv/helix/channels?broadcaster_name={raider}"
    url = f"https://api.twitch.tv/helix/users?login={raider}"
    # url = f'https://api.twitch.tv/kraken/users?login={raider}'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':'Bearer ' + Token}
    r = requests.get(url=url, headers=headers)
    raiderjson = r.json()
    raider_id = raiderjson['data'][0]['id']
    return(get_raider_info(ClientID, Token, raider_id))

def get_raider_info(ClientID, Token, raider_id):
    # url = f'https://api.twitch.tv/kraken/channels/{raider_id}'
    url = f'https://api.twitch.tv/helix/channels?broadcaster_id={raider_id}'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':'Bearer ' + Token }
    # title, category = update_info.split(";")
    # title = title.replace(" ", "+")
    # category = category.replace(" ", "+").replace("&","&amp;")
    # gamedata = f'channel[status]={title}&channel[game]={category}&channel[channel_feed_enabled]=false'
    r = requests.get(url=url, headers=headers).json()
    return(r['data'][0]["game_name"])

if __name__ == "__main__":
    print(get_raider_id("gp762nuuoqcoxypju8c569th9wz7q5", "rbz271cs9omqnggpeaugnkqxqoluqi", "medallionstallion_"))
    pass
    