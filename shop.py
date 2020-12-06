weapons = []
shop_dict = {}

weapon_profile = ['type','cost', 'damage']
weapon_type = 'melee'

with open("shop.txt", 'r') as shop:
    for line in shop:
        weapon_list = line.replace('\n','').split(', ')
        weapons.append(weapon_list)

for item in range(len(weapons)):
    wname = weapons[item][0]
    wdict = dict(zip(weapon_profile, weapons[item][1:]))
    shop_dict[wname] = wdict
    # print(weapons[item][0], dict(zip(weapon_profile, weapons[item][1:])))
    # shop[weapons[item][0]] = dict(zip(weapon_profile, weapons[item]))

print (shop_dict)
with open("itemlist.py", 'w') as itemlist:
    itemlist.write(str(shop_dict))