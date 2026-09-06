# Changelog

What changed in TERA Reforged, written for players.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). One entry per
patch, newest first. An entry is written only when a patch has shipped, so everything below
is live on the server.

Every change here comes from a spec in this repository, if you want the exact numbers.

## [Patch 004] - 2026-09-05

Velika and Arcadia begin their return to the classic game: the places, names and merchants
of the early continent as they were, and the instances that arrived later closed.

### Added

- The Free Traders Hall is back in Velika, with its name and its place on the world map.
- The Velika Federation union fields and their fortress towns are back on the world map.
- The classic solo Bastion of Lok can be entered again from the entry stone in Oblivion Woods, beside the party version. Each solo visit takes you through one half of the dungeon, chosen when you enter, with its own way out at the end.
- Velika, Crescentia and Lumbertown have their classic crafting-material and design merchants back, selling what they sold in the early game.
- The guild quest board and its turn-in are available again from the Mission Board and Verise in Velika.

### Changed

- The Berzerad Cemetery ring in Arcadia has its classic boundary again.
- Crystal merchants everywhere sell the classic weapon and armor crystals instead of the Fine range.
- Mounts are no longer allowed inside the Valkyon Federation headquarters.
- Merchants and villagers in Velika, Crescentia, Lumbertown and Arcadia offer their classic menus again.

### Removed

- The instances added to Velika and Arcadia after the classic game are closed: the Velika Banquet, Velik's Hold, Velik's Sanctuary, Wonderholme, Antaroth's Abyss, Harrowhold, Broken Prison, the solo trials and the solo rework of Bastion of Lok.
- The entry NPCs of those instances no longer offer them.

### Fixed

- The party Bastion of Lok's gate to the lower half is back. It had been missing since the solo rework was added.

## [Patch 003] - 2026-08-23

The Island of Dawn gets its first field event, and a long list of reported problems gets
answered. The client also ships in two more languages for the first time.

### Added

- Guardian Legion: Orcan Raiders, the first field event to run on the Island of Dawn. Clear the raider wave to draw out the Orcan Warlord Acharak, then bring him down before the mission closes.
- The exploding barrels around the Orcan camp are now a weapon. Pull a Guardian Legion monster onto one and break it. The blast does not care who is standing nearby, you included.
- Gear dismantling. Combat gear in the early ranks now breaks down into enchant materials. Most of it was already marked breakable and refunded nothing.
- The Semi-Enigmatic Scroll now sells on the Valkyon Quartermaster's Materials tab.
- Spanish and Brazilian Portuguese, selectable in the launcher. Both are machine-translated first drafts under review, and anything not yet translated stays in English.

### Changed

- New accounts start with six character slots instead of three.
- Infusion costs almost nothing while you are levelling and starts to bite from the fourth gear rank, climbing to meet the price the game already charged at the top.
- Tank weapons absorb 20% more damage on a block at the level cap.
- Chat channels no longer carry a level requirement.
- The Island of Dawn now uses the classic terrain, which clears up the areas where skills would refuse to fire.
- Leman now survives beside you in Karascha's Lair instead of dying to the first hit he takes.
- The Orcan Warlord fights to his own battle music.

### Fixed

- The Mystic's Boomerang Pulse travels where you aim it. It used to launch at a fixed upward angle no matter where you pointed.
- Blocking with a tank weapon now absorbs the damage it is supposed to.
- Sorcha's repeatable challenge completes for every member of the party, not only whoever tripped it.
- Teleporting between two points on the Island of Dawn no longer drops you out of your party.
- Infusion boxes draw evenly across their whole reward list. They used to hand out the same single item on every open.
- Attack-speed and damage-reflection charms were applying the wrong effect. Attack-speed charms had been healing the wearer to full instead of doing anything to attack speed.
- Gameforge's system announcements, links and sender name are gone from chat.

## [Patch 002] - 2026-08-09

The first Reforged patch. Patch 001 rebuilt the Island of Dawn as it was in the classic game;
this one is where Reforged starts making its own choices, on top of that island and across the
whole world's gear and enchanting.

### Added

- The Valkyon Commendation, an Island of Dawn currency paid out by story quests, side quests and
  repeatable work, and spent with Deren the Valkyon Quartermaster at Tower Base.
- Sorcha and her guard now stand at Tower Base once you have cleared her instance, selling four
  cosmetics found nowhere else in exchange for Sorcha's Sigil.
- A repeatable run of Sorcha's instance for characters between level 8 and 12, paying Sigils on
  every clear, so her shelf is reachable instead of decorative.
- Bounty Brokers at Tower Base and at the Tainted Gorge Outpost.
- The Valkyon Fortune Cache, a cosmetic cache on the Quartermaster's shelf.
- The Regal Frostlion mount, sold by Sorcha.
- Dyad crystals for weapons and armour across six tiers, with the customizing bags and passive
  effects that belong to them.
- Potential unlock for gear, and top rolls on chest pieces.
- Gear infusion, along with infusion boxes and crystal boxes.
- Every new character now knows Retaliate from the moment it is created.

### Changed

- **Side quests own your gear now, and the story owns the story.** On the Island of Dawn the
  level 4 and level 7 outfits are earned from side quests, while story quests pay experience and
  gold. Every class can complete a full matching look at each step.
- The level 8 set is bought with the tokens Kugai drops, rather than handed to you whole by a
  story quest.
- All enchanting consumes a single feedstock material instead of a ladder of tiers, so what you
  gather early does not go stale later.
- Island of Dawn quest experience was re-paced downward. The island no longer levels you clean
  past its own content before you have seen it.
- Every open-world region starts on one channel and opens a second only once it passes 300
  players, so the world reads as populated rather than empty.
- The starting kit is trimmed, the starter mount is usable from level 1, and the Bay Gelding
  riding skill can be learned at level 1.
- For the limited alpha, the Island of Dawn is sealed. Scrolls, journal travel and summons will
  not take you off the island, while the portals within it work as before.

### Removed

- Five Island of Dawn side quests were retired. Each one repeated another quest task for task, or
  paid a reward you had already been given for doing the same thing. The chains around them were
  re-anchored, so nothing is left stranded.
- The level 5 and 6 gear step. There is deliberately nothing between the level 4 outfit and the
  level 7 one.

### Fixed

- **Priest and Mystic healing.** Both classes healed for almost nothing. Every heal, and every
  heal-over-time effect, now restores what it is supposed to.
- Quest rewards appear in the quest log again. The accept window and the payout were always
  right; the log panel beside them was empty.
- Teleport scrolls and death revives on the Island of Dawn return you to the Tower Base, instead
  of dropping you at the North Dock on the far side of the island.
- Brawlers, Ninjas and Valkyries are given weapons that match their level on the Island of Dawn,
  and are offered the class quests they were silently being skipped for.
- The terron collecting quests have enough of the right terrons to actually finish, rather than
  three that do not count for every one that does.
- Sorcha's instance can no longer be completed by talking to her and waiting out the clock.
