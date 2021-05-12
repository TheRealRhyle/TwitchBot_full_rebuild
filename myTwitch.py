import requests
import loader
# import othercreds

def update_twitch(ClientID, OAuth, update_info):
    url = 'https://api.twitch.tv/kraken/channels/38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':OAuth }
    title, category = update_info.split("; ")
    title = title.replace(" ", "+")
    category = category.replace(" ", "%20").replace("&","%26").replace("\r",'')
    gamedata = f'channel[status]={title}&channel[game]={category}&channel[channel_feed_enabled]=false'
    r = requests.put(url=url, headers=headers, data=gamedata).json()
    print(r)

def get_status(ClientID, OAuth):
    url = 'https://api.twitch.tv/kraken/channels/38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':OAuth }
    # title, category = update_info.split(";")
    # title = title.replace(" ", "+")
    # category = category.replace(" ", "+").replace("&","&amp;")
    # gamedata = f'channel[status]={title}&channel[game]={category}&channel[channel_feed_enabled]=false'
    r = requests.get(url=url, headers=headers).json()
    print(r)

def get_current_tags(ClientID, OAuth):
    url = 'https://api.twitch.tv/helix/streams/tags?broadcaster_id=38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':OAuth }
    # r = requests.get(url = url, headers = headers)
    requests.get(url = url, headers = headers)
    # print(r.text)

def set_tags(ClientID, OAuth):
    url = 'https://api.twitch.tv/helix/streams/tags?broadcaster_id=38847203'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/json', 'Authorization':OAuth, \
            'Scope':'user:edit+user:read:email+user:edit:broadcast'}
    tags = '{"tag_ids": ["cea7bc0c-75a5-4446-8743-6db031b71550","a59f1e4e-257b-4bd0-90c7-189c3efbf917", \
        "6f86127d-6051-4a38-94bb-f7b475dde109"]}'
    # r = requests.put(url=url, headers=headers, data=tags)
    requests.put(url=url, headers=headers, data=tags)
    
def get_raider_id(ClientID, OAuth, raider):
    url = f'https://api.twitch.tv/kraken/users?login={raider}'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':OAuth }
    r = requests.get(url=url, headers=headers)
    raiderjson = r.json()
    raider_id = raiderjson['users'][0]['_id']
    return(get_raider_info(ClientID, OAuth, raider_id))
    
def get_raider_info(ClientID, OAuth, raider_id):
    url = f'https://api.twitch.tv/kraken/channels/{raider_id}'
    headers = {'Client-ID':ClientID, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':OAuth }
    # title, category = update_info.split(";")
    # title = title.replace(" ", "+")
    # category = category.replace(" ", "+").replace("&","&amp;")
    # gamedata = f'channel[status]={title}&channel[game]={category}&channel[channel_feed_enabled]=false'
    r = requests.get(url=url, headers=headers).json()
    return(r["game"])

if __name__ == "__main__":
    pass
    