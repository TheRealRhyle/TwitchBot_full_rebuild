from random import choice, randint


class Character():
    """ This is going to be a random character generator for twitch.tv/rhyle_
    """

    def __init__(self, name, race, prof, phys, social, mental):
        self.name = name
        self.race = race
        self.prof = prof
        self.phys = phys
        self.social = social
        self.mental = mental

    def retire(self):
        pass

    def permadeath(self):
        pass

    def upgrade(self, category):
        pass

    def physical_combat(self):
        pass

    def social_combat(self):
        pass

    def mental_combat(self):
        pass

    def __str__(self):
        return f"{self.name} is a {self.race} {self.prof} who has {self.phys} physical, {self.social} social, and {self.mental} mental traits."

def chat_char(uname):
    race = choice(['dwarf', 'elf', 'halfling', 'human'])
    phys = randint(1, 10)
    social = randint(1, 10)
    mental = randint(1, 10)
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

    # name,race,prof, phys, social, mental
    chatchar = Character(uname, race, prof, phys, social, mental)
    return chatchar

# print(chatchar)
