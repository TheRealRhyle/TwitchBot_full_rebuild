import ast
import random

def choose_mob():
    with open('beastdict.txt', 'r') as f:
        main_dict = f.read()
        main_dict = ast.literal_eval(main_dict)

    # for ite in range(1,50):
    #     type_selection = random.randint(1, 100)
    #     if type_selection > 75:
    #         creature_type = main_dict[random.choice(list(main_dict)[:8])]
    #     else:
    #         creature_type = main_dict['Normal']
    #     print(creature_type)
    return main_dict[random.choice(list(main_dict)[10:])]


if __name__ == "__main__":
    print(choose_mob())

# creature_type = main_dict[random.choice(list(main_dict)[:8])]
# creature_type = main_dict[random.choice()]

# for i in range(10):
#     creature_type = main_dict[random.choice(list(main_dict)[1:10])]
#     print(creature_type['name'])
# print(main_dict[random.choice(list(main_dict)[10:])])
