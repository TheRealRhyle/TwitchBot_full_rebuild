from random import choice, randint
import ast


class Character:
    """ Character Class for idle chat game
        methods: 
            get_char: requires username
            take_damage: requires username, amount
            heal_damage: requires username, amount
            level_up: requires which stat.
    """
    def __init__(self, name, race, prof, weapon_skill, ballistic_skill, strength, toughness, armor, weapon, max_wounds, current_wounds):
        self.name = name
        self.race = race
        self.prof = prof
        self.ws = weapon_skill
        self.bs = ballistic_skill
        self.s = strength
        self.t = toughness
        self.armor = armor
        self.weapon = weapon
        self.max_wounds = max_wounds
        self.current_wounds = current_wounds

    def get_char(self, name):
        """Converts String character into dictionary

        Args:
            name (string): twitch viewer name

        Returns:
            Dictionary: character dict
        """
        char_dict =  {'name': '', 'race':'', 'prof':'', 'weapon_skill':'', 'ballistic_skill':'', 'strength':'',
                      'toughness':'', 'armor':'','weapon':'', 'max_wounds':'', 'current_wounds':''}
        char_ = [self.name, self.race, self.prof, self.ws, self.bs, self.s, self.t, self.armor, self.weapon, self.max_wounds, self.current_wounds]
        return dict(zip(char_dict, char_))

    def take_damage(self, name, amount):
        if self.current_wounds - amount <=0:
            self.current_wounds = 0
            isDead = True
        else:
            self.current_wounds -= amount
    
    def heal_damage(self, name, amount):
        if self.current_wounds + amount > self.max_wounds:
            self.current_wounds = self.max_wounds
        else:
            self.current_wounds += amount

    def level_up(self, stat):
        if stat == "ws":
            self.ws += 5
        elif stat == "bs":
            self.bs += 5
        elif stat == "s":
            self.s += 5
        elif stat == "t":
            self.t += 5
        elif stat == 'w':
            if self.max_wounds <= 20:
                self.max_wounds += 1
                self.current_wounds += 1
            else:
                print("max wounds already at 20")

def base_char(uname):
    """Creates basic template character for anyone new to the chat.

    Args:
        uname (string): twitch viewer name

    Returns:
        dictionary: basic character
    """
    char_dict =  {'name': '', 'race':'', 'prof':'', 'weapon_skill':'', 'ballistic_skill':'', 'strength':'',
                      'toughness':'', 'armor':'','weapon':'', 'max_wounds':'', 'current_wounds':''}
    char_ = [uname, 'human', 'peasant', 20, 20, 20,20, 'none', 'fists', 10, 10]
    return dict(zip(char_dict, char_))

def chat_char(uname):
    """Generates random character based on WFRP 2nd ed

    Args:
        uname (string): the twitch viewer

    Returns:
        Character: instance of the Character class.
    """
    race = choice(['dwarf', 'elf', 'halfling', 'human'])
    stats_dict = {'WS': 0, 'BS': 0, 'S': 0, 'T': 0, 'MW': 0, 'CW':0}

    if race == 'dwarf':
        max_wounds = choice([11,12,13,14])
        stats = [30, 20, 20, 30, max_wounds, max_wounds]

    elif race == 'elf':
        max_wounds = choice([9,10,11,12])
        stats = [20, 30, 20, 20, max_wounds, max_wounds]

    elif race == 'halfling':
        max_wounds = choice([8,9,10,11])
        stats = [10, 30, 10, 10, max_wounds, max_wounds]

    elif race == 'human':
        max_wounds = choice([10,11,12,13])
        stats = [20, 20, 20, 20, max_wounds, max_wounds]

    stat_prof  = [stat + randint(2, 20) for stat in stats]
    
    stats_dict = dict(zip(stats_dict, stat_prof))

    # phys = randint(1, 10)
    # social = randint(1, 10)
    # mental = randint(1, 10)
    prof = choice(['Agitator', 'Apprentice Wizard', 'Bailiff', 'Barber-Surgeon', 'Boatman', 'Bodyguard', 'Bone Picker',
                   'Bounty Hunter', 'Burgher', 'Camp Follower', 'Charcoal-Burner', 'Coachman', 'Entertainer', 'Envoy',
                   'Estalian Diestro', 'Ferryman', 'Fieldwarden', 'Fisherman', 'Grave Robber', 'Hedge Wizard', 'Hunter',
                   'Initiate', 'Jailer', 'Kislevite Kossar', 'Kithband Warrior', 'Marine', 'Mercenary', 'Messenger',
                   'Militiaman', 'Miner', 'Noble', 'Norse Berserker', 'Outlaw', 'Outrider', 'Peasant', 'Pit Fighter',
                   'Protagonist', 'Rat Catcher', 'Roadwarden', 'Rogue', 'Runebearer', 'Scribe', 'Seaman', 'Servant',
                   'Shieldbreaker', 'Smuggler', 'Soldier', 'Squire', 'Student', 'Thief', 'Thug', 'Toll Keeper',
                   'Tomb Robber',
                   'Tradesman', 'Troll Slayer', 'Vagabond', 'Valet', 'Watchman', 'Woodsman', 'Zealot', 'Anointed Priest',
                   'Artisan', 'Assassin', 'Captain', 'Cat Burglar', 'Champion', 'Charlatan', 'Coutier', 'Daemon Slayer',
                   'Demagogue', 'Duellist', 'Engineer', 'Explorer', 'Fence', 'Flagellant', 'Friar', 'Ghost Strider',
                   'Giant Slayer', 'Guild Master', 'Herald', 'High Priest', 'Highwayman', 'Innkeeper', 'Interrogator',
                   'Journeyman Wizard', 'Judicial Champion', 'Knight', 'Knight of the Inner Circle', 'Master Thief',
                   'Master Wizard', 'Mate', 'Merchant', 'Minstrel', 'Navigator', 'Noble Lord', 'Outlaw Chief', 'Physician',
                   'Pistolier', 'Politician', 'Priest', 'Racketeer', 'Scholar', 'Scout', 'Sea Captain', 'Sergeant', 'Spy',
                   'Steward', 'Targeteer', 'Vampire Hunter', 'Veteran', 'Witch Hunter', 'Wizard Lord'])

    armor = 'none'
    weapon = 'fists'
    # name, race, prof, weapon_skill, ballistic_skill, strength, toughness, armor, weapon

    chatchar = Character(uname, race, prof, stats_dict['WS'], stats_dict['BS'], stats_dict['S'], stats_dict['T'],
                         armor, weapon, max_wounds, max_wounds)

    return chatchar


if __name__ == "__main__":
    a= chat_char("testuser")
    print(a.get_char("testuser"))
    a.take_damage("testuser", 5)
    print(a.get_char("testuser"))
    a.heal_damage("testuser", 100)
    print(a.get_char("testuser"))
    a.level_up("ws")
    a.level_up("bs")
    a.level_up("s")
    a.level_up("t")
    a.level_up("w")
    print(a.get_char("testuser"))
    

# ch = (chat_char('test'))
#
# print(type(str(ch.get_char('test'))))
# print(str(ch.get_char('test')))
# print(*ch.get_char("test"), sep='\n')


