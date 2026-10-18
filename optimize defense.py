import json
import math
import tkinter as tk
from tkinter import messagebox, ttk

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import argparse
import pathlib
import json

def damage(defense_evs, base_defense, def_mult=1, atk=150, power=100, level=50, bonus=[1]):
    calculated_defense = math.floor((base_defense + defense_evs + 20) * def_mult)

    raw_damage = math.floor((( ( (2 * level / 5) + 2) * power * ( (atk) / calculated_defense) ) / 50) + 2 )
    raw_damage_unrounded = (( ( (2 * level / 5) + 2) * power * ( (atk) / calculated_defense) ) / 50) + 2

    for b in bonus:
        raw_damage = round(raw_damage * b)
        raw_damage_unrounded = raw_damage_unrounded * b

    return raw_damage, raw_damage_unrounded

def damage_percent(defense_evs, health_evs, base_health, base_defense, total_evs=50, def_mult=1, atk=150, power=100, level=50, bonus=[1]):
    if (defense_evs + health_evs) > total_evs:  # Constraint check
        #print("EV distribution exceeds total EV limit.")
        return None, None  # Invalid solution
    
    calculated_health = base_health + health_evs + 75
    raw_damage, raw_damage_unrounded = damage(defense_evs, base_defense, def_mult, atk, power, level, bonus)

    return raw_damage / calculated_health * 100, raw_damage



def main(attacks, defenses):
    #Targets x Parental Bond x Weather x GlaiveRush x Critical x random x STAB x Type(Super Effective) x Burn x other x ZMove x TeraShield
    #items like fairy feather are given straight to power
    #most abilities are given straight to power too

    for defense in defenses:

        starting_base_health = defense['base_health']
        starting_base_defense = defense['base_defense']
        starting_base_special_defense = defense['base_special_defense']
        level = 50

        total_evs = defense['total_evs'] if 'total_evs' in defense else 50

        evs_map = np.zeros((33, 33))

        attackN = 0
        for a in attacks:
            print(f"Optimizing for {a['name']}...")
            for i, hp in enumerate(range(0, 33)):
                for j, defense in enumerate(range(0, 33)):
                    base_defense = starting_base_defense if a['PhySpec'] == "Physical" else starting_base_special_defense
                    evs_map[i, j], raw = damage_percent(defense_evs = defense, health_evs = hp, base_health = starting_base_health, base_defense = base_defense, total_evs = total_evs, def_mult = 1, atk = a['atk'], power = a['power'], level = level, bonus = a['bonus'])
                    #print(f"HP EVs: {hp}, Defense EVs: {defense}, Damage Percent: {evs_map[i, j]}, Raw Damage: {raw}")
                    attacks[attackN]['evs'].append((hp, defense, evs_map[i, j]))

            attackN += 1

        #attach the lowest defense percent and lowest special defense percent to each unique hp evs value for each attack

        #create dict with a evs key for 1-32
        optimized_evs = {hp: {"defense": None, "special_defense": None} for hp in range(33)}

        for a in attacks:
        # print(a)
            #for each hp ev value get the lowest defense evs and lowest special defense evs and attach to optimized_evs dict
            for hp in range(33):
                #print(a['evs'])

                        #gets ev1 and 2 for corrosponding hp
                pairs = [(ev[1], ev[2]) for ev in a['evs'] if ev[0] == hp and ev[2] is not None]
                if not pairs:
                    continue

                            #gets evs and damage for all pairs where dmg < 100
                under_100 = [(d_ev, dmg) for d_ev, dmg in pairs if dmg < 100]
                #runs min on under_100 or pairs at [0]
                if under_100:
                    min_defense_evs, chosen_damage = min(under_100, key=lambda x: x[0])
                else:
                    min_defense_evs, chosen_damage = min(pairs, key=lambda x: x[0])

                if a['PhySpec'] == "Physical":
                    if optimized_evs[hp]['defense'] is None or min_defense_evs > optimized_evs[hp]['defense']:
                        optimized_evs[hp]['defense'] = min_defense_evs
                        optimized_evs[hp]['defense_percent'] = chosen_damage
                else:
                    if optimized_evs[hp]['special_defense'] is None or min_defense_evs > optimized_evs[hp]['special_defense']:
                        optimized_evs[hp]['special_defense'] = min_defense_evs
                        optimized_evs[hp]['special_defense_percent'] = chosen_damage

        #for each set of optimized evs find the one with the least evs total (hp, def, spD) and attach it to optimized evs
        for hp in range(33):
                
            if (any(attack["PhySpec"] == "Physical" for attack in attacks) and optimized_evs[hp]['defense'] is None) or (any(attack["PhySpec"] == "Special" for attack in attacks) and optimized_evs[hp]['special_defense'] is None) or (any(attack["PhySpec"] == "Physical" for attack in attacks) and optimized_evs[hp]['defense_percent'] >= 100) or (any(attack["PhySpec"] == "Special" for attack in attacks) and optimized_evs[hp]['special_defense_percent'] >= 100):
                #remove key
                del optimized_evs[hp]
                continue
            defense_evs = 0 if optimized_evs[hp]['defense'] is None else optimized_evs[hp]['defense']
            special_defense_evs = 0 if optimized_evs[hp]['special_defense'] is None else optimized_evs[hp]['special_defense']
            total_evs = hp + defense_evs + special_defense_evs
            optimized_evs[hp]['total_evs'] = total_evs

        #print min total evs and corresponding hp, defense, and special defense evs
        min_total_evs = min([optimized_evs[hp]['total_evs'] for hp in optimized_evs])
        best_evs = None
        for hp in optimized_evs:
            if optimized_evs[hp]['total_evs'] == min_total_evs:
                # print(f"Optimal HP EVs: {hp}, Optimal Defense EVs: {optimized_evs[hp]['defense']}, Optimal Special Defense EVs: {optimized_evs[hp]['special_defense']}, Total EVs: {optimized_evs[hp]['total_evs']}")
                best_evs = optimized_evs[hp]

        best_evs['hp'] = best_evs['total_evs'] - (0 if best_evs['defense'] is None else best_evs['defense']) - (0 if best_evs['special_defense'] is None else best_evs['special_defense'])

        print(f"HP: {best_evs['hp']}, Defense: {best_evs['defense']}, Special Defense: {best_evs['special_defense']}, Total EVs: {best_evs['total_evs']}")
        for a in attacks:
            if a['PhySpec'] == "Physical":
                #get the matching hp and def (x, x, 0) tuple from a['evs'] where x is the hp evs and def evs from best_evs
                for ev in a['evs']:
                    if ev[0] == best_evs['hp'] and ev[1] == best_evs['defense']:
                        print(f"{a['name']} - {ev[2]:.2f}%")
            else:
                for ev in a['evs']:
                    if ev[0] == best_evs['hp'] and ev[1] == best_evs['special_defense']:
                        print(f"{a['name']} - {ev[2]:.2f}%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize EVs for defense against attacks")
    parser.add_argument("attacks", help="Path to a JSON file containing attack definitions (list)")
    parser.add_argument("defense", help="Path to a JSON file containing the defender dict")
    args = parser.parse_args()

    def load_json(path):
        p = pathlib.Path(path)
        if not p.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return json.loads(p.read_text(encoding="utf-8"))

    attacks_data = load_json(args.attacks)
    defense_data = load_json(args.defense)

    main(attacks_data, defense_data)