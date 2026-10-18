const { Generations, Pokemon, Move, Field, calculate } = require("@smogon/calc");

let input = "";

process.stdin.setEncoding("utf8");
process.stdin.on("data", (chunk) => {
  input += chunk;
});

process.stdin.on("end", () => {
  try {
    const config = JSON.parse(input);
    const gen = Generations.get(config.generation ?? 0);
    const results = config.matchups.map(({ attacker: attackerSet, defender: defenderSet, move: moveName, field: matchupField }) => {
      const attacker = new Pokemon(gen, attackerSet.name, {
        level: attackerSet.level ?? 50,
        nature: attackerSet.nature,
        item: attackerSet.item,
        ability: attackerSet.ability,
        evs: attackerSet.evs,
        ivs: attackerSet.ivs,
        boosts: attackerSet.boosts,
      });

      const defender = new Pokemon(gen, defenderSet.name, {
        level: defenderSet.level ?? 50,
        nature: defenderSet.nature,
        item: defenderSet.item,
        ability: defenderSet.ability,
        evs: defenderSet.evs,
        ivs: defenderSet.ivs,
        boosts: defenderSet.boosts,
      });

      const field = matchupField ? new Field(matchupField) : (config.field ? new Field(config.field) : undefined);
      const move = new Move(gen, moveName);
      const result = calculate(gen, attacker, defender, move, field);
      const attackerStats = result.attacker.stats;
      const defenderStats = result.defender.stats;
      const [minDamage, maxDamage] = result.range();
      const description =
        maxDamage === 0 && move.category !== "Status"
          ? `${attackerSet.name} ${moveName} vs. ${defenderSet.name}: 0 damage`
          : result.desc();

      return {
        attacker: attackerSet.name,
        defender: defenderSet.name,
        move: moveName,
        category: move.category,
        damage: result.damage,
        maxDamage,
        minDamage,
        description,
        attackerStats: {
          hp: result.attacker.maxHP(),
          atk: attackerStats.atk,
          def: attackerStats.def,
          spa: attackerStats.spa,
          spd: attackerStats.spd,
          spe: attackerStats.spe,
        },
        defenderStats: {
          hp: result.defender.maxHP(),
          atk: defenderStats.atk,
          def: defenderStats.def,
          spa: defenderStats.spa,
          spd: defenderStats.spd,
          spe: defenderStats.spe,
        },
      };
    });

    console.log(JSON.stringify(results));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
});
