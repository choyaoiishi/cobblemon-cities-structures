# default to spawn all npc
execute unless data storage ccs:config config.npcs_enabled run data modify storage ccs:config config.npcs_enabled set value "all"