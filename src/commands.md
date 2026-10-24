### loot table
/data get block <x> <y> <z>
/data merge block <x> <y> <z> {LootTable:"ccs:towns/foods"}

### cobbledollars
/summon cobbledollars:cobble_merchant ~ ~ ~ {attributes:[{id:"minecraft:generic.movement_speed",base:0.0d}]}

### rctmod
/rctmod trainer summon_persistent team_rocket_grunt ~ ~ ~ {attributes:[{id:"minecraft:generic.movement_speed",base:0.0d}]}

/summon minecraft:marker ~ ~ ~ {Tags:["boss_giovanni_1_pos"]}

/kill @e[type=cobblemon:npc, sort=nearest, limit=1]

https://github.com/TempusMMORPG/TempusScripts/blob/main---1.7.x/TempusNpcs/data/cobblemon/molang/kill_pokemon_entity.molang