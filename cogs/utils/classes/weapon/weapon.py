import random


class Weapon:
    def __init__(self, weapon_dict, match_data):
        self.Weapon_dict = weapon_dict
        self.match_data = match_data
        self.max_hit = weapon_dict['max_hit']
        self.min_hit = weapon_dict['min_hit']
        self.spec_used = weapon_dict['spec_used']
        self.times_hit = weapon_dict['times_hit']

        self.damage = self.generate_damage()
        self.heal = self.generate_heal(weapon_dict['base_heal'])
        self.poison = weapon_dict['poison']
        self.freeze = weapon_dict['freeze']

    def generate_damage(self):
        dmg = []
        for hit in range(self.times_hit):
            c_hit = random.randint(self.min_hit, self.max_hit)
            dmg.append(c_hit)
        return dmg

    def generate_heal(self, heal):
        return heal


class Blood(Weapon):
    def __init__(self, weapon_dict, match_data):
        Weapon.__init__(self, weapon_dict, match_data)

    def generate_heal(self, heal):
        return int(sum(self.damage) * 0.75)


class Sgs(Weapon):
    def __init__(self, weapon_dict, match_data):
        Weapon.__init__(self, weapon_dict, match_data)

    def generate_heal(self, heal):
        return int(sum(self.damage) * 0.5)


class Dharoks(Weapon):
    def __init__(self, weapon_dict, match_data):
        Weapon.__init__(self, weapon_dict, match_data)

    def generate_damage(self):
        dmg = super().generate_damage()[0]
        modify = 1.0 + ((99 - self.match_data['player'][self.match_data['match']['attacker']]['hp']) / 100)

        if modify > 1.0:
            dmg *= modify

        return [int(dmg)]


class Guth(Weapon):
    def __init__(self, weapon_dict, match_data):
        Weapon.__init__(self, weapon_dict, match_data)

    def generate_heal(self, heal):
        roll = random.randint(1, 3)

        if roll == 1:
            heal += self.damage[0]

        return heal
