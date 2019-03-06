import random


class Weapon:
    def __init__(self, weapon_dict):
        self.Weapon_dict = weapon_dict
        self.max_hit = weapon_dict['max_hit']
        self.min_hit = weapon_dict['min_hit']
        self.spec_used = weapon_dict['spec_used']
        self.times_hit = weapon_dict['times_hit']

        self.damage = self.generate_damage()
        self.heal = 0
        self.poison = weapon_dict['poison']
        self.freeze = weapon_dict['freeze']

    def generate_damage(self):
        dmg = []
        for hit in range(self.times_hit):
            c_hit = random.randint(self.min_hit, self.max_hit + 1)
            dmg.append(c_hit)
        return dmg
