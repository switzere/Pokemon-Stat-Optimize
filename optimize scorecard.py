import re
from pathlib import Path
import json
import pandas as pd
import subprocess
import numpy as np
import seaborn as sns
from io import BytesIO

from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import Normalize
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.offsetbox import AnnotationBbox, OffsetImage
from copy import deepcopy
import textwrap
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec


cmap_red = LinearSegmentedColormap.from_list(
    "cmap_red",
    [
        (0.0, "#ffffff"),  # 0%: white
        (0.5, "#ffb7b7"),  # 50%: light red
        (0.99, "#ff5959"),  # 99%: dark red
        (1.0, "#ff0000"),  # 100%: red
    ],
)

cmap_blue = LinearSegmentedColormap.from_list(
    "cmap_blue",
    [
        (0.0, "#ffffff"),  # 0%: white
        (0.5, "#b7dcff"),  # 50%: light blue
        (0.9999, "#59a7ff"),  # 99%: dark blue
        (1.0, "#0074e9"),  # 100%: blue
    ],
)

project_dir = Path(r"C:\Users\evan\Desktop\Personal Projects\Pokemon Stat Optimize")
sprite_dir = project_dir / "images" / "sprites"
report_figures = []


def parse_showdown_set(block):
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    pokemon_text, separator, item = lines[0].partition(" @ ")
    pokemon_text = re.sub(r"\s+\([MF]\)$", "", pokemon_text.strip())
    species_match = re.search(r"\(([^()]+)\)$", pokemon_text)
    pokemon = {"name": species_match.group(1).strip() if species_match else pokemon_text,
               "level": 50, "evs": {}, "moves": []}
    if separator:
        pokemon["item"] = item.strip()

    for line in lines[1:]:
        if line.startswith("- "):
            pokemon["moves"].append(line[2:].strip())
        elif line.lower().startswith("ability:"):
            pokemon["ability"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("level:"):
            pokemon["level"] = int(line.split(":", 1)[1].strip())
        elif line.lower().startswith("evs:"):
            for entry in line.split(":", 1)[1].split("/"):
                amount, stat = entry.strip().split(maxsplit=1)
                pokemon["evs"][stat.lower()] = int(amount)
        elif line.lower().endswith(" nature"):
            pokemon["nature"] = line[:-len(" nature")].strip()
    return pokemon

def read_showdown_team(path):
    text = path.read_text(encoding="utf-8").strip()
    return [parse_showdown_set(block) for block in re.split(r"\r?\n\s*\r?\n", text) if block.strip()]

attackers = read_showdown_team(project_dir / "attackers.txt")
defenders = read_showdown_team(project_dir / "defenders.txt")

def sprite_path_for(name):
    slug = re.sub(r"[^a-z0-9]+", "-", name.casefold()).strip("-")
    candidates = [sprite_dir / f"{slug}.png"]
    if slug.endswith("-f"):
        candidates.append(sprite_dir / f"{slug[:-2]}-female.png")
    for path in candidates:
        if path.is_file():
            return path
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"No sprite found for {name!r}; checked: {searched}")

def figure_to_image(source_figure):
    buffer = BytesIO()
    source_figure.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    return mpimg.imread(buffer)

matchup_requests = [
    {"attacker": {key: value for key, value in attacker.items() if key != "moves"},
     "defender": {key: value for key, value in defender.items() if key != "moves"},
     "move": move,
     "field": {"gameType": "Doubles"}}
    for attacker in attackers
    for defender in defenders
    for move in attacker["moves"]
]

for request in matchup_requests:
    participants = {
        request["attacker"]["name"],
        request["defender"]["name"],
    }

    field = request["field"]

    if "Indeedee-F" in participants:
        field["terrain"] = "Psychic"

    if "Mr. Rime" in participants:
        field["terrain"] = "Psychic"

    if "Froslass-Mega" in participants:
        field["weather"] = "Snow"
    elif "Pelipper" in participants:
        field["weather"] = "Rain"
    elif "Charizard-Mega-Y" in participants:
        field["weather"] = "Sun"

    if field:
        request["field"] = field


try:
    matchup_result = subprocess.run(
        ["node", "damage.js"],
        input=json.dumps({"generation": 0, "matchups": matchup_requests}),
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )
except subprocess.CalledProcessError as error:
    print(error.stderr)
    raise

a_pokemon_raw = []
d_pokemon_raw = []

for a in attackers:
    name = a['name']

    result = subprocess.run(
        ["node", "damage.js"],
        input=json.dumps({
            "action": "lookup",
            "generation": 0,
            "name": name,
            "level": 50,
        }),
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )

    a_result = json.loads(result.stdout)
    a_pokemon_raw.append(a_result)

for d in defenders:
    name = d['name']

    result = subprocess.run(
        ["node", "damage.js"],
        input=json.dumps({
            "action": "lookup",
            "generation": 0,
            "name": name,
            "level": 50,
        }),
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )

    d_result = json.loads(result.stdout)
    d_pokemon_raw.append(d_result)

speed_tiers = [
    {
        "side": side,
        "name": pokemon["name"],
        "speed": pokemon["species"]["baseStats"]["spe"],
    }
    for side, pokemon_list in [
        ("Attacker", a_pokemon_raw),
        ("Defender", d_pokemon_raw),
    ]
    for pokemon in pokemon_list
]

speed_tiers.sort(key=lambda pokemon: pokemon["speed"], reverse=True)

print("Matchup Chart")

move_results = json.loads(matchup_result.stdout)
matchup_df = pd.DataFrame(move_results)
damaging_moves = matchup_df[matchup_df["category"] != "Status"]

best_attacks_df = damaging_moves.loc[
    damaging_moves.groupby(["attacker", "defender"])["maxDamage"].idxmax()
].reset_index(drop=True)

attacker_stats = best_attacks_df["attackerStats"].apply(pd.Series)
attacker_stats = attacker_stats.add_prefix("attacker_")

defender_stats = best_attacks_df["defenderStats"].apply(pd.Series)
defender_stats = defender_stats.add_prefix("defender_")

best_attacks_df = pd.concat(
    [best_attacks_df.drop(columns="attackerStats"), attacker_stats],
    axis=1,
)

best_attacks_df = pd.concat(
    [best_attacks_df.drop(columns="defenderStats"), defender_stats],
    axis=1,
)

best_attacks_df['max_damage_percent'] = best_attacks_df['maxDamage'] / best_attacks_df['defender_hp'] * 100
best_attacks_df['min_damage_percent'] = best_attacks_df['minDamage'] / best_attacks_df['defender_hp'] * 100


forward_best_attacks_df = best_attacks_df.copy()

reverse_matchup_requests = [
    {
        "attacker": {key: value for key, value in opponent.items() if key != "moves"},
        "defender": {key: value for key, value in your_pokemon.items() if key != "moves"},
        "move": move,
        "field": {"gameType": "Doubles"},
    }
    for your_pokemon in attackers
    for opponent in defenders
    for move in opponent["moves"]
]

for request in reverse_matchup_requests:
    participants = {request["attacker"]["name"], request["defender"]["name"]}
    field = request["field"]
    if "Indeedee-F" in participants or "Mr. Rime" in participants:
        field["terrain"] = "Psychic"
    if "Froslass-Mega" in participants:
        field["weather"] = "Snow"
    elif "Pelipper" in participants:
        field["weather"] = "Rain"

try:
    reverse_result = subprocess.run(
        ["node", "damage.js"],
        input=json.dumps({"generation": 0, "matchups": reverse_matchup_requests}),
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )
except subprocess.CalledProcessError as error:
    print(error.stderr)
    raise

reverse_matchup_df = pd.DataFrame(json.loads(reverse_result.stdout))
reverse_damaging_moves = reverse_matchup_df[
    reverse_matchup_df["category"] != "Status"
]
reverse_best_attacks_df = reverse_damaging_moves.loc[
    reverse_damaging_moves.groupby(["attacker", "defender"])["maxDamage"].idxmax()
].reset_index(drop=True)

reverse_defender_stats = reverse_best_attacks_df["defenderStats"].apply(pd.Series)
reverse_best_attacks_df = pd.concat(
    [reverse_best_attacks_df.drop(columns="defenderStats"),
     reverse_defender_stats.add_prefix("defender_")],
    axis=1,
)
reverse_best_attacks_df["min_damage_percent"] = (
    reverse_best_attacks_df["minDamage"] / reverse_best_attacks_df["defender_hp"] * 100
)
def add_sprite(ax, name, x, y, zoom=0.35):
    image = plt.imread(sprite_path_for(name))
    icon = OffsetImage(image, zoom=zoom)
    box = AnnotationBbox(
        icon,
        (x, y),
        frameon=False,
        annotation_clip=False,
    )
    ax.add_artist(box)

outgoing_damage = forward_best_attacks_df.pivot(
    index="attacker", columns="defender", values="min_damage_percent"
)
outgoing_moves = forward_best_attacks_df.pivot(
    index="attacker", columns="defender", values="move"
)
incoming_damage = reverse_best_attacks_df.pivot(
    index="defender", columns="attacker", values="min_damage_percent"
)
incoming_moves = reverse_best_attacks_df.pivot(
    index="defender", columns="attacker", values="move"
)

your_names = outgoing_damage.index
opponent_names = outgoing_damage.columns
incoming_damage = incoming_damage.reindex(index=your_names, columns=opponent_names)
incoming_moves = incoming_moves.reindex(index=your_names, columns=opponent_names)

norm = Normalize(vmin=0, vmax=100)
fig, ax = plt.subplots(
    figsize=(max(10, 2.4 * len(opponent_names)), max(6, 1.5 * len(your_names)))
)
triangles = []
facecolors = []

for row, your_name in enumerate(your_names):
    for col, opponent_name in enumerate(opponent_names):
        outgoing = outgoing_damage.loc[your_name, opponent_name]
        incoming = incoming_damage.loc[your_name, opponent_name]

        if pd.notna(outgoing):
            triangles.append([(col, row + 1), (col + 1, row + 1), (col, row)])
            facecolors.append(cmap_red(norm(outgoing)))
            ax.text(
                col + 1 / 3,
                row + 2 / 3,
                f"{outgoing_moves.loc[your_name, opponent_name]}\n{outgoing:.1f}%",
                ha="center",
                va="top",
                fontsize=9,
            )

        if pd.notna(incoming):
            triangles.append([(col + 1, row), (col + 1, row + 1), (col, row)])
            facecolors.append(cmap_blue(norm(incoming)))
            ax.text(
                col + 2 / 3,
                row + 1 / 3,
                f"{incoming_moves.loc[your_name, opponent_name]}\n{incoming:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
            )

ax.add_collection(
    PolyCollection(triangles, facecolors=facecolors, edgecolors="white", linewidths=0.8)
)
ax.set_xlim(0, len(opponent_names))
ax.set_ylim(len(your_names), 0)
ax.set_aspect("equal")

ax.set_xlim(-0.8, len(opponent_names))
ax.set_ylim(len(your_names), -0.8)

ax.set_xticks([i + 0.5 for i in range(len(opponent_names))], labels=[])
ax.set_yticks([i + 0.5 for i in range(len(your_names))], labels=[])
ax.tick_params(length=0)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.spines["left"].set_visible(False)

for col, name in enumerate(opponent_names):
    add_sprite(ax, name, col + 0.5, -0.4)

for row, name in enumerate(your_names):
    add_sprite(ax, name, -0.4, row + 0.5)

# ax.set_xticks([i + 0.5 for i in range(len(opponent_names))], labels=opponent_names)
# ax.set_yticks([i + 0.5 for i in range(len(your_names))], labels=your_names)
ax.xaxis.tick_top()
ax.xaxis.set_label_position("top")
ax.set_title("Your Damage(min) vs Opponents' Damage(max) ", pad=24, fontdict={"fontsize": 22})
# fig.colorbar(
#     ScalarMappable(norm=norm, cmap=cmap_red),
#     ax=ax,
#     fraction=0.025,
#     pad=0.04,
#     label="You -> Opponent damage (% of opponent HP)",
# )
# fig.colorbar(
#     ScalarMappable(norm=norm, cmap=cmap_blue),
#     ax=ax,
#     fraction=0.025,
#     pad=0.10,
#     label="Opponent -> You damage (% of your HP)",
# )
plt.tight_layout()
report_figures.append(fig)

print("Speed Tiers")

speed_rows = []

for pokemon in speed_tiers:
    base_speed = pokemon["speed"]
    default_speed = base_speed + 20
    evs32 = default_speed + 32
    evs32p = np.floor(evs32 * 1.1)
    p1 = np.floor(evs32p*1.5)
    p2 = evs32p*2

    speed_rows.append({
        "Pokémon": pokemon["name"],
        "Side": pokemon["side"],
        "Base": base_speed,
        "32": int(evs32),
        "32+": int(evs32p),
        "+1": int(p1),
        "+2": int(p2),
    })

speed_df = (
    pd.DataFrame(speed_rows)
    .sort_values("Base", ascending=False)
    .reset_index(drop=True)
)

display_df = speed_df.drop(columns="Side").copy()
display_df.insert(0, "", "")

sprite_width = 0.10
name_width = 0.28
other_width = (1 - sprite_width - name_width) / (len(display_df.columns) - 2)
col_widths = [sprite_width, name_width] + [other_width] * (len(display_df.columns) - 2)

fig, ax = plt.subplots(figsize=(8, max(3.5, len(speed_df) * 0.38 + 1.5)))
ax.axis("off")

table = ax.table(
    cellText=display_df.values,
    colLabels=display_df.columns,
    cellLoc="center",
    colLoc="center",
    colWidths=col_widths,
    loc="center",
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.35)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#26374a")
        cell.set_text_props(color="white", weight="bold")
    else:
        side = speed_df.iloc[row - 1]["Side"]
        cell.set_facecolor("#ffb7b7" if side == "Attacker" else "#b7dcff")
        cell.set_edgecolor("white")

fig.tight_layout()
fig.canvas.draw()

# Overlay each Pokémon sprite in the first (Sprite) column
for table_row, name in enumerate(speed_df["Pokémon"], start=1):
    cell = table[(table_row, 0)]
    image = plt.imread(sprite_path_for(name))
    icon = OffsetImage(image, zoom=0.18)

    x, y = cell.get_xy()
    sprite = AnnotationBbox(
        icon,
        (x + cell.get_width() / 2, y + cell.get_height() / 2),
        xycoords=ax.transAxes,
        frameon=False,
        box_alignment=(0.5, 0.5),
    )
    ax.add_artist(sprite)

report_figures.append(fig)

print("Individual Matchups")

new_requests = []

super_bulk_flag = False

for i in range(0, 33):
    #edit matchup requests to make a new request with attack evs being 0-32
    for request in matchup_requests:
        new_request = deepcopy(request)
        new_request["attacker"]["evs"]["atk"] = i
        new_request["attacker"]["evs"]["spa"] = i
        new_request["attacker"]["nature"] = "Adamant"
        if super_bulk_flag:
            new_request["defender"]["evs"]["hp"] = 32
            new_request["defender"]["evs"]["def"] = 32
            new_request["defender"]["evs"]["spd"] = 32
        new_requests.append(new_request)
        
        new_request = deepcopy(request)
        new_request["attacker"]["evs"]["atk"] = i
        new_request["attacker"]["evs"]["spa"] = i
        new_request["attacker"]["nature"] = "Modest"
        if super_bulk_flag:
            new_request["defender"]["evs"]["hp"] = 32
            new_request["defender"]["evs"]["def"] = 32
            new_request["defender"]["evs"]["spd"] = 32
        new_requests.append(new_request)

        new_request = deepcopy(request)
        new_request["attacker"]["evs"]["atk"] = i
        new_request["attacker"]["evs"]["spa"] = i
        new_request["attacker"]["nature"] = "Serious"
        if super_bulk_flag:
            new_request["defender"]["evs"]["hp"] = 32
            new_request["defender"]["evs"]["def"] = 32
            new_request["defender"]["evs"]["spd"] = 32
        new_requests.append(new_request)

try:
    result = subprocess.run(
        ["node", "damage.js"],
        input=json.dumps({"generation": 0, "matchups": new_requests}),
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )
except subprocess.CalledProcessError as error:
    print(error.stderr)
    raise

new_results = json.loads(result.stdout)

for result, request in zip(new_results, new_requests):
    attacker = request["attacker"]
    result["attack_evs"] = attacker["evs"].get("atk", 0)
    result["special_attack_evs"] = attacker["evs"].get("spa", 0)
    result["nature"] = attacker.get("nature", "Serious")

new_results = [result for result in new_results if result["damage"] != 0]
new_results_df = pd.DataFrame(new_results)

attacker_stats = new_results_df["attackerStats"].apply(pd.Series)
attacker_stats = attacker_stats.add_prefix("attacker_")

defender_stats = new_results_df["defenderStats"].apply(pd.Series)
defender_stats = defender_stats.add_prefix("defender_")

new_results_df = pd.concat(
    [new_results_df.drop(columns="attackerStats"), attacker_stats],
    axis=1,
)

new_results_df = pd.concat(
    [new_results_df.drop(columns="defenderStats"), defender_stats],
    axis=1,
)

new_results_df['min_damage_percent'] = new_results_df['minDamage'] / new_results_df['defender_hp'] * 100
new_results_df

#for each attack per pokemon per defender, find the move that deals the minimum damage percent that is closest to 100 without going under
def choose_best_index(group):
    at_least_100 = group[group["min_damage_percent"] >= 100]
    candidates = at_least_100 if not at_least_100.empty else group
    return (candidates["min_damage_percent"] - 100).abs().idxmin()

best_moves = new_results_df.loc[
    new_results_df.groupby(["attacker", "defender"], group_keys=False)
    .apply(choose_best_index)
]

#for each attacker in best moves, create a simple table/heatmap showing the minimum damage percent against each defender

sprites_flag = False

attacker_figs = {}

for attacker, group in best_moves.groupby("attacker"):
    group["wrapped_description"] = group["description"].apply(
        lambda text: textwrap.fill(str(text), width=75)
    )

    pivot_table = group.pivot(
        index="defender",
        columns="attacker",
        values="min_damage_percent"
    )
    description_table = group.pivot(
        index="defender",
        columns="attacker",
        values="wrapped_description",
    ).reindex(index=pivot_table.index, columns=pivot_table.columns)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        pivot_table,
        annot=description_table,
        fmt="",
        cmap=cmap_red,
        # cbar_kws={'label': 'Min Damage %'},
        vmin=0,
        vmax=100,
        annot_kws={"color": "black"},
        )

    #removing extra labels and colour bar
    ax.set_yticklabels([])
    ax.set_ylabel("")
    ax.tick_params(axis="y", length=0)
    ax.set_xticklabels([])
    ax.set_xlabel("")
    ax.tick_params(axis="x", length=0)
    ax.collections[0].colorbar.remove()


    if sprites_flag:
        # Put each defender's sprite next to its heatmap row
        for row, defender in enumerate(pivot_table.index):
            filename = defender.lower().replace(" ", "-") + ".png"
            sprite_path = sprite_dir / filename

            if sprite_path.exists():
                image = mpimg.imread(sprite_path)
                sprite = OffsetImage(image, zoom=0.35)
                box = AnnotationBbox(
                    sprite,
                    (-0.05, row + 0.5),
                    xycoords=ax.transData,
                    frameon=False,
                    box_alignment=(0.5, 0.5),
                )
                ax.add_artist(box)

    #image_path = image_dir / f"{attacker.lower().replace(' ', '-')}.png"
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    #report_figures.append(fig)
    #fig.savefig(image_path, dpi=150, bbox_inches="tight", pad_inches=0)
    attacker_figs[attacker] = fig
    plt.close(fig)

new_requests = []

super_strength_flag = False
only_neutral_nature = True

for i in range(0, 33):
    for j in range(0, 33):

        for request in reverse_matchup_requests:
            if not only_neutral_nature:
                new_request = deepcopy(request)
                new_request["defender"]["evs"]["hp"] = i
                new_request["defender"]["evs"]["def"] = j
                new_request["defender"]["evs"]["spd"] = j
                new_request["defender"]["nature"] = "Lax"
                if super_strength_flag:
                    new_request["defender"]["evs"]["hp"] = 32
                    new_request["defender"]["evs"]["def"] = 32
                    new_request["defender"]["evs"]["spd"] = 32
                new_requests.append(new_request)
                
                new_request = deepcopy(request)
                new_request["defender"]["evs"]["hp"] = i
                new_request["defender"]["evs"]["def"] = j
                new_request["defender"]["evs"]["spd"] = j
                new_request["defender"]["nature"] = "Gentle"
                if super_strength_flag:
                    new_request["defender"]["evs"]["hp"] = 32
                    new_request["defender"]["evs"]["def"] = 32
                    new_request["defender"]["evs"]["spd"] = 32
                new_requests.append(new_request)

            new_request = deepcopy(request)
            new_request["defender"]["evs"]["hp"] = i
            new_request["defender"]["evs"]["def"] = j
            new_request["defender"]["evs"]["spd"] = j
            new_request["defender"]["nature"] = "Serious"
            if super_strength_flag:
                new_request["defender"]["evs"]["hp"] = 32
                new_request["defender"]["evs"]["def"] = 32
                new_request["defender"]["evs"]["spd"] = 32
            new_requests.append(new_request)

try:
    result = subprocess.run(
        ["node", "damage.js"],
        input=json.dumps({"generation": 0, "matchups": new_requests}),
        cwd=project_dir,
        check=True,
        capture_output=True,
        text=True,
    )
except subprocess.CalledProcessError as error:
    print(error.stderr)
    raise

new_results = json.loads(result.stdout)

for result, request in zip(new_results, new_requests):
    defender = request["defender"]
    result["hp_evs"] = defender["evs"].get("hp", 0)
    result["defense_evs"] = defender["evs"].get("def", 0)
    result["special_defense_evs"] = defender["evs"].get("spd", 0)
    result["total_evs"] = result["hp_evs"] + result["defense_evs"]
    result["nature"] = defender.get("nature", "Serious")


new_results = [result for result in new_results if result["damage"] != 0]
new_results_df = pd.DataFrame(new_results)

attacker_stats = new_results_df["attackerStats"].apply(pd.Series)
attacker_stats = attacker_stats.add_prefix("attacker_")

defender_stats = new_results_df["defenderStats"].apply(pd.Series)
defender_stats = defender_stats.add_prefix("defender_")

new_results_df = pd.concat(
    [new_results_df.drop(columns="attackerStats"), attacker_stats],
    axis=1,
)

new_results_df = pd.concat(
    [new_results_df.drop(columns="defenderStats"), defender_stats],
    axis=1,
)

new_results_df['max_damage_percent'] = new_results_df['maxDamage'] / new_results_df['defender_hp'] * 100

def choose_best_index(group):
    # Identify the move with the highest damage across the tested spreads
    strongest_move = group.loc[
        group["max_damage_percent"].idxmax(), "move"
    ]

    # Check which EV spreads survive that move
    strongest_move_rows = group[group["move"] == strongest_move]
    survivors = strongest_move_rows[
        strongest_move_rows["max_damage_percent"] < 100
    ]

    if not survivors.empty:
        neutral_survivors = survivors[survivors["nature"] == "Serious"]
        # Among spreads that survive, use the fewest total EVs
        if not neutral_survivors.empty:
            return neutral_survivors["total_evs"].idxmin()
        return survivors["total_evs"].idxmin()

    # If none survive, select the spread that reduces damage the most
    return strongest_move_rows["max_damage_percent"].idxmin()




selected_indices = (
    new_results_df.groupby(["attacker", "defender"])
    .apply(choose_best_index)
)

best_moves = new_results_df.loc[selected_indices.astype(int)]

#for each attacker in best moves, create a simple table/heatmap showing the maximum damage percent against each defender

defender_figs = {}

for defender, group in best_moves.groupby("defender"):
    group["wrapped_description"] = group["description"].apply(
        lambda text: textwrap.fill(str(text), width=75)
    )

    pivot_table = group.pivot(
        index="attacker",
        columns="defender",
        values="max_damage_percent"
    )
    description_table = group.pivot(
        index="attacker",
        columns="defender",
        values="wrapped_description",
    ).reindex(index=pivot_table.index, columns=pivot_table.columns)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(
        pivot_table,
        annot=description_table,
        fmt="",
        cmap=cmap_blue,
        # cbar_kws={'label': 'Min Damage %'},
        vmin=0,
        vmax=100,
        annot_kws={"color": "black"},
        ax=ax,
        )

    #removing extra labels and colour bar
    ax.set_yticklabels([])
    ax.set_ylabel("")
    ax.tick_params(axis="y", length=0)
    ax.set_xticklabels([])
    ax.set_xlabel("")
    ax.tick_params(axis="x", length=0)
    ax.collections[0].colorbar.remove()
    ax.set_xlim(-0., pivot_table.shape[1])

    for row, defender_name in enumerate(pivot_table.index):
        filename = defender_name.lower().replace(" ", "-").replace(".", "") + ".png"
        filename = filename.replace("-f", "-female")
        #print(filename)
        sprite_path = sprite_dir / filename

        if sprite_path.exists():
            image = mpimg.imread(sprite_path)
            sprite = OffsetImage(image, zoom=0.35)
            box = AnnotationBbox(
                sprite,
                (-0.05, row + 0.5),
                xycoords=ax.transData,
                frameon=False,
                box_alignment=(0.5, 0.5),
                annotation_clip=False,
            )
            ax.add_artist(box)
            
    fig.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02)
    #report_figures.append(fig)
    #fig.savefig(image_path, dpi=150, bbox_inches="tight", pad_inches=0)
    defender_figs[defender] = fig
    plt.close(fig)

merged_damage_figures = {}

for pokemon in attackers:
    pokemon_name = pokemon["name"]

    attacker_image = figure_to_image(attacker_figs[pokemon_name])
    defender_image = figure_to_image(defender_figs[pokemon_name])

    fig = plt.figure(figsize=(14, 7))

    images = [attacker_image, defender_image]
    height = 0.9  # shared image height, as a fraction of the figure
    gap = 0.00

    # Convert image aspect ratios to figure-relative widths.
    width_factors = [
        (image.shape[1] / image.shape[0])
        * (fig.get_figheight() / fig.get_figwidth())
        for image in images
    ]

    # Reduce both images equally if they would exceed the figure width.
    if height * sum(width_factors) + gap > 1:
        height = (1 - gap) / sum(width_factors)

    widths = [height * factor for factor in width_factors]
    left = (1 - sum(widths) - gap) / 2
    bottom = (1 - height) / 2

    for image, width in zip(images, widths):
        ax = fig.add_axes([left, bottom, width, height])
        ax.imshow(image, aspect="equal")
        ax.axis("off")
        left += width + gap

    merged_damage_figures[pokemon_name] = fig
    plt.close(fig)

attackers = read_showdown_team(project_dir / "attackers.txt")

for attacker in attackers:
    name = attacker["name"]
    sprite_path = sprite_path_for(name)

    fig = plt.figure(figsize=(14, 8))

    gs = GridSpec(
    2, 3,
    figure=fig,
    height_ratios=[1, 5],
    width_ratios=[1, 2, 2],
    )

    # Sprite: top left
    sprite_ax = fig.add_subplot(gs[0, 0])
    sprite_ax.axis("off")

    if sprite_path.exists():
        sprite = OffsetImage(mpimg.imread(sprite_path), zoom=1.5)
        box = AnnotationBbox(
            sprite,
            (0.03, 0.97),
            xycoords="axes fraction",
            box_alignment=(0, 1),         # align sprite's top-left to that position
            frameon=False,
        )
        sprite_ax.add_artist(box)
    else:
        print(f"Sprite not found: {sprite_path}")

    # Placeholder text: top middle
    evs = attacker.get("evs", {})
    ev_text = " / ".join(
        f"{stat.upper()} {value}"
        for stat, value in evs.items()
    )

    middle_ax = fig.add_subplot(gs[0, 1])
    middle_ax.axis("off")

    details = (
    f'Level: {attacker.get("level", "—")}  |  '
    f'Nature: {attacker.get("nature", "—")}\n'
    f'Ability: {attacker.get("ability", "—")}  |  '
    f'Item: {attacker.get("item", "—")}\n'
    f'EVs: {ev_text}\n'
    f'{" / ".join(attacker.get("moves", []))}'
    )

    middle_ax.text(
        0.05, 0.8,
        attacker["name"],
        fontsize=48,
        fontweight="bold",
        va="top",
        transform=middle_ax.transAxes,
    )

    middle_ax.text(
        0.05, 0.2,
        details,
        fontsize=18,
        va="top",
        transform=middle_ax.transAxes,
    )

    # Placeholder text: top right
    right_ax = fig.add_subplot(gs[0, 2])
    right_ax.axis("off")

    right_ax.text(
        0.00, 0.2,
        " ",
        fontsize=18,
        va="top",
        transform=right_ax.transAxes,
    )


    graph_ax = fig.add_subplot(gs[1, :])
    graph_ax.imshow(figure_to_image(merged_damage_figures[name]))
    graph_ax.axis("off")

    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, hspace=0.02)
    report_figures.append(fig)
    plt.close(fig)

print("Raw Text")

def read_wrapped_lines(path, width=55):
    lines = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        lines.extend(textwrap.wrap(line, width=width) or [""])
    return lines

attacker_lines = read_wrapped_lines("attackers.txt")
defender_lines = read_wrapped_lines("defenders.txt")

lines_per_page = 48
page_count = max(
    (len(attacker_lines) + lines_per_page - 1) // lines_per_page,
    (len(defender_lines) + lines_per_page - 1) // lines_per_page,
)

for page_num in range(page_count):
    start = page_num * lines_per_page

    fig = plt.figure(figsize=(11, 8.5))
    fig.text(
        0.05, 0.95,
        "\n".join(attacker_lines[start:start + lines_per_page]),
        ha="left", va="top", family="monospace", fontsize=10,
    )
    fig.text(
        0.53, 0.95,
        "\n".join(defender_lines[start:start + lines_per_page]),
        ha="left", va="top", family="monospace", fontsize=10,
    )

    report_figures.append(fig)
    #pdf.savefig(fig)
    plt.close(fig)

with PdfPages("pokemon_report.pdf") as pdf:
    for fig in report_figures:
        pdf.savefig(fig, bbox_inches="tight")

for fig in report_figures:
    plt.close(fig)