# import random

# # [("{'name': 'ceacelion', 'race': 'human', 'prof': 'Smuggler', 
# # 'weapon_skill': 29, 'ballistic_skill': 37, 'strength': 30, 'toughness': 37, 
# # 'armor': 'None', 'weapon': 'Fists'}",)]

# # name, ws, bs, s, t, armor, weapon
# beastiary_template = ['name:', 'ws:', 'bs:', 's:', 't:', 'armor:', 'weapon:']
# beastiary = {}

# idx = 0
# while True:
#     # name, ws, bs, s, t, armor, weapon 
#     beast_list =  input("Beastiary Item: ").split(' ')
#     beast_dict = dict(zip(beastiary_template,beast_list))
#     if beast_list[0] != 'done':
#         idx += 1
#         beastiary[idx]=beast_dict
#         print(beastiary[idx])
#     else:
#         with open('beastiary.txt', 'w+') as b:
#             b.write(str(beastiary))
#         exit(0)

from chattodb import social_ad

ad = social_ad()
print(ad)
