# v17.11 Client Gathering Extraction (Island of Dawn)

Scope zones: 13, 64, 213, 313, 364, 436.

## Zone-scope finding

The v17 client carries gathering-node TYPE definitions (Collections) and interactable-object definitions (WorkObjectData) as GLOBAL catalogs keyed by collectionId / templateId. Neither is zone-scoped, and the client has no CollectionTerritory / per-zone gathering placement family. Where IoD gathering nodes spawn (and the items they yield) is server-side, so v31 is the source for scope-zone gathering placement; the client only supplies the node-type catalog.

## Collections (gathering-node type catalog)

Shard `Collections-00000.xml`: 353 collection nodes (global, not zone-scoped). By type:

| typeName | count |
|----------|-------|
| Bug | 48 |
| Energy | 49 |
| Herb | 50 |
| Mine | 49 |
| Quest | 157 |

Full catalog (`questCollection=true` marks quest-only nodes):

| collectionId | name | typeName | grade | neededProficiency | quest |
|-------------|------|----------|-------|-------------------|-------|
| 1 | Verdra Plant | Herb | 1 | 1 | false |
| 2 | Verdra Plant | Herb | 1 | 1 | false |
| 3 | Verdra Plant | Herb | 1 | 1 | false |
| 4 | Sylva Plant | Herb | 2 | 110 | false |
| 5 | Sylva Plant | Herb | 2 | 110 | false |
| 6 | Verdra Plant | Herb | 1 | 1 | false |
| 7 | Sylva Plant | Herb | 2 | 110 | false |
| 8 | Sylva Plant | Herb | 2 | 110 | false |
| 9 | Sylva Plant | Herb | 2 | 110 | false |
| 10 | Sylva Plant | Herb | 2 | 110 | false |
| 11 | Sylva Plant | Herb | 2 | 110 | false |
| 12 | Sylva Plant | Herb | 2 | 110 | false |
| 13 | Shetla Plant | Herb | 3 | 160 | false |
| 14 | Shetla Plant | Herb | 3 | 160 | false |
| 15 | Shetla Plant | Herb | 3 | 160 | false |
| 16 | Shetla Plant | Herb | 3 | 160 | false |
| 17 | Shetla Plant | Herb | 3 | 160 | false |
| 18 | Shetla Plant | Herb | 3 | 160 | false |
| 19 | Shetla Plant | Herb | 3 | 160 | false |
| 20 | Shetla Plant | Herb | 3 | 160 | false |
| 21 | Shetla Plant | Herb | 3 | 160 | false |
| 22 | Toira Plant | Herb | 4 | 210 | false |
| 23 | Toira Plant | Herb | 4 | 210 | false |
| 24 | Toira Plant | Herb | 4 | 210 | false |
| 25 | Toira Plant | Herb | 4 | 210 | false |
| 26 | Toira Plant | Herb | 4 | 210 | false |
| 27 | Toira Plant | Herb | 4 | 210 | false |
| 28 | Toira Plant | Herb | 4 | 210 | false |
| 29 | Toira Plant | Herb | 4 | 210 | false |
| 30 | Toira Plant | Herb | 4 | 210 | false |
| 31 | Luria Plant | Herb | 5 | 270 | false |
| 32 | Luria Plant | Herb | 5 | 270 | false |
| 33 | Luria Plant | Herb | 5 | 270 | false |
| 34 | Luria Plant | Herb | 5 | 270 | false |
| 35 | Luria Plant | Herb | 5 | 270 | false |
| 36 | Luria Plant | Herb | 5 | 270 | false |
| 37 | Luria Plant | Herb | 5 | 270 | false |
| 38 | Luria Plant | Herb | 5 | 270 | false |
| 39 | Luria Plant | Herb | 5 | 270 | false |
| 40 | Luria Plant | Herb | 5 | 270 | false |
| 41 | Luria Plant | Herb | 5 | 270 | false |
| 42 | Luria Plant | Herb | 5 | 270 | false |
| 43 | Luria Plant | Herb | 5 | 270 | false |
| 44 | Luria Plant | Herb | 5 | 270 | false |
| 45 | Luria Plant | Herb | 5 | 270 | false |
| 46 | Luria Plant | Herb | 5 | 270 | false |
| 47 | Luria Plant | Herb | 5 | 270 | false |
| 48 | Luria Plant | Herb | 5 | 270 | false |
| 49 | Dark Blue Leaf Stalk | Herb | 5 | 270 | false |
| 101 | Krymetal Ore | Mine | 1 | 1 | false |
| 102 | Krymetal Ore | Mine | 1 | 1 | false |
| 103 | Krymetal Ore | Mine | 1 | 1 | false |
| 104 | Linmetal Ore | Mine | 2 | 110 | false |
| 105 | Linmetal Ore | Mine | 2 | 110 | false |
| 106 | Krymetal Ore | Mine | 1 | 1 | false |
| 107 | Linmetal Ore | Mine | 2 | 110 | false |
| 108 | Linmetal Ore | Mine | 2 | 110 | false |
| 109 | Linmetal Ore | Mine | 2 | 110 | false |
| 110 | Linmetal Ore | Mine | 2 | 110 | false |
| 111 | Linmetal Ore | Mine | 2 | 110 | false |
| 112 | Linmetal Ore | Mine | 2 | 110 | false |
| 113 | Normetal Ore | Mine | 3 | 160 | false |
| 114 | Normetal Ore | Mine | 3 | 160 | false |
| 115 | Normetal Ore | Mine | 3 | 160 | false |
| 116 | Normetal Ore | Mine | 3 | 160 | false |
| 117 | Normetal Ore | Mine | 3 | 160 | false |
| 118 | Normetal Ore | Mine | 3 | 160 | false |
| 119 | Normetal Ore | Mine | 3 | 160 | false |
| 120 | Normetal Ore | Mine | 3 | 160 | false |
| 121 | Normetal Ore | Mine | 3 | 160 | false |
| 122 | Shadmetal Ore | Mine | 4 | 210 | false |
| 123 | Shadmetal Ore | Mine | 4 | 210 | false |
| 124 | Shadmetal Ore | Mine | 4 | 210 | false |
| 125 | Shadmetal Ore | Mine | 4 | 210 | false |
| 126 | Shadmetal Ore | Mine | 4 | 210 | false |
| 127 | Shadmetal Ore | Mine | 4 | 210 | false |
| 128 | Shadmetal Ore | Mine | 4 | 210 | false |
| 129 | Shadmetal Ore | Mine | 4 | 210 | false |
| 130 | Shadmetal Ore | Mine | 4 | 210 | false |
| 131 | Xermetal Ore | Mine | 5 | 270 | false |
| 132 | Xermetal Ore | Mine | 5 | 270 | false |
| 133 | Xermetal Ore | Mine | 5 | 270 | false |
| 134 | Xermetal Ore | Mine | 5 | 270 | false |
| 135 | Xermetal Ore | Mine | 5 | 270 | false |
| 136 | Xermetal Ore | Mine | 5 | 270 | false |
| 137 | Xermetal Ore | Mine | 5 | 270 | false |
| 138 | Xermetal Ore | Mine | 5 | 270 | false |
| 139 | Xermetal Ore | Mine | 5 | 270 | false |
| 140 | Xermetal Ore | Mine | 5 | 270 | false |
| 141 | Xermetal Ore | Mine | 5 | 270 | false |
| 142 | Xermetal Ore | Mine | 5 | 270 | false |
| 143 | Xermetal Ore | Mine | 5 | 270 | false |
| 144 | Xermetal Ore | Mine | 5 | 270 | false |
| 145 | Xermetal Ore | Mine | 5 | 270 | false |
| 146 | Xermetal Ore | Mine | 5 | 270 | false |
| 147 | Xermetal Ore | Mine | 5 | 270 | false |
| 148 | Xermetal Ore | Mine | 5 | 270 | false |
| 149 | Dark Blue Manacache | Mine | 5 | 270 | false |
| 201 | Sun Essence | Bug | 1 | 1 | false |
| 202 | Sun Essence | Bug | 1 | 1 | false |
| 203 | Sun Essence | Bug | 1 | 1 | false |
| 204 | Essence of Wind | Bug | 2 | 110 | false |
| 205 | Essence of Wind | Bug | 2 | 110 | false |
| 206 | Sun Essence | Bug | 1 | 1 | false |
| 207 | Essence of Wind | Bug | 2 | 110 | false |
| 208 | Essence of Wind | Bug | 2 | 110 | false |
| 209 | Essence of Wind | Bug | 2 | 110 | false |
| 210 | Essence of Wind | Bug | 2 | 110 | false |
| 211 | Essence of Wind | Bug | 2 | 110 | false |
| 212 | Essence of Wind | Bug | 2 | 110 | false |
| 213 | Star Essence | Bug | 3 | 160 | false |
| 214 | Star Essence | Bug | 3 | 160 | false |
| 215 | Star Essence | Bug | 3 | 160 | false |
| 216 | Star Essence | Bug | 3 | 160 | false |
| 217 | Star Essence | Bug | 3 | 160 | false |
| 218 | Star Essence | Bug | 3 | 160 | false |
| 219 | Star Essence | Bug | 3 | 160 | false |
| 220 | Star Essence | Bug | 3 | 160 | false |
| 221 | Star Essence | Bug | 3 | 160 | false |
| 222 | Essence of Ice | Bug | 4 | 210 | false |
| 223 | Essence of Ice | Bug | 4 | 210 | false |
| 224 | Essence of Ice | Bug | 4 | 210 | false |
| 225 | Essence of Ice | Bug | 4 | 210 | false |
| 226 | Essence of Ice | Bug | 4 | 210 | false |
| 227 | Essence of Ice | Bug | 4 | 210 | false |
| 228 | Essence of Ice | Bug | 4 | 210 | false |
| 229 | Essence of Ice | Bug | 4 | 210 | false |
| 230 | Essence of Ice | Bug | 4 | 210 | false |
| 231 | Lightning Essence | Bug | 5 | 270 | false |
| 232 | Lightning Essence | Bug | 5 | 270 | false |
| 233 | Lightning Essence | Bug | 5 | 270 | false |
| 234 | Lightning Essence | Bug | 5 | 270 | false |
| 235 | Lightning Essence | Bug | 5 | 270 | false |
| 236 | Lightning Essence | Bug | 5 | 270 | false |
| 237 | Lightning Essence | Bug | 5 | 270 | false |
| 238 | Lightning Essence | Bug | 5 | 270 | false |
| 239 | Lightning Essence | Bug | 5 | 270 | false |
| 240 | Lightning Essence | Bug | 5 | 270 | false |
| 241 | Lightning Essence | Bug | 5 | 270 | false |
| 242 | Lightning Essence | Bug | 5 | 270 | false |
| 243 | Lightning Essence | Bug | 5 | 270 | false |
| 244 | Lightning Essence | Bug | 5 | 270 | false |
| 245 | Lightning Essence | Bug | 5 | 270 | false |
| 246 | Lightning Essence | Bug | 5 | 270 | false |
| 247 | Lightning Essence | Bug | 5 | 270 | false |
| 248 | Lightning Essence | Bug | 5 | 270 | false |
| 301 | Sun Essence | Energy | 1 | 1 | false |
| 302 | Sun Essence | Energy | 1 | 1 | false |
| 303 | Sun Essence | Energy | 1 | 1 | false |
| 304 | Essence of Wind | Energy | 2 | 110 | false |
| 305 | Essence of Wind | Energy | 2 | 110 | false |
| 306 | Sun Essence | Energy | 1 | 1 | false |
| 307 | Essence of Wind | Energy | 2 | 110 | false |
| 308 | Essence of Wind | Energy | 2 | 110 | false |
| 309 | Essence of Wind | Energy | 2 | 110 | false |
| 310 | Essence of Wind | Energy | 2 | 110 | false |
| 311 | Essence of Wind | Energy | 2 | 110 | false |
| 312 | Essence of Wind | Energy | 2 | 110 | false |
| 313 | Star Essence | Energy | 3 | 160 | false |
| 314 | Star Essence | Energy | 3 | 160 | false |
| 315 | Star Essence | Energy | 3 | 160 | false |
| 316 | Star Essence | Energy | 3 | 160 | false |
| 317 | Star Essence | Energy | 3 | 160 | false |
| 318 | Star Essence | Energy | 3 | 160 | false |
| 319 | Star Essence | Energy | 3 | 160 | false |
| 320 | Star Essence | Energy | 3 | 160 | false |
| 321 | Star Essence | Energy | 3 | 160 | false |
| 322 | Essence of Ice | Energy | 4 | 210 | false |
| 323 | Essence of Ice | Energy | 4 | 210 | false |
| 324 | Essence of Ice | Energy | 4 | 210 | false |
| 325 | Essence of Ice | Energy | 4 | 210 | false |
| 326 | Essence of Ice | Energy | 4 | 210 | false |
| 327 | Essence of Ice | Energy | 4 | 210 | false |
| 328 | Essence of Ice | Energy | 4 | 210 | false |
| 329 | Essence of Ice | Energy | 4 | 210 | false |
| 330 | Essence of Ice | Energy | 4 | 210 | false |
| 331 | Lightning Essence | Energy | 5 | 270 | false |
| 332 | Lightning Essence | Energy | 5 | 270 | false |
| 333 | Lightning Essence | Energy | 5 | 270 | false |
| 334 | Lightning Essence | Energy | 5 | 270 | false |
| 335 | Lightning Essence | Energy | 5 | 270 | false |
| 336 | Lightning Essence | Energy | 5 | 270 | false |
| 337 | Lightning Essence | Energy | 5 | 270 | false |
| 338 | Lightning Essence | Energy | 5 | 270 | false |
| 339 | Lightning Essence | Energy | 5 | 270 | false |
| 340 | Lightning Essence | Energy | 5 | 270 | false |
| 341 | Lightning Essence | Energy | 5 | 270 | false |
| 342 | Lightning Essence | Energy | 5 | 270 | false |
| 343 | Lightning Essence | Energy | 5 | 270 | false |
| 344 | Lightning Essence | Energy | 5 | 270 | false |
| 345 | Lightning Essence | Energy | 5 | 270 | false |
| 346 | Lightning Essence | Energy | 5 | 270 | false |
| 347 | Lightning Essence | Energy | 5 | 270 | false |
| 348 | Lightning Essence | Energy | 5 | 270 | false |
| 349 | Dark Blue Spiritual Energy | Energy | 5 | 270 | false |
| 400 | Veridia Plant | Herb | 1 | 1 | false |
| 401 | Orcan Rations | Quest | 1 | 1 | true |
| 402 | Merchant's Luggage | Quest | 1 | 1 | true |
| 403 | Cloud Mushroom | Quest | 1 | 1 | true |
| 404 | Sweet Hayblossom | Quest | 1 | 1 | true |
| 405 | Barley Sack | Quest | 1 | 1 | true |
| 406 | Toruan | Quest | 1 | 1 | true |
| 407 | Basilisk Egg | Quest | 1 | 1 | true |
| 408 | Merchant's Chest | Quest | 1 | 1 | true |
| 409 | Supply Crate | Quest | 1 | 1 | true |
| 410 | Inscribed Fragment | Quest | 1 | 1 | true |
| 411 | Expedition Member's Corpse | Quest | 1 | 1 | true |
| 412 | Galicho | Quest | 1 | 1 | true |
| 413 | Khamala | Quest | 1 | 1 | true |
| 414 | Relic Fragments | Quest | 1 | 1 | true |
| 415 | Fossilized Bone | Quest | 1 | 1 | true |
| 416 | Weapon Crate | Quest | 1 | 1 | true |
| 417 | Arctus Musk | Quest | 1 | 1 | true |
| 418 | Victim's Remains | Quest | 1 | 1 | true |
| 419 | Golden Pigweed | Quest | 1 | 1 | true |
| 420 | Pirate's Plunder | Quest | 1 | 1 | true |
| 421 | Jettisoned Luggage | Quest | 1 | 1 | true |
| 422 | Expedition Supplies | Quest | 1 | 1 | true |
| 423 | Hazevine | Quest | 1 | 1 | true |
| 424 | Weapons Crate | Quest | 1 | 1 | true |
| 425 | Ancient Relics | Quest | 1 | 1 | true |
| 426 | Instructor's Chest | Quest | 1 | 1 | true |
| 427 | Dig Records | Quest | 1 | 1 | true |
| 428 | Giant Relics | Quest | 1 | 1 | true |
| 429 | Toolbox | Quest | 1 | 1 | true |
| 430 | Stolen Water Barrel | Quest | 1 | 1 | true |
| 431 | Derasa Clam | Quest | 1 | 1 | true |
| 432 | Desert Rose | Quest | 1 | 1 | true |
| 433 | Fragrant Rosehips | Quest | 1 | 1 | true |
| 434 | Lok's Relic | Quest | 1 | 1 | true |
| 435 | Cultist's Remains | Quest | 1 | 1 | true |
| 436 | Not-Lost Relics | Quest | 1 | 1 | true |
| 437 | Essenian Supply Crates | Quest | 1 | 1 | true |
| 438 | Wispy Iceflower | Quest | 1 | 1 | true |
| 439 | Ouijic Ore | Quest | 1 | 1 | true |
| 440 | Dismalweed | Quest | 1 | 1 | true |
| 441 | Suspicious Crate | Quest | 1 | 1 | true |
| 442 | Aetherduct | Quest | 1 | 1 | true |
| 443 | Goddess's Remains | Quest | 1 | 1 | true |
| 444 | Felled Timber | Quest | 1 | 1 | true |
| 445 | Bloodpetal Plant | Quest | 1 | 1 | true |
| 446 | Adderfungus | Quest | 1 | 1 | true |
| 447 | Abandoned Crystal | Quest | 1 | 1 | true |
| 448 | Tertas | Quest | 1 | 1 | true |
| 449 | Shevranberry | Quest | 1 | 1 | true |
| 450 | Victim's Remains | Quest | 1 | 1 | true |
| 451 | Barbed Diamond | Quest | 1 | 1 | true |
| 452 | Tablet | Quest | 1 | 1 | true |
| 453 | Frostvine | Quest | 1 | 1 | true |
| 454 | Arms Crate | Quest | 1 | 1 | true |
| 455 | Aefra | Quest | 1 | 1 | true |
| 456 | Iridescent Nugget | Quest | 1 | 1 | true |
| 457 | Rytenstone | Quest | 1 | 1 | true |
| 458 | Giant Relics | Quest | 1 | 1 | true |
| 459 | Tearroot | Quest | 1 | 1 | true |
| 460 | Garrison Supplies | Quest | 1 | 1 | true |
| 461 | Frozen Corpse | Quest | 1 | 1 | true |
| 462 | Spiritlace | Quest | 1 | 1 | true |
| 463 | Nurea Champignon | Quest | 1 | 1 | true |
| 464 | Faerie Relics | Quest | 1 | 1 | true |
| 465 | Shadow Mushroom | Quest | 1 | 1 | true |
| 466 | Crate of Mana Ore | Quest | 1 | 1 | true |
| 467 | Deathblossom | Quest | 1 | 1 | true |
| 468 | Blooddrop Fungus | Quest | 1 | 1 | true |
| 469 | Food Sack | Quest | 1 | 1 | true |
| 470 | Dead Body | Quest | 1 | 1 | true |
| 471 | Crimson Crystal | Quest | 1 | 1 | true |
| 472 | Cave Mushroom | Quest | 1 | 1 | true |
| 473 | New-Laid Basilisk Egg | Quest | 1 | 1 | true |
| 474 | Frozen Bone | Quest | 1 | 1 | true |
| 475 | Mekonari Bloodtomb | Quest | 1 | 1 | true |
| 476 | Sikandari Egg | Quest | 1 | 1 | true |
| 477 | Ancient Amani Remains | Quest | 1 | 1 | true |
| 478 | Dreamreaper Core | Quest | 1 | 1 | true |
| 479 | Piercing Crystal | Quest | 1 | 1 | true |
| 480 | Eclipse Thistle | Quest | 1 | 1 | true |
| 481 | Argon Appurtenance | Quest | 1 | 1 | true |
| 482 | Flamelicked Ore | Quest | 1 | 1 | true |
| 483 | Discarded Orb | Quest | 1 | 1 | true |
| 484 | Brigand Supplies | Quest | 1 | 1 | true |
| 485 | Old Document Folder | Quest | 1 | 1 | true |
| 486 | Old Harvest | Quest | 1 | 1 | true |
| 487 | Townsfolk's Belongings | Quest | 1 | 1 | true |
| 488 | Glowing Ore | Quest | 1 | 1 | true |
| 489 | Abandoned Treasure Chest | Quest | 1 | 1 | true |
| 490 | Deserted Timber | Quest | 1 | 1 | true |
| 491 | Kaidun Supplies | Quest | 1 | 1 | true |
| 492 | Skyreach Flower | Quest | 1 | 1 | true |
| 493 | Azure Shard | Quest | 1 | 1 | true |
| 494 | Xanthic Shard | Quest | 1 | 1 | true |
| 495 | Crimson Shard | Quest | 1 | 1 | true |
| 496 | Mock Rock | Quest | 1 | 1 | true |
| 497 | Cultist Weapon Chest | Quest | 1 | 1 | true |
| 498 | Mysterious Lab Item | Quest | 1 | 1 | true |
| 499 | Astrocorn Fungus | Quest | 1 | 1 | true |
| 500 | Azurebond Stalk | Quest | 1 | 1 | true |
| 501 | Blood Crystal | Quest | 1 | 1 | true |
| 502 | Artful Gracebloom | Quest | 1 | 1 | true |
| 503 | Hummingrock | Quest | 1 | 1 | true |
| 504 | Dewdrop Bush | Quest | 1 | 1 | true |
| 505 | Glacial Ice | Quest | 1 | 1 | true |
| 506 | Pile of bones | Quest | 1 | 1 | true |
| 507 | Defender's Corpse | Quest | 1 | 1 | true |
| 508 | Stack of Weapons | Quest | 1 | 1 | true |
| 509 | Strelitzia | Quest | 1 | 1 | true |
| 510 | Dead Lambs | Quest | 1 | 1 | true |
| 511 | Argon Supply Crate | Quest | 1 | 1 | true |
| 512 | Prion's Treasure | Quest | 1 | 1 | true |
| 513 | Malodorous Flower | Quest | 1 | 1 | true |
| 514 | Salixia Flower | Quest | 1 | 1 | true |
| 515 | Toolbox | Quest | 1 | 1 | true |
| 516 | Spider Egg Sac | Quest | 1 | 1 | true |
| 517 | Mummified Remains | Quest | 1 | 1 | true |
| 518 | Contaminated Well | Quest | 1 | 1 | true |
| 519 | Dropwort | Quest | 1 | 1 | true |
| 520 | Orcan Jerky | Quest | 1 | 1 | true |
| 521 | Red Dogbane | Quest | 1 | 1 | true |
| 522 | Naga Egg | Quest | 1 | 1 | true |
| 523 | Dagon's Scale | Quest | 1 | 1 | true |
| 524 | Villager's Corpse | Quest | 1 | 1 | true |
| 525 | Old Jar | Quest | 1 | 1 | true |
| 526 | Autumn Mushroom | Quest | 1 | 1 | true |
| 527 | Liquor Flask | Quest | 1 | 1 | true |
| 528 | Crimson Shard | Quest | 1 | 1 | true |
| 529 | Horn Mound | Quest | 1 | 1 | true |
| 530 | Burnt Ore | Quest | 1 | 1 | true |
| 531 | Casian’s New Sprout | Quest | 1 | 1 | true |
| 532 | Raindrop Bellflower | Quest | 1 | 1 | true |
| 533 | Argon Test Tube | Quest | 1 | 1 | true |
| 534 | Box of Vision | Quest | 1 | 1 | true |
| 535 | Moon Shadow Plant | Quest | 1 | 1 | true |
| 536 | Moonlight Lotus | Quest | 1 | 1 | true |
| 537 | Stone Box | Quest | 1 | 1 | true |
| 538 | Arkai’s Egg | Quest | 1 | 1 | true |
| 539 | Argon Wildflower | Quest | 1 | 1 | true |
| 540 | Argon Construction Tools | Quest | 1 | 1 | true |
| 541 | Argon Building Debris | Quest | 1 | 1 | true |
| 542 | Mutated Plant | Quest | 1 | 1 | true |
| 543 | Mutated Mushroom | Quest | 1 | 1 | true |
| 544 | Mutated Flower | Quest | 1 | 1 | true |
| 545 | Destroyed Argon Component | Quest | 1 | 1 | true |
| 546 | Component of the Destroyed Siege Tank | Quest | 1 | 1 | true |
| 547 | Ancient Legacy | Quest | 1 | 1 | true |
| 548 | Orange Cap Mushroom | Quest | 1 | 1 | true |
| 549 | Duckweed | Quest | 1 | 1 | true |
| 550 | Argonite Ore | Quest | 1 | 1 | true |
| 551 | Contaminated Mushroom | Quest | 1 | 1 | true |
| 552 | Argonized Plant | Quest | 1 | 1 | true |
| 553 | Corpse of the Expedition Member | Quest | 1 | 1 | true |
| 554 | Corpse of the Kanstria Outrider | Quest | 1 | 1 | true |
| 555 | Corpse of the Guerilla | Quest | 1 | 1 | true |
| 556 | Lamenting Grass | Quest | 1 | 1 | true |
| 557 | Tainted Mountain Debris | Quest | 1 | 1 | true |

## WorkObjectData (interactable-object catalog)

Shard `WorkObjectData-00000.xml`: 92 interactable objects (levers, altars, coffins, defense stones, etc.), global, keyed by templateId. `isForQuestId` links an object to a quest (0 = none).

| templateId | name | isForQuestId | socialMotionId |
|-----------|------|--------------|----------------|
| 1 | Engine of Mischief | 0 | 21 |
| 2 | Vortex Shard | 0 | 11 |
| 3 | Mysterious Altar | 332 | 11 |
| 4 | Count's Coffin | 1503 | 13 |
| 5 | Countess's Coffin | 1503 | 13 |
| 6 | Ancient Tombstone | 0 | 11 |
| 7 | Sealing Device | 2702 | 11 |
| 8 | Purification Device | 2802 | 11 |
| 10 | Treasure Chest | 0 | 11 |
| 23 | Magic Stone Pillar | 0 | 11 |
| 24 | Emancipation Pillar | 0 | 11 |
| 27 | Serena's Ephemeral Guardian | 2304 | 11 |
| 29 | Resurrection Stone | 0 | 11 |
| 30 | Relic of Dagon | 4201 | 11 |
| 31 | Dimensional Hold | 2502 | 11 |
| 32 | Stealth Menhir | 302 | 11 |
| 33 | Weapon Crate | 602 | 11 |
| 34 | Secure Chest | 604 | 11 |
| 35 | Weather Station | 5125 | 11 |
| 36 | Weather Station | 5125 | 11 |
| 37 | Morbolith Mill | 3901 | 11 |
| 38 | Vertex of Eternity | 3701 | 11 |
| 39 | Vertex of Eternity | 3701 | 11 |
| 40 | Vertex of Eternity | 3701 | 11 |
| 41 | Killian's Necromantic Surgery | 5301 | 11 |
| 42 | Energy Cell | 0 | 11 |
| 43 | Menhir Casing | 3703 | 11 |
| 44 | Black Tower Defense Control | 3702 | 11 |
| 45 | Sparking Baetylith | 701 | 11 |
| 46 | Strange Seal | 0 | 11 |
| 47 | Pirate's Treasure Chest | 4201 | 11 |
| 48 | Priest's Treasure Chest | 4201 | 11 |
| 49 | Ore Refiner | 3534 | 11 |
| 51 | Ishlangu | 5502 | 11 |
| 52 | Secluded Terrace Teleportal | 0 | 11 |
| 53 | Strange Seal | 0 | 11 |
| 54 | Smoldering Bloodshard | 444 | 11 |
| 55 | Grave of the Unknown Soldier | 1047 | 11 |
| 56 | [Low Grade] Summoning Stone | 0 | 11 |
| 57 | [Middle Grade] Summoning Stone | 0 | 11 |
| 58 | [High Grade] Summoning Stone | 0 | 11 |
| 59 | Training Stone | 0 | 11 |
| 60 | Shadow Reaver’s Tombstone | 4841 | 11 |
| 61 | Purification Stone Operation Device No. 1 | 0 | 11 |
| 62 | Purification Stone Operation Device No. 2 | 0 | 11 |
| 63 | Purification Stone Operation Device No. 3 | 0 | 11 |
| 64 | Argon Watch Device | 0 | 11 |
| 65 | Argon Watch Device | 0 | 11 |
| 66 | [Low Grade] Summoning Stone | 0 | 11 |
| 67 | [Middle Grade] Summoning Stone | 0 | 11 |
| 68 | [High Grade] Summoning Stone | 0 | 11 |
| 69 | [Low Grade] Summoning Stone | 0 | 11 |
| 70 | [Middle Grade] Summoning Stone | 0 | 11 |
| 71 | [High Grade] Summoning Stone | 0 | 11 |
| 72 | [Low Grade] Summoning Stone | 0 | 11 |
| 73 | [Middle Grade] Summoning Stone | 0 | 11 |
| 74 | [High Grade] Summoning Stone | 0 | 11 |
| 75 | Banana Tree | 0 | 11 |
| 76 | Feed Container for Fish Farming | 0 | 11 |
| 77 | Lighthouse Ignition Device | 0 | 11 |
| 78 | Tree of Life | 4701 | 11 |
| 79 | Contaminated Lake Wardstone | 4701 | 11 |
| 80 | Valkyon Flag | 0 | 11 |
| 81 | Live Body Experiment Tool Controller | 60114 | 11 |
| 82 | Live Body Experiment Tool Controller | 60114 | 11 |
| 83 | Live Body Experiment Tool Controller | 60114 | 11 |
| 84 | Argon Incubator | 0 | 11 |
| 85 | Argon Portal | 60208 | 11 |
| 86 | Power Supply Switch | 0 | 13 |
| 87 | Power Supply Switch | 0 | 13 |
| 88 | Allemantheian Communication Machine | 3001 | 11 |
| 89 | Repository of Wisdom | 3002 | 11 |
| 90 | Broken Repository of Wisdom | 3038 | 11 |
| 91 | Garden of the Sun Stone Lantern | 3047 | 11 |
| 92 | Seren's Seal | 3002 | 11 |
| 93 | Seren's Seal | 3003 | 11 |
| 94 | Mysterium Encyclopedia | 3022 | 11 |
| 95 | Tombstone of the Sun God | 0 | 11 |
| 96 | Banana Tree for Planting | 0 | 11 |
| 97 | Broken Argon Contamination Structure | 0 | 11 |
| 98 | Argon Transmitter Control Console | 0 | 11 |
| 99 | Mysterious Argon Device | 0 | 11 |
| 100 | Broken Argon Fortress Pillar | 4535 | 11 |
| 101 | Broken Structure Remains | 4535 | 11 |
| 102 | Plant Subject Water Tank | 0 | 11 |
| 103 | Shandra’s Root | 5021 | 11 |
| 104 | Mirror of Light | 0 | 13 |
| 105 | Cannon Repair Switch | 0 | 13 |
| 106 | Magic Detector | 0 | 11 |
| 107 | Manacache of Protection | 0 | 11 |
| 108 | Protected Manacache | 0 | 11 |
| 109 | Manacache of the Wall | 0 | 11 |

