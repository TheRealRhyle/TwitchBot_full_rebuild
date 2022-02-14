from random import choice

subject = [
    "My liegelord's",
    "The village",
    "My Dwarven nephew's",
    "My horse's",
    "The Princess's",
    "The innkeeper's",
    "My bastard son's",
]
verb = [
    "codpiece",
    "cheese shed",
    "pet cockatrice",
    "bosom",
    "shrubbery",
    "dainty wrist",
    "court jester",
]
quandry = [
    "is on fyre.",
    "committed treason.",
    "hath been run o'er by an ox cart.",
    "was ravaged by orcs.",
    "was struck by an arrow.",
    "ran out of cheese.",
    "fell afoul of the magistrate.",
]

def make_excuse():
    return (choice(subject), choice(verb), choice(quandry))

if __name__ == "__main__":
    for x in range(10):
        print(' '.join(make_excuse()))