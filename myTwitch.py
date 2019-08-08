import requests
import othercreds

def update_twitch(update_info):
    url = 'https://api.twitch.tv/kraken/channels/38847203'
    headers = {'Client-ID':othercreds.ClientId, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':othercreds.OAuth }
    title, category = update_info.split(";")
    title = title.replace(" ", "+")
    category = category.replace(" ", "%20").replace("&","%26").replace("\r",'')
    gamedata = f'channel[status]={title}&channel[game]={category}&channel[channel_feed_enabled]=false'
    r = requests.put(url=url, headers=headers, data=gamedata).json()
    print(r)

def get_status():
    url = 'https://api.twitch.tv/kraken/channels/38847203'
    headers = {'Client-ID':othercreds.ClientId, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':othercreds.OAuth }
    # title, category = update_info.split(";")
    # title = title.replace(" ", "+")
    # category = category.replace(" ", "+").replace("&","&amp;")
    # gamedata = f'channel[status]={title}&channel[game]={category}&channel[channel_feed_enabled]=false'
    r = requests.get(url=url, headers=headers).json()
    print(r)

def get_current_tags():
    url = 'https://api.twitch.tv/helix/streams/tags?broadcaster_id=38847203'
    headers = {'Client-ID':othercreds.ClientId, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/x-www-form-urlencoded', 'Authorization':othercreds.OAuth }
    r = requests.get(url = url, headers = headers)
    print(r.text)

def set_tags():
    url = 'https://api.twitch.tv/helix/streams/tags?broadcaster_id=38847203'
    headers = {'Client-ID':othercreds.ClientId, 'Accept':'application/vnd.twitchtv.v5+json', \
        'Content-Type': 'application/json', 'Authorization':othercreds.OAuth, \
            'Scope':'user:edit+user:read:email+user:edit:broadcast'}
    tags = '{"tag_ids": ["cea7bc0c-75a5-4446-8743-6db031b71550","a59f1e4e-257b-4bd0-90c7-189c3efbf917", \
        "6f86127d-6051-4a38-94bb-f7b475dde109"]}'
    r = requests.put(url=url, headers=headers, data=tags)
    print(r.text)
# curl -H 'Client-ID: uo6dggojyb8d6soh92zknwmi5ej1q2' \
# -X PUT 'https://api.twitch.tv/helix/streams/tags?broadcaster_id=257788195' \
# -H 'Content-Type: application/json' \
# -d '{"tag_ids": ["621fb5bf-5498-4d8f-b4ac-db4d40d401bf","79977fb9-f106-4a87-a386-f1b0f99783dd"]}'
