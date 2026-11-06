# Ensure the helper display entity exists
execute unless entity fccbfdf9-84d1-4962-b573-0ecc4ff79c98 run summon item_display ~ ~ ~ {UUID:[I;-53740039,-2066658974,-1250750772,1341627544]}

# Put the exploration map into the entity to calculate coordinates
loot replace entity fccbfdf9-84d1-4962-b573-0ecc4ff79c98 contents loot ccs:maps/pewter

# Copy map decoration coordinates to storage
data modify storage ccs:data pewter set from entity fccbfdf9-84d1-4962-b573-0ecc4ff79c98 item.components."minecraft:map_decorations".+
title @s actionbar {"translate":"pewter: x=%s z=%s","with":[{"storage":"ccs:data","nbt":"pewter.x"},{"storage":"ccs:data","nbt":"pewter.z"}]}

# Execute the macro teleport using the storage coordinates
function ccs:tp_exec with storage ccs:data pewter