from random import choice, randint
import ast


class Character:
    """ This is going to be a random character generator for twitch.tv/rhyle_
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
        char_dict =  {'name': '', 'race':'', 'prof':'', 'weapon_skill':'', 'ballistic_skill':'', 'strength':'',
                      'toughness':'', 'armor':'','weapon':'', 'max_wounds':'', 'current_wounds':''}
        char_ = [self.name, self.race, self.prof, self.ws, self.bs, self.s, self.t, self.armor, self.weapon, self.max_wounds, self.current_wounds]
        return dict(zip(char_dict, char_))
    # def __str__(self):
    #     return f"""{self.name} is a {self.race} {self.prof} who has {self.ws} weapon skill, {self.bs} ballistic skill,
    #     and {self.s} strength, and {self.t} toughness."""

    def take_damage(self, name, amount):
        pass

def base_char(uname):
    char_dict =  {'name': '', 'race':'', 'prof':'', 'weapon_skill':'', 'ballistic_skill':'', 'strength':'',
                      'toughness':'', 'armor':'','weapon':'', 'max_wounds':'', 'current_wounds':''}
    char_ = [uname, 'human', 'peasant', 20, 20, 20,20, 'none', 'fists', 10, 10]
    return dict(zip(char_dict, char_))


def chat_char(uname):
    race = choice(['dwarf', 'elf', 'halfling', 'human'])
    stats_dict = {'WS': 0, 'BS': 0, 'S': 0, 'T': 0, 'MW': 0, 'CW':0}

    if race == 'dwarf':
        max_wounds = choice([11,12,13,14])
        stats = [30, 20, 20, 30]

    elif race == 'elf':
        max_wounds = choice([9,10,11,12])
        stats = [20, 30, 20, 20]

    elif race == 'halfling':
        max_wounds = choice([8,9,10,11])
        stats = [10, 30, 10, 10]

    elif race == 'human':
        max_wounds = choice([10,11,12,13])
        stats = [20, 20, 20, 20]

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

# ch = (chat_char('test'))
#
# print(type(str(ch.get_char('test'))))
# print(str(ch.get_char('test')))
# print(*ch.get_char("test"), sep='\n')


