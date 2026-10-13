data get storage ccs:config Config.SilphRandomRewards

execute store result score #RandomRewards ccs_temp run data get storage ccs:config Config.SilphRandomRewards

execute if score #RandomRewards ccs_temp matches 1 run runmolang "q.player.data.silph_random_rewards=1" @s
execute if score #RandomRewards ccs_temp matches 0 run runmolang "q.player.data.silph_random_rewards=0" @s