# none
execute if data storage ccs:config {config:{npcs_enabled:"none"}} run kill @e[nbt={NPCClass:"ccs:npc"}]

# essential_only
execute if data storage ccs:config {config:{npcs_enabled:"essential_only"}} run kill @e[nbt={NPCClass:"ccs:npc"}, tag=!ccs_essential]