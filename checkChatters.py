import ast
with open('beastdict.txt', 'r') as f:
    main_dict = f.read()
    main_dict = ast.literal_eval(main_dict)

for key, value in main_dict.items():
    if ' or ' in value['weapon']:
        print(value['name'])