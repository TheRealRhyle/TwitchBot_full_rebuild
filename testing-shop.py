def shop(username, *args):
    import itemlist
    shoplist = itemlist.load_shop()
    shop_items = []
    shop_message = ''
    
    if not args:
        shop_message = f"/w {username} Welcome to the shop!  The following commands are necessary for using the shop: " \
            f"!shop melee, ranged, or armor will show you the available weapons.  !shop buy followed by the item you would " \
            f"like to purchase will allow you to purchase that specific item assuming that you have the available crowns."
    elif 'melee' in args[0].lower() or 'ranged' in args[0].lower() or 'armor' in args[0].lower():
        [shop_items.append(f"[{item}] {shoplist[item]['type']} {shoplist[item]['cost']}") for item in shoplist if args[0].lower() in shoplist[item]['type'].lower()]
        print(shop_items)
        shop_items = str(shop_items).replace('[\'','').replace(']\'','').replace("', '"," ").replace("']", "")
        shop_message = f"/w {username} The available items are as follows: {shop_items}"
    elif 'buy' in args[0].lower():
        shopper = ret_char(username)
        shopper_xp, shopper_purse = get_user_exp(username)
        print(len(args))
        if len(args) != 2:
            shop_message = "I'm sorry, I didn't understand that, please try again."
        else:
            new_weapon = args[1].lower()
            if new_weapon not in shoplist:
                shop_message = "No item exists that with that name, please look at the !shop melee, !shop armor or !shop ranged list again."
                return

            crown_cost = shoplist[args[1].lower()]['cost'].split(' ')
            # print(crown_cost[0], shopper_purse)

            if int(shopper_purse) >= int(crown_cost[0]):
                if shoplist[new_weapon.lower()]['type'] == 'Melee' or shoplist[new_weapon.lower()]['type'] == 'Ranged':
                    shopper['weapon'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?",(int(shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper),username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You brandish your new {args[1]}.  It fits your hands " \
                        f"as though it was made for you."
                elif shoplist[new_weapon.lower()]['type'] == 'Armor':
                    shopper['armor'] = args[1]
                    c.execute("update users set crowns = ? where uname = ?",(int(shopper_purse) - int(crown_cost[0]), username))
                    c.execute("update users set gchar = ? where uname = ?", (str(shopper),username))
                    conn.commit()
                    shop_message = shop_message = f"/w {username} You don your new {args[1]}.  The armor fits " \
                        f"as though it was made for you."
            else:
                Send_message(f"/w {username} You do not have enough Crowns to buy the {args[1]}. " \
                    f"Your current purse is {shopper_purse}.")
                return
    print(shop_message)
    # chatmessage = ''

# shop(username, *args)
shop("rhyle_", 'melee')