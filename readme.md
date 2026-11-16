```bash
git clone https://github.com/switzere/Pokemon-Stat-Optimize.git
cd Pokemon-Stat-Optimize
pip install -r requirements.txt
npm install   
python "optimize scorecard.py"
```

Requires Python 3.9+ and Node.js.

The script reads the teams from `attackers.txt` and `defenders.txt` (Pokémon Showdown format) and writes `pokemon_report.pdf` next to the script.