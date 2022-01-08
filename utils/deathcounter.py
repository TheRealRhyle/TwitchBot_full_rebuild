from pathlib import Path
import shutil

deathcounter_path = Path(r'F:\Google Drive\May 2020\TwitchBot_full_rebuild\utils\dc_files')

def increment_death_count(character):
    """[Used to increment the number of deaths for the current character]

    Args:
        character ([string]): [the character name that is currently being used]
    """
    with open(f'{deathcounter_path}\{character}.txt', 'r+') as dcf:
        death_counter = dcf.readlines()
        new_death_count = int(death_counter.pop()) + 1
        death_counter.append(str(new_death_count))
        dcf.seek(0)
        dcf.writelines(death_counter)

    with open(f'{deathcounter_path}\current_tracked_character.txt', 'r+') as dcf:
        death_counter = dcf.readlines()
        new_death_count = int(death_counter.pop()) + 1
        death_counter.append(str(new_death_count))
        dcf.seek(0)
        dcf.writelines(death_counter)

def create_death_counter_file(character, deaths, character_class='Survivor'):
    """[If the file for the current character doesn't exist, create one.]

    Args:
        character ([string]): [The character name, this should include 
            -servername if playing a server based game]
        character_class ([string]): [The class of the character if playing 
            an MMO otherwise should default to 'Survivor']
        deaths ([string]): [The current number of deaths.]
    """
    file_exists = Path.is_file(Path(f'{deathcounter_path}\\{character}.txt'))
    if not file_exists:
        with open(f'{deathcounter_path}\\{character}.txt', 'w') as dcf:
            dcf.writelines('\n'.join(
                [character.split('-')[0].title(), character_class.title(), str(deaths)]))
    
    # Copy new tracked character to the standard file displayed on twitch.
    character_file = f'{deathcounter_path}\\{character}.txt'
    display_file = f'{deathcounter_path}\current_tracked_character.txt'
    shutil.copyfile(character_file, display_file)
        

if __name__ == "__main__":
    #call increment_death_count and supply the current character info.
    # create_death_counter_file('Shorofro-Quellious',0, 'Ranger')
    increment_death_count('Shorofro-Quellious')
    