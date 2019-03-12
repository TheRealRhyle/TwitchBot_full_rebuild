def load_shop():
    import ast
    with open("itemlist.txt", 'r') as shop:
        itemlist = shop.read()
        itemlist = ast.literal_eval(itemlist)
    return itemlist

if __name__ == "__main__":
    itemlist= load_shop()
    for item in itemlist.keys():
        print(item + ": " + itemlist[item]['cost'])