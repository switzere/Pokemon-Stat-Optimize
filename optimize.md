```python
from scipy.optimize import minimize
```


```python
power = 80
atk = 150
base_health = 150
base_defense = 80
level = 50

defense_evs = 0
health_evs = 0
total_evs = 0
```


```python
damage = (( (2*level/5 + 2) * power * (atk / base_defense) ) / 50) + 2

damage
```


```python
health_percent = ((( (2*level/5 + 2) * power * (atk / base_defense) ) / 50) + 2 ) / base_health * 100

health_percent
```


```python
health_percent = ((( (2*level/5 + 2) * power * (atk / (base_defense + defense_evs)) ) / 50) + 2 ) / (base_health + health_evs) * 100

```


```python
import numpy as np

# Constants
power = 80
atk = 150
base_health = 150
base_defense = 80
level = 50
total_evs = 510

# Define the health_percent function
def health_percent(defense_evs, health_evs):
    if defense_evs + health_evs > total_evs:  # Constraint check
        return 0  # Invalid solution
    return ((( (2*level/5 + 2) * power * (atk / (base_defense + defense_evs)) ) / 50) + 2 ) / (base_health + health_evs) * 100

# Grid search over all possible EV combinations
defense_range = np.arange(0, 253)  # EVs from 0 to 252
health_range = np.arange(0, 253)
max_health_percent = 0
optimal_defense_evs = 0
optimal_health_evs = 0

for defense_evs in defense_range:
    for health_evs in health_range:
        if defense_evs + health_evs <= total_evs:  # Check total EV constraint
            current_health_percent = health_percent(defense_evs, health_evs)
            if current_health_percent > max_health_percent:
                max_health_percent = current_health_percent
                optimal_defense_evs = defense_evs
                optimal_health_evs = health_evs

print(f"Optimal Defense EVs: {optimal_defense_evs}")
print(f"Optimal Health EVs: {optimal_health_evs}")
print(f"Maximum Health Percent: {max_health_percent}")
```


```python
import matplotlib.pyplot as plt

# Define the health_percent function
def health_percent(defense_evs, health_evs):
    if defense_evs + health_evs > total_evs:  # Constraint check
        return 0  # Invalid solution
    return ((( (2*level/5 + 2) * power * (atk / (base_defense + defense_evs)) ) / 50) + 2 ) / (base_health + health_evs) * 100

# Fix defense_evs and vary health_evs
defense_evs = 32  # Example fixed value
health_evs_range = np.arange(0, 32)
health_percent_values = [health_percent(defense_evs, health_evs) for health_evs in health_evs_range]

# Plot the curve
plt.plot(health_evs_range, health_percent_values)
plt.xlabel('Health EVs')
plt.ylabel('Health Percent')
plt.title(f'Health Percent vs Health EVs (Defense EVs = {defense_evs})')
plt.show()
```


```python
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

# Constants
power = 80
atk = 150
base_health = 150
base_defense = 80
level = 50
total_evs = 66

# Define the health_percent function
def health_percent(defense_evs, health_evs):
    if defense_evs + health_evs > total_evs:  # Constraint check
        return 0  # Invalid solution
    return ((( (2*level/5 + 2) * power * (atk / (base_defense + defense_evs)) ) / 50) + 2 ) / (base_health + health_evs) * 100

# Create a grid of defense_evs and health_evs
defense_evs_range = np.linspace(0, 32, 32)
health_evs_range = np.linspace(0, 32, 32)
defense_evs_grid, health_evs_grid = np.meshgrid(defense_evs_range, health_evs_range)

# Calculate health_percent for each combination of defense_evs and health_evs
health_percent_grid = np.zeros_like(defense_evs_grid)
for i in range(defense_evs_grid.shape[0]):
    for j in range(defense_evs_grid.shape[1]):
        defense_evs = defense_evs_grid[i, j]
        health_evs = health_evs_grid[i, j]
        if defense_evs + health_evs <= total_evs:  # Check total EV constraint
            health_percent_grid[i, j] = health_percent(defense_evs, health_evs)

# Plot the 3D surface
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(defense_evs_grid, health_evs_grid, health_percent_grid, cmap='viridis')

# Add labels and title
ax.set_xlabel('Defense EVs')
ax.set_ylabel('Health EVs')
ax.set_zlabel('Health Percent')
ax.set_title('Health Percent vs Defense EVs and Health EVs')

# Add a color bar
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)

plt.show()
```


```python
# Find the minimum health_percent and its coordinates
min_health_percent = np.min(health_percent_grid)
min_index = np.unravel_index(np.argmin(health_percent_grid), health_percent_grid.shape)
optimal_defense_evs = defense_evs_grid[min_index]
optimal_health_evs = health_evs_grid[min_index]

print(f"Minimum Health Percent: {min_health_percent}")
print(f"Optimal Defense EVs: {optimal_defense_evs}")
print(f"Optimal Health EVs: {optimal_health_evs}")
```


```python
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np

# Constants
power = 80
atk = 150
base_health = 150
base_defense = 80
level = 50
total_evs = 50

#create a set of hp and def evs that add up to total_evs maxing at 32 for each. Example [32, 18], [31, 19], [30, 20], etc.]


# Generate all valid combinations of hp_evs and def_evs
ev_combinations = [
    (hp, total_evs - hp)
    for hp in range(0, min(32, total_evs) + 1)
    if total_evs - hp <= 32
]

# Print the combinations
for hp, defense in ev_combinations:
    print(f"HP EVs: {hp}, Defense EVs: {defense}")
```


```python
#Using the above combinations, calculate the health percent for each combination and find the optimal one. Then plot the results.

import matplotlib.pyplot as plt

# Constants
power = 80*2
atk = 182
base_health = 170
base_defense = 85
level = 50
total_evs = 1

# Define the health_percent function
def health_percent(defense_evs, health_evs):
    if defense_evs + health_evs > total_evs:  # Constraint check
        return 0  # Invalid solution
    return ((( (2*level/5 + 2) * power * (atk / (base_defense + defense_evs)) ) / 50) + 2 ) / (base_health + health_evs) * 100

# Generate all valid combinations of hp_evs and def_evs
ev_combinations = [
    (hp, total_evs - hp)
    for hp in range(0, min(32, total_evs) + 1)
    if total_evs - hp <= 32
]

# Calculate health_percent for each combination
results = []
for hp, defense in ev_combinations:
    hp_percent = health_percent(defense, hp)
    results.append((hp, defense, hp_percent))

# Find the optimal combination
optimal_combination = max(results, key=lambda x: x[2])  # Maximize health_percent
optimal_hp, optimal_defense, max_health_percent = optimal_combination

print(f"Optimal HP EVs: {optimal_hp}")
print(f"Optimal Defense EVs: {optimal_defense}")
print(f"Maximum Health Percent: {max_health_percent}")

# Plot the results
hp_evs = [r[0] for r in results]
def_evs = [r[1] for r in results]
health_percents = [r[2] for r in results]

plt.figure(figsize=(10, 6))
plt.scatter(hp_evs, def_evs, c=health_percents, cmap='viridis', s=100)
plt.colorbar(label='Health Percent')
plt.xlabel('HP EVs')
plt.ylabel('Defense EVs')
plt.title('Health Percent for Each EV Combination')
plt.show()
```


```python
import matplotlib.pyplot as plt
import math


def optimize_health_percent(base_health, base_defense, total_evs, def_mult=1, atk=150, power=100, level=50):
    """
    Optimizes health percent based on given constants and EV constraints.

    Args:
        power (int): Power of the move.
        atk (int): Attack stat.
        base_health (int): Base health stat.
        base_defense (int): Base defense stat.
        level (int): Level of the Pokémon.
        total_evs (int): Total EVs available to distribute.

    Returns:
        dict: A dictionary containing the optimal HP EVs, Defense EVs, maximum health percent, and a plot.
    """
    # Define the health_percent function
    def health_percent(defense_evs, health_evs):
        
        calculated_health = base_health + health_evs + 75
        calculated_defense = math.floor((base_defense + defense_evs + 20) * def_mult)

        if defense_evs + health_evs > total_evs:  # Constraint check
            return 0  # Invalid solution
        return ((( (2 * level / 5 + 2) * power * (atk / calculated_defense) ) / 50) + 2 ) / (calculated_health) * 100

    # Generate all valid combinations of hp_evs and def_evs
    ev_combinations = [
        (hp, total_evs - hp)
        for hp in range(0, min(32, total_evs) + 1)
        if total_evs - hp <= 32
    ]

    # Calculate health_percent for each combination
    results = []
    for hp, defense in ev_combinations:
        hp_percent = health_percent(defense, hp)
        results.append((hp, defense, hp_percent))

    # Find the optimal combination
    optimal_combination = min(results, key=lambda x: x[2])  # Minimize health_percent
    optimal_hp, optimal_defense, min_health_percent = optimal_combination

    # Print the optimal results
    print(f"Optimal HP EVs: {optimal_hp}")
    print(f"Optimal Defense EVs: {optimal_defense}")
    print(f"Minimum Health Percent: {min_health_percent}")

    # Plot the results
    hp_evs = [r[0] for r in results]
    def_evs = [r[1] for r in results]
    health_percents = [r[2] for r in results]

    plt.figure(figsize=(10, 6))
    plt.scatter(hp_evs, def_evs, c=health_percents, cmap='viridis', s=100)
    plt.colorbar(label='Health Percent')
    plt.xlabel('HP EVs')
    plt.ylabel('Defense EVs')
    plt.title('Health Percent for Each EV Combination')
    plt.show()

    # Return the results as a dictionary
    return {
        "optimal_hp_evs": optimal_hp,
        "optimal_defense_evs": optimal_defense,
        "max_health_percent": max_health_percent
    }

# HP = Base + StatPoints + 75
# OtherStat = lower( (Base + StatPoints + 20) * Allignment(1.2/0.8/1) )
```


```python
#simplified formula for health percent:
#((( 22 / calculated_defense ) / 50) + 2 ) / (calculated_health) * 100

# Example usage
results = optimize_health_percent(
    base_health=75,
    base_defense=60,
    total_evs=50,
    def_mult = 0.8
)

print(results)
```


```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math
from matplotlib.colors import ListedColormap
from ipywidgets import interact, IntSlider, FloatSlider
import pandas as pd

starting_base_health = 95
starting_base_defense = 65
atk = 182
power = 160
level = 50
bonus = 1.5


def interactive_heatmap_with_widgets():
    def plot_heatmap(base_health, base_defense, total_evs, def_mult):
        # Define the health_percent function
        def health_percent(defense_evs, health_evs):
            calculated_health = base_health + health_evs + 75
            calculated_defense = math.floor((base_defense + defense_evs + 20) * def_mult)
            if (defense_evs + health_evs) > total_evs:  # Constraint check
                return 0  # Invalid solution
            return ((( ( (2 * level / 5) + 2) * power * ( (atk * bonus) / calculated_defense) ) / 50) + 2 ) / (calculated_health) * 100
        
       

        # Create a grid for HP EVs and Defense EVs
        hp_evs_range = np.arange(0, 33)  # EVs from 0 to 32
        def_evs_range = np.arange(0, 33)
        heatmap_data = np.zeros((len(hp_evs_range), len(def_evs_range)))

        # Calculate health_percent for each combination
        for i, hp in enumerate(hp_evs_range):
            for j, defense in enumerate(def_evs_range):
                heatmap_data[i, j] = health_percent(defense, hp)

        # Flip the heatmap data along the y-axis to match the reversed y-axis labels
        # heatmap_df = pd.DataFrame(heatmap_data)
        # print(heatmap_df)

        # heatmap_data = np.flipud(heatmap_data)

        # heatmap_df = pd.DataFrame(heatmap_data)
        # print(heatmap_df)

        # Find the minimum health_percent that is not zero and its coordinates
        # Mask zero values in the heatmap data
        masked_heatmap = np.ma.masked_where(heatmap_data == 0, heatmap_data)

        flipped_heatmap_data = np.flipud(heatmap_data)

        # Find the index of the minimum non-zero value
        min_index = np.unravel_index(np.ma.argmin(masked_heatmap), flipped_heatmap_data.shape)

        # Extract the optimal EVs
        optimal_hp_evs = hp_evs_range[min_index[0]]
        optimal_defense_evs = def_evs_range[min_index[1]]
        optimal_hp_evs = hp_evs_range[min_index[0]]
        optimal_defense_evs = def_evs_range[min_index[1]]
        min_health_percent = heatmap_data[min_index]

        print(f"Optimal HP EVs: {optimal_hp_evs}")
        print(f"Optimal Defense EVs: {optimal_defense_evs}")
        print(f"Minimum Health Percent: {min_health_percent}")

        #flip optimal_hp_evs to match the flipped y-axis
        optimal_hp_evs = 32 - optimal_hp_evs

        # Create a custom colormap
        cmap = sns.color_palette("viridis", as_cmap=True)
        cmap_with_grey = ListedColormap(list(cmap(np.linspace(0, 1, 256))))

        # Mask zero values
        mask = flipped_heatmap_data == 0

        # Create the heat map
        plt.figure(figsize=(12, 8))
        sns.heatmap(
            flipped_heatmap_data,
            xticklabels=def_evs_range,  # Defense EVs on x-axis
            yticklabels=hp_evs_range[::-1],  # Reverse HP EVs for correct orientation
            cmap=cmap_with_grey,
            mask=mask,
            cbar_kws={'label': 'Health Percent'}
        )
        plt.xlabel("Defense EVs")
        plt.ylabel("HP EVs")
        plt.title("Health Percent Heat Map")

        # Overlay the total_evs constraint line
        # Overlay the total_evs constraint line
        hp_evs = np.arange(0, min(33, total_evs + 1))
        def_evs = total_evs - hp_evs

        #plt.plot(def_evs, hp_evs[::-1], color="red", label="Total EVs Constraint")  # Reverse hp_evs for flipped y-axis
        plt.scatter(
            optimal_defense_evs+.5, 
            optimal_hp_evs+.5,
            color="white", 
            edgecolor="black", 
            s=100, 
            label="Optimal Point"
        )
        plt.legend()

        # Show the plot
        plt.show()

    # Interactive sliders for parameters
    interact(
        plot_heatmap,
        base_health=IntSlider(value=starting_base_health, min=49, max=120, step=1, description="Base Health"),
        base_defense=IntSlider(value=starting_base_defense, min=40, max=150, step=1, description="Base Defense"),
        total_evs=IntSlider(value=50, min=0, max=64, step=1, description="Total EVs"),
        def_mult=FloatSlider(value=1.0, min=0.8, max=1.2, step=0.2, description="Defense Multiplier")
    )

# Call the function to enable interactivity
interactive_heatmap_with_widgets()
```


```python
def health_percent(defense_evs, health_evs, base_health, base_defense, total_evs, def_mult=1, atk=150, power=100, level=50, bonus=[1]):
    #print all values
    #print(f"Defense EVs: {defense_evs}, Health EVs: {health_evs}, Base Health: {base_health}, Base Defense: {base_defense}, Total EVs: {total_evs}, Defense Multiplier: {def_mult}, Attack: {atk}, Power: {power}, Level: {level}, Bonus: {bonus}")
    calculated_health = base_health + health_evs + 75
    calculated_defense = math.floor((base_defense + defense_evs + 20) * def_mult)
    if (defense_evs + health_evs) > total_evs:  # Constraint check
        return 0  # Invalid solution
    raw_damage = math.floor((( ( (2 * level / 5) + 2) * power * ( (atk) / calculated_defense) ) / 50) + 2 )

    for b in bonus:
        raw_damage = round(raw_damage * b)

    print(f" Raw Damage: {raw_damage} / Calculated Health: {calculated_health}, Calculated Defense: {calculated_defense}, Health Percent: {raw_damage / calculated_health * 100}%")
    return raw_damage / calculated_health * 100

    # print(((( ( (2 * level / 5) + 2) * power * ( (atk * bonus) / calculated_defense) ) / 50) + 2 ))
    # return ((( ( (2 * level / 5) + 2) * power * ( (atk * bonus) / calculated_defense) ) / 50) + 2 ) / (calculated_health) * 100
```


```python
#so I have a set of attacks that I want to optimize for, I think I want checkpoints for each attack

#Targets x Parental Bond x Weather x GlaiveRush x Critical x random x STAB x Type x Burn x other x ZMove x TeraShield

attacks = [
    {"name": "Dire Claw", "power": 80, "atk": 182, "bonus": [1.5,2], "PhySpec": "Physical", "evs": []},
 #   {"name": "Attack 2", "power": 100, "atk": 120, "bonus": 1, "PhySpec": "Physical", "evs": []},
    {"name": "Hyper Voice", "power": 100, "atk": 178, "bonus": [1.5, 2, 0.75, 1.2], "PhySpec": "Special", "evs": []}
]

defense = {
    "name": "Pokemon 1",
    "base_health": 88,
    "base_defense": 80,
    "base_special_defense": 95
}

starting_base_health = defense['base_health']
starting_base_defense = defense['base_defense']
starting_base_special_defense = defense['base_special_defense']
level = 50

evs_map = np.zeros((33, 33))

attackN = 0
for a in attacks:
    print(f"Optimizing for {a['name']}...")
    for i, hp in enumerate(np.arange(0, 33)):
        for j, defense in enumerate(np.arange(0, 33)):
            base_defense = starting_base_defense if a['PhySpec'] == "Physical" else starting_base_special_defense
            evs_map[i, j] = health_percent(defense_evs = defense, health_evs = hp, base_health = starting_base_health, base_defense = base_defense, total_evs = 64, def_mult = 1, atk = a['atk'], power = a['power'], level = level, bonus = a['bonus'])
            if evs_map[i, j] != 0 and evs_map[i, j] < 100:
                attacks[attackN]['evs'].append((hp, defense, evs_map[i, j]))
            else:
                attacks[attackN]['evs'].append((hp, defense, 0))
    attackN += 1
```


```python
attacks[0]['evs']
#attacks[1]['evs'][-70:]
```


```python
#attach the lowest defense percent and lowest special defense percent to each unique hp evs value for each attack

#create dict with a evs key for 1-32
optimized_evs = {hp: {"defense": None, "special_defense": None} for hp in range(33)}

for a in attacks:
    #for each hp ev value get the lowest defense evs and lowest special defense evs and attach to optimized_evs dict
    for hp in range(33):
        defense_evs = [ev[1] for ev in a['evs'] if ev[0] == hp and ev[2] != 0]
        health_percents = [ev[2] for ev in a['evs'] if ev[0] == hp and ev[2] != 0]

        if len(defense_evs) > 0:
            min_defense_evs = min(defense_evs)
            if a['PhySpec'] == "Physical":
                optimized_evs[hp]['defense'] = min_defense_evs
                optimized_evs[hp]['defense_percent'] = health_percents[defense_evs.index(min_defense_evs)]
            else:
                optimized_evs[hp]['special_defense'] = min_defense_evs
                optimized_evs[hp]['special_defense_percent'] = health_percents[defense_evs.index(min_defense_evs)]
        else:
            if a['PhySpec'] == "Physical":
                optimized_evs[hp]['defense'] = None
                optimized_evs[hp]['defense_percent'] = None
            else:
                optimized_evs[hp]['special_defense'] = None
                optimized_evs[hp]['special_defense_percent'] = None

# for oe in optimized_evs:
#     #if sum of hp evs, def evs, spD evs is less than or equal to 66 keep
#     if optimized_evs[oe]['defense'] is not None and optimized_evs[oe]['special_defense'] is not None:
#         if oe + optimized_evs[oe]['defense'] + optimized_evs[oe]['special_defense'] <= 66:
#             optimized_evs[oe]['total'] = oe + optimized_evs[oe]['defense'] + optimized_evs[oe]['special_defense']

```


```python
#for each set of optimized evs find the one with the least evs total (hp, def, spD) and attach it to optimized evs
for hp in range(33):
    if optimized_evs[hp]['defense'] is None or optimized_evs[hp]['special_defense'] is None:
        #remove key
        del optimized_evs[hp]
        continue
    defense_evs = optimized_evs[hp]['defense'] if optimized_evs[hp]['defense'] is not None else 0
    special_defense_evs = optimized_evs[hp]['special_defense'] if optimized_evs[hp]['special_defense'] is not None else 0
    total_evs = hp + defense_evs + special_defense_evs
    optimized_evs[hp]['total_evs'] = total_evs
```


```python
optimized_evs
```


```python
#print min total evs and corresponding hp, defense, and special defense evs
min_total_evs = min([optimized_evs[hp]['total_evs'] for hp in optimized_evs])
for hp in optimized_evs:
    if optimized_evs[hp]['total_evs'] == min_total_evs:
        print(f"Optimal HP EVs: {hp}, Optimal Defense EVs: {optimized_evs[hp]['defense']}, Optimal Special Defense EVs: {optimized_evs[hp]['special_defense']}, Total EVs: {optimized_evs[hp]['total_evs']}")
```


```python
#graph optimized_evs in a stacked bar chart with total evs on the y axis, with different colors for hp, defense and special defense evs
hp_evs = list(optimized_evs.keys())
defense_evs = [optimized_evs[hp]['defense'] for hp in optimized_evs]
special_defense_evs = [optimized_evs[hp]['special_defense'] for hp in optimized_evs]
total_evs = [optimized_evs[hp]['total_evs'] for hp in optimized_evs]

plt.figure(figsize=(12, 8))
plt.bar(hp_evs, hp_evs, color='green', label='HP EVs')
plt.bar(hp_evs, defense_evs, bottom=hp_evs, color='blue', label='Defense EVs')
plt.bar(hp_evs, special_defense_evs, bottom=np.add(hp_evs, defense_evs), color='orange', label='Special Defense EVs')
plt.xlabel('HP EVs')
plt.xticks(hp_evs)
plt.ylabel('EVs')
plt.title('Optimized EV Distribution')
plt.legend()
plt.show()


```


```python
import tkinter as tk
from tkinter import ttk, messagebox
import json

def parse_bonuses(text):
    # "1.5,2,0.75" -> [1.5, 2.0, 0.75]
    return [float(x.strip()) for x in text.split(",") if x.strip()]

def run_optimizer(defense_info, attacks):
    # TODO: call your existing health_percent + optimized_evs pipeline here.
    # Return a dict/list with results.

    base_health = defense_info['base_health']
    base_defense = defense_info['base_defense']
    base_special_defense = defense_info['base_special_defense']
    level = 50

    attackN = 0
    for a in attacks:
        print(f"Optimizing for {a['name']}...")
        for i, hp in enumerate(np.arange(0, 33)):
            for j, defense in enumerate(np.arange(0, 33)):
                effective_defense = base_defense if a['PhySpec'] == "Physical" else base_special_defense
                evs_map[i, j] = health_percent(defense_evs = defense, health_evs = hp, base_health = base_health, base_defense = effective_defense, total_evs = 64, def_mult = 1, atk = a['atk'], power = a['power'], level = level, bonus = a['bonus'])
                if evs_map[i, j] != 0 and evs_map[i, j] < 100:
                    attacks[attackN]['evs'].append((hp, defense, evs_map[i, j]))
                else:
                    attacks[attackN]['evs'].append((hp, defense, 0))
        attackN += 1

    return {"attacks": attacks}

def on_add_attack():
    try:
        attack = {
            "name": name_var.get().strip(),
            "power": int(power_var.get()),
            "atk": int(atk_var.get()),
            "PhySpec": physpec_var.get(),
            "bonus": parse_bonuses(bonus_var.get()),
            "evs": []
        }
        if not attack["name"]:
            raise ValueError("Attack name is required.")
        attacks.append(attack)
        attacks_list.insert(tk.END, f'{attack["name"]} | {attack["PhySpec"]} | Pwr {attack["power"]} | Atk {attack["atk"]} | bonus={attack["bonus"]}')
        name_var.set("")
        power_var.set("")
        atk_var.set("")
        bonus_var.set("1")
    except Exception as e:
        messagebox.showerror("Invalid Attack Input", str(e))

def on_run():
    try:
        defense_info = {
            "base_health": int(base_hp_var.get()),
            "base_defense": int(base_def_var.get()),
            "base_special_defense": int(base_spdef_var.get())
        }
        if not attacks:
            raise ValueError("Add at least one attack first.")

        result = run_optimizer(defense_info, attacks)
        result_box.delete("1.0", tk.END)
        result_box.insert(
            tk.END,
            json.dumps(
                result,
                indent=2,
                default=lambda o: int(o) if isinstance(o, np.integer)
                else float(o) if isinstance(o, np.floating)
                else o.tolist() if isinstance(o, np.ndarray)
                else str(o)
            )
        )
    except Exception as e:
        messagebox.showerror("Run Failed", str(e))

# App state
attacks = []

# UI
root = tk.Tk()
root.title("Pokemon EV Optimizer")
root.geometry("760x560")

main = ttk.Frame(root, padding=12)
main.pack(fill="both", expand=True)

# Defense inputs
ttk.Label(main, text="Defense Info", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 6))
base_hp_var = tk.StringVar(value="88")
base_def_var = tk.StringVar(value="80")
base_spdef_var = tk.StringVar(value="95")

ttk.Label(main, text="Base HP").grid(row=1, column=0, sticky="w")
ttk.Entry(main, textvariable=base_hp_var, width=10).grid(row=1, column=1, sticky="w")

ttk.Label(main, text="Base Def").grid(row=1, column=2, sticky="w")
ttk.Entry(main, textvariable=base_def_var, width=10).grid(row=1, column=3, sticky="w")

ttk.Label(main, text="Base SpDef").grid(row=1, column=4, sticky="w")
ttk.Entry(main, textvariable=base_spdef_var, width=10).grid(row=1, column=5, sticky="w")

# Attack inputs
ttk.Separator(main, orient="horizontal").grid(row=2, column=0, columnspan=6, sticky="ew", pady=10)
ttk.Label(main, text="Attack Input", font=("Segoe UI", 11, "bold")).grid(row=3, column=0, sticky="w", pady=(0, 6))

name_var = tk.StringVar()
power_var = tk.StringVar()
atk_var = tk.StringVar()
bonus_var = tk.StringVar(value="1.5,2")
physpec_var = tk.StringVar(value="Physical")

ttk.Label(main, text="Name").grid(row=4, column=0, sticky="w")
ttk.Entry(main, textvariable=name_var, width=16).grid(row=4, column=1, sticky="w")

ttk.Label(main, text="Power").grid(row=4, column=2, sticky="w")
ttk.Entry(main, textvariable=power_var, width=10).grid(row=4, column=3, sticky="w")

ttk.Label(main, text="Atk").grid(row=4, column=4, sticky="w")
ttk.Entry(main, textvariable=atk_var, width=10).grid(row=4, column=5, sticky="w")

ttk.Label(main, text="Type").grid(row=5, column=0, sticky="w")
ttk.Combobox(main, textvariable=physpec_var, values=["Physical", "Special"], state="readonly", width=12).grid(row=5, column=1, sticky="w")

ttk.Label(main, text="Bonuses (comma-separated)").grid(row=5, column=2, sticky="w")
ttk.Entry(main, textvariable=bonus_var, width=24).grid(row=5, column=3, columnspan=3, sticky="w")

ttk.Button(main, text="Add Attack", command=on_add_attack).grid(row=6, column=0, pady=8, sticky="w")

attacks_list = tk.Listbox(main, height=8, width=95)
attacks_list.grid(row=7, column=0, columnspan=6, sticky="ew")

ttk.Button(main, text="Run Optimization", command=on_run).grid(row=8, column=0, pady=10, sticky="w")

result_box = tk.Text(main, height=10, width=95)
result_box.grid(row=9, column=0, columnspan=6, sticky="nsew")

main.grid_rowconfigure(9, weight=1)
main.grid_columnconfigure(5, weight=1)

root.mainloop()
```
