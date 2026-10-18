import streamlit as st
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt

st.set_page_config(layout="wide", page_title="Pokemon EV Optimizer")

# --- Core functions (adapted from notebook) ---

def damage(defense_evs, base_defense=80, def_mult=1, atk=150, power=100, level=50, bonus=[1]):
    calculated_defense = math.floor((base_defense + defense_evs + 20) * def_mult)

    raw_damage = math.floor((math.floor( math.floor( (2 * level / 5) + 2) * power * ( (atk) / calculated_defense) ) / 50) + 2 )
    raw_damage_unrounded = (( ( (2 * level / 5) + 2) * power * ( (atk) / calculated_defense) ) / 50) + 2

    for b in bonus:
        raw_damage = math.floor(raw_damage * b)
        raw_damage_unrounded = raw_damage_unrounded * b

    return raw_damage, raw_damage_unrounded


def damage_percent(defense_evs, health_evs, base_health=75, base_defense=80, total_evs=66, def_mult=1, atk=150, power=100, level=50, bonus=[1]):
    if (defense_evs + health_evs) > total_evs:
        return None, None

    calculated_health = base_health + health_evs + 75
    raw_damage, raw_damage_unrounded = damage(defense_evs, base_defense, def_mult, atk, power, level, bonus)
    return raw_damage / calculated_health * 100, raw_damage


# --- Streamlit UI ---
st.title("Pokemon EV Optimizer")

st.sidebar.header("Input Pokémon (manual)")
# we'll collect the defensive pokemon (single) and multiple attacks
df = None

if 'attacks' not in st.session_state:
    st.session_state['attacks'] = []

st.sidebar.markdown("---")
with st.sidebar.form(key='defender'):
    name = st.text_input("Defender Name", value="Defender")
    base_hp = st.number_input("Base HP", value=75, min_value=1)
    base_def = st.number_input("Base Defense", value=80, min_value=1)
    base_spdef = st.number_input("Base Sp. Def", value=80, min_value=1)
    total_evs = st.number_input("Total EVs to use", value=50, min_value=0, max_value=252)
    submitted = st.form_submit_button("Use defender")

if submitted:
    st.session_state['defender_data'] = {"name": name, "hp": base_hp, "defense": base_def, "sp_def": base_spdef, "total_evs": total_evs}
    df = pd.DataFrame([st.session_state['defender_data']])
    st.success(f"Defender '{name}' set")

# Attack input form
with st.sidebar.form(key='attack_form'):
    st.write("Add an attack")
    a_name = st.text_input("Attack name", value="Dire Claw")
    a_power = st.number_input("Power", value=80)
    a_atk = st.number_input("Attacker Attack", value=150)
    a_bonus = st.text_input("Bonus multipliers (comma-separated)", value="1.5,2")
    a_physspec = st.selectbox("Physical or Special", options=["Physical", "Special"])
    add_attack = st.form_submit_button("Add attack")

if add_attack:
    # parse bonuses
    try:
        bonuses = [float(x.strip()) for x in a_bonus.split(",") if x.strip()]
    except Exception:
        bonuses = [1.0]
    st.session_state['attacks'].append({
        'name': a_name,
        'power': float(a_power),
        'atk': float(a_atk),
        'bonus': bonuses,
        'PhySpec': a_physspec,
        'evs': []
    })
    st.success(f"Added attack '{a_name}'")

st.sidebar.markdown("---")

# Select a Pokémon to analyze
if ('defender_data' not in st.session_state) and (df is None or df.empty):
    st.info("Enter a defender in the sidebar to begin.")
    st.stop()
elif 'defender_data' in st.session_state and (df is None or df.empty):
    df = pd.DataFrame([st.session_state['defender_data']])

sel = st.selectbox("Choose Pokémon", options=df["name"].tolist())
row = df[df["name"] == sel].iloc[0]

st.subheader(f"Analyzing {sel}")
col1, col2 = st.columns([2, 3])

with col1:
    st.metric("Base HP", row.get("hp", 75))
    st.metric("Base Def", row.get("defense", 80))
    st.metric("Base Sp.Def", row.get("sp_def", 80))

with col2:
    st.write("### Attacks")
    attacks = st.session_state.get('attacks', [])
    if attacks:
        attack_names = [f"{i}: {a['name']} ({a['PhySpec']})" for i, a in enumerate(attacks)]
        sel_attack_idx = st.selectbox("Select attack to analyze", options=list(range(len(attacks))), format_func=lambda i: attack_names[i])
        sel_attack = attacks[sel_attack_idx]
        st.write(sel_attack)
        total_evs_input = st.number_input("Total EVs", value=total_evs)
        run = st.button("Optimize EVs for selected attack")
        if st.button("Remove selected attack"):
            attacks.pop(sel_attack_idx)
            st.experimental_rerun()
    else:
        st.info("No attacks added yet. Use the sidebar form to add attacks.")
        run = False

if run:
    defender = st.session_state.get("defender_data", {})
    starting_base_health = defender.get("hp", 75)
    starting_base_defense = defender.get("defense", 80)
    starting_base_special_defense = defender.get("sp_def", 80)
    total_evs_def = defender.get('total_evs', 50)
    level = 50

    # Clear previous evs lists
    for a in attacks:
        a['evs'] = []

    evs_map = np.zeros((33, 33))

    attackN = 0
    # Compute evs for each attack
    for a in attacks:
        for i, hp in enumerate(range(0, 33)):
            for j, defense in enumerate(range(0, 33)):
                base_defense = starting_base_defense if a['PhySpec'] == "Physical" else starting_base_special_defense
                evs_map[i, j], raw = damage_percent(defense_evs = defense, health_evs = hp, base_health = starting_base_health, base_defense = base_defense, total_evs = 66-8, def_mult = 1, atk = a['atk'], power = a['power'], level = level, bonus = a['bonus'])
                print(f"HP EVs: {hp}, Defense EVs: {defense}, Damage Percent: {evs_map[i, j]}, Raw Damage: {raw}")
                attacks[attackN]['evs'].append((hp, defense, evs_map[i, j]))

        attackN += 1

    # Build combined optimized_evs across all attacks
    optimized_evs = {hp: {"defense": None, "special_defense": None} for hp in range(33)}

    for a in attacks:
        print(a)
        for hp in range(33):
            pairs = [(ev[1], ev[2]) for ev in a['evs'] if ev[0] == hp and ev[2] is not None]
            if not pairs:
                continue
            under_100 = [(d_ev, dmg) for d_ev, dmg in pairs if dmg < 100]
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

        for o in optimized_evs:
            print(f"HP EVs: {o}, Defense EVs: {optimized_evs[o]['defense']}, Special Defense EVs: {optimized_evs[o]['special_defense']}, Defense Percent: {optimized_evs[o].get('defense_percent')}, Special Defense Percent: {optimized_evs[o].get('special_defense_percent')}")


    for hp in range(33):
            
        if (any(attack["PhySpec"] == "Physical" for attack in attacks) and optimized_evs[hp]['defense'] is None) or (any(attack["PhySpec"] == "Special" for attack in attacks) and optimized_evs[hp]['special_defense'] is None) or (any(attack["PhySpec"] == "Physical" for attack in attacks) and optimized_evs[hp]['defense_percent'] >= 100) or (any(attack["PhySpec"] == "Special" for attack in attacks) and optimized_evs[hp]['special_defense_percent'] >= 100):
            #remove key
            del optimized_evs[hp]
            continue
        defense_evs = 0 if optimized_evs[hp]['defense'] is None else optimized_evs[hp]['defense']
        special_defense_evs = 0 if optimized_evs[hp]['special_defense'] is None else optimized_evs[hp]['special_defense']
        total_evs = hp + defense_evs + special_defense_evs
        optimized_evs[hp]['total_evs'] = total_evs

    if not optimized_evs:
        st.warning("No valid EV combinations found for the current attacks/defender.")
    else:
        min_total_evs = min([optimized_evs[hp]['total_evs'] for hp in optimized_evs])
        best_evs = []
        for hp in optimized_evs:
            if optimized_evs[hp]['total_evs'] == min_total_evs:
                print(f"Optimal HP EVs: {hp}, Optimal Defense EVs: {optimized_evs[hp]['defense']}, Optimal Special Defense EVs: {optimized_evs[hp]['special_defense']}, Total EVs: {optimized_evs[hp]['total_evs']}")
                best_evs.append({
                    'hp': hp,
                    'defense': optimized_evs[hp]['defense'],
                    'special_defense': optimized_evs[hp]['special_defense'],
                    'total_evs': optimized_evs[hp]['total_evs']
                })

        print(best_evs)

        st.write("## Result: Combined Optimization")
        st.write(f"Best HP EVs: {best_evs[0].get('hp',0) if best_evs else 0}")
        st.write(f"Defense EVs: {best_evs[0].get('defense',0) if best_evs else 0}")
        st.write(f"Special Defense EVs: {best_evs[0].get('special_defense',0) if best_evs else 0}")
        st.write(f"Total EVs used: {best_evs[0].get('total_evs',0) if best_evs else 0}")

        st.write("### Per-attack damage at chosen EVs")
        rows = []
        for a in attacks:
            # find damage for this attack at the chosen distribution
            target_def = best_evs[0].get('defense') if a['PhySpec']=="Physical" else best_evs[0].get('special_defense') if best_evs else 0
            dmg = next((ev[2] for ev in a['evs'] if ev[0]==best_evs[0].get('hp',0) and ev[1]==target_def), None) if best_evs else None
            rows.append({"attack": a['name'], "PhySpec": a['PhySpec'], "damage_percent": dmg})
        st.table(pd.DataFrame(rows))

    # st.write("## Result")
    # st.write(f"Optimal HP EVs: {res['optimal_hp_evs']}")
    # st.write(f"Optimal Defense EVs: {res['optimal_defense_evs']}")
    # st.write(f"Minimum Damage %: {res['min_damage_percent']:.2f}%")

    # st.write("### Damage percent table (top rows)")
    # st.dataframe(res['results_df'].head(50))

    # # scatter plot
    # fig, ax = plt.subplots()
    # sc = ax.scatter(res['results_df']["hp_evs"], res['results_df']["def_evs"], c=res['results_df']["damage_percent"], cmap='autumn_r')
    # ax.set_xlabel('HP EVs')
    # ax.set_ylabel('Defense EVs')
    # ax.set_title('Damage % across EV combinations')
    # fig.colorbar(sc, ax=ax, label='Damage %')
    # st.pyplot(fig)

    st.success("Done")
