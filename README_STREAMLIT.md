# Pokemon EV Optimizer — Streamlit

Run locally:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Usage:
- Upload a CSV with columns `name`, `hp`, `defense`, `sp_def` or enter a Pokémon manually in the sidebar.
- Set attacker `atk` and move `power`, then click `Optimize EVs` to compute the optimal HP/Defense EV split.

Notes:
- This is a minimal port of the notebook logic. You can expand to support multiple moves, STAB/bonuses, or export results.
