### 30-10-2026 - 1.0.15
- fix scientist dont have pokemon
- fix teams only have 1 and level 1 pokemon

### 29-10-2026 - 1.0.14
#### structures
- added celadon department store
- added farmers market in viridian

#### config
- added option to disable npcs in server config

#### mechanics
- removed rctmod dependency. battles now use native cobblemon system
	- trainers use random pokemon from preset teams without repeats
	- trainers have multiple teams that scale with player level
	- trainer pokemon level scales with the player's highest-level pokemon (with slight variation)
	- trainer party size varies based on trainer type and player level
	- set minimum levels for key trainers to prevent early end-game boss fights
- added advancements
- added optional cobbleverse badge mod support:
	- starter kit includes a kanto badge box (if installed)
	- defeating gym leaders awards their respective badge (if installed)

#### bug fixes
- fixed misty's winning dialogue not triggering

### 24-10-2026 - 1.0.13
#### structures:
- changed grid from 9x9 to 11x11 to make cities more compact
- rebuilt saffron houses, celadon houses, and silph co to match the game design
	- silph co now uses teleporter tiles instead of abra
- updated rocket game center hidden stairs
- added cerulean cave
- added road entrances so roads connect directly to buildings
- added street decorations as streets are wider now
- changed biome tags to cobblemon tags to support modded biomes

#### config:
- changed the silph reward command to: /opendialogue ccs:server_config @s

#### npc:
- npcs can now start dialogue when they see you
- added minimap icons
- moved npc text to dialogue files for easier updates
- moved npc functions like rewards and trades into molang for easier maintenance

### 14-10-2026 - 1.0.12
- add optional starter kit and start radical red series in the welcome dialogue
- change pewter search radius to 100
- add names for npc
- add new items that can be sold to pokemart
- make all exploration map skip_existing_chunks to false
- disable vanilla mobs spawn in the cities 
- change cities biome to cobblemon tags
- fix celadon not showing 3x2 buildings

### 13-10-2026 - 1.0.11
battle:
- add pre-battle dialogue and win dialogue
- add give item, tm, pokemon on win

saffron:
- add silph co building
- add option to toggle the silph co reward:
	- /function ccs:silph/set_fixed_reward
	- /function ccs:silph/set_random_reward

textures:
- change textures to 2 pixel height eye
- add new textures for npc, rockets, rivals and leaders

gameplay:
- add welcome diagloue and teleport to pewter option after choosen the starter
- add key trainers to the cities. radical red can now progress up to cinnabar gym

### 09-10-2026 - 1.0.10
- fix waystone processor list error

### 08-10-2026 - 1.0.09
- packaged into a single mod

#### assets
add
- placeholder
- fisher
- psychic
- camper
- richboy
- bugcatcher
- youngster
- pokeball

change texture
- gentleman
- hiker
- shopkeeper
- rocket grunt

### 08-10-2026 - 1.0.08
- added city npcs
- added npc trading, tms, and item rewards
- added slot machines function and game corner prize exchange
- added skyscraper buildings
- added pokemart clerk selling special poke balls in each cities
- fixed the viridian gym leader spawning the wrong trainer
- moved the town guide to the pokemon center
- added town guide map giveaways

### 30-09-2026 - 1.0.07
- Add foundation for more modern looks
- Add town center and guide
- Add cobblemon berries
- Add decos to make cities unique
- Add animation to npc
- new houses design

### 23-09-2026 - 1.0.06
- Add town center and town guide for pewter and cerulean
- Move all dialogues and npcs into custom namespace

### 22-09-2026 - 1.0.05
- Add loot_table
- Change pokemart npc to cobbledollar's
- Add rocket grunt trainer to game center
- Rearrange houses interior

### 21-09-2026 - 1.0.04
- Fix museum lamp position
- Fix pokemart floor light blue get replaced
- Fix vermilion gym chisel copper oxidized
- Fix cerulean fence not connecting properly
- New pack icon

### 21-09-2026 - 1.0.03
- Hide rocket hideout entrance

### 21-09-2026 - 1.0.02
- Adjust houses spawning rate
- Add limit to berry, flower garden and patches spawn

### 21-09-2026 - 1.0.01
- Overhaul all houses
- Add gradient to the roofs
- Add celadon game center
- Add team rocket grunt and nerd npcs

### 18-09-2026 - 1.0.0
- Add all 8 Kanto gyms with towns, houses, decorations, pokmarts, and pokecenters
- Add pewter museum
- Add pokemon fan club
- Add nurse, shopkeeper, gentleman, scientist, and lass npcs