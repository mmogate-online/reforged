# Classic Restoration: Source Strategy Assessment

Date: 2026-07-20. Author: agent analysis at user request. Status: recommendation for decision.

## The question

Does the current doctrine (v17.11 client as north star, v31 server as gap-fill) scale to the
full classic-restoration project, or should we pivot to a v31-primary baseline with v17 filling
only the gaps that are still intact or cheap to replicate?

This is prompted by the IoD live test, where the story spine (Leander's Outpost, the traveling
Leander, Priscus/1389) exposed that spawn data is brittle and incomplete in both sources and
that reconstruction depended on watching a gameplay video.

## The core structural finding (this is the whole issue)

Spawn positions and conditional-spawn wiring live ONLY in server data.

- **v17.11 is a CLIENT.** It has quest logic, quest/dialog text, NPC templates and names, and map
  geometry. It has **zero NPC spawn positions**: its `TerritoryData` is geometry-only (fence
  polygons). Proven three times this session (the extracted `v17-territories.json` is geometry
  only; the raw `TerritoryData-00025.xml` for HZ 213 holds just 3 generic groups with no `Npc`
  placements).
- **The only classic-era SERVER we have is v31**, which is the same rework era as v92: stripped
  progression, flattened spawns, 40 IoD quests sentinel-disabled.

Consequence: **v17 can never be the source of truth for spawns.** The founding assumption, that the
relevant v17-era data survives inside v31, is exactly inverted for spawns: v17 never contained
them, and v31 contains them only in stripped form. "v17 north star for spawn layout" was
structurally impossible from day one; IoD is simply where that surfaced.

## What each source can and cannot provide

| Data type | v17.11 client | v31 server | v92 server (current) |
|---|---|---|---|
| Quest logic (tasks, givers, prereqs) | Full, classic | Full, reworked | Full, reworked |
| Quest / dialog / journal text | Full, classic (some KR-only = dormant) | Full | Full |
| NPC templates + names | Full | Full | Full |
| Rewards (class bags) | Full, classic display data | Reworked | Reworked |
| **NPC spawn positions** | **NONE (client)** | Present but STRIPPED | Present (v31 + our spec 02) |
| **Conditional / traveling spawns** | **NONE** | **NONE (flattened)** | **NONE** |
| Territory / fence geometry | Full | Full | Full |
| Mob habitats / gathering | Derivable | Present, largely intact | Present, correct |

The two rows in bold are the entire problem. Everything else is recoverable from v17 cheaply and
has been working.

## Quantified gaps (measured this session)

- **63 classic IoD quests** existed (v17, `Quest번호 13,*`). ~40 were sentinel-disabled in the
  v31/v92 rework: roughly **63% of the IoD spine was stripped**. This is the "half the map voided"
  pattern, quantified, and it repeats across reworked continents.
- **10 quest-giving/receiving NPCs are unspawned** in BOTH v31 and v92 (whole camps never built
  server-side): Leander's Outpost roster (Eria 1021, Jehan 1130, Ayrdoss 1126, Lorin 1128, plus
  Priscus 1020) and the Kamarnu/Riel/Kirash/Clovis/Milun set. These break ~16 quests.
- **0 `conditionalSpawn="true"`** across all six IoD territory files in v31 AND v92 (808 v92 spawns,
  641 v31 spawns scanned). The classic quest-gated / traveling-NPC choreography (Leander appearing
  at outpost, then shrine, then Tower Base per quest step) is entirely absent from the data. It is
  **unrecoverable from any datasheet we hold**; the only evidence is external video.
- **v92 already carries 808 IoD spawns vs v31's 641.** Our patch-001 spec 02 has already pushed the
  live server ABOVE v31's spawn density. We are no longer "restoring toward v31"; we have passed it.

## Cost and scale reality

- One continent (IoD: 6 hunting zones, 63 quests) has consumed multiple sessions and still has open
  camps. Final NPC placement required a **gameplay video** because no datasheet source has the
  positions.
- **Video does not exist for most zones.** Where it does not, unbuilt-camp spawns and traveling-NPC
  choreography are simply unrecoverable. There is no source to reconstruct from.
- The **3-source reconciliation** the doctrine requires (does it exist in v17, how is it encoded in
  v31, what does v92 have) is precisely where the automated audits failed:
  - Eria was classified MATCH while being unspawned (existence compared, not placement).
  - Priscus was written off as an "event guide, do-not-place" when he actually gives a live English
    quest (1389 "Emptying Pandora's Box"); a wrong-format grep (`template="1020"` vs the v17 comma
    form `213,1020`) hid it.
  - The traveling-Leander / conditional-spawn mechanic was never detected.
  These are systematic failure modes of reconciling three divergent sources, not isolated slips.
  They will recur, and worse, in zones with less scrutiny than IoD received.

## Options

### A. Keep v17-primary (current doctrine)
- Pro: maximal fidelity intent; treats classic content as authoritative.
- Con: cannot deliver spawn fidelity anyway (v17 has no spawns; the ceiling is set by v31 + video
  regardless). Adds a heavy 3-source reconciliation and per-zone video-reconstruction burden on top
  of that same spawn floor. Does not scale past zones we have video for. Highest agent-error surface.

### B. Pivot to a v31-primary structural baseline + selective v17 overlay
- Pro: v31 is the only COMPLETE, internally-consistent classic-era server. A spawned NPC in v31 is
  actually placed, with position and flags. Porting v31 to v92 is same-format, same-lineage, low
  friction, and bounded per zone. Collapses the 3-source reconciliation into a 1-source port plus a
  targeted overlay, removing the exact failure modes above.
- Con: v31's baseline is the stripped/faster progression. Shipping it verbatim loses classic
  content. (Mitigated below: the high-value classic content is recoverable as an overlay.)

The important realization: **both options draw spawns from v31 and quest logic from v17.** They are
not different data pipelines. The real difference is the DEFAULT POSTURE and the STOPPING RULES.
Option A defaults to "reconcile and reconstruct everything" (unscalable). Option B defaults to "port
v31, overlay v17 where cheap, stop at video."

## Recommendation

**Pivot to a v31-primary structural baseline, reframe the north star per data-type, and adopt hard
stopping rules.** Concretely:

| Data type | Source of truth going forward |
|---|---|
| Spawn positions, territories, progression skeleton | **v31** (port to v92; the only viable source) |
| Conditional / traveling-spawn choreography | **None achievable**; flag as known divergence, do not chase |
| Quest existence + scope (what should be live) | **v17** (defines the classic set) |
| Quest logic re-enable, rewards, dialogs, strings | **v17** where cheaply recoverable from the client |
| Mobs, gathering, habitats | v31, spot-corrected against v17 |

Rationale, grounded in the data above:
1. v17 structurally cannot supply spawns; the spawn-fidelity ceiling is v31 + video no matter which
   posture we pick. Chasing classic spawn choreography is spending effort on an unreachable target.
2. v31 is the only complete, self-consistent server dataset and the only one that ports at scale.
3. The traveling-NPC mechanic is gone from every source (0 conditionalSpawn). Classic spawn
   choreography is off the table regardless; accept it as a divergence rather than reconstructing it
   zone-by-zone from video that mostly does not exist.
4. v31-primary removes the 3-source reconciliation that caused every audit miss this session, so it
   is not only faster, it is more correct.

### Stopping rules (the part that makes it scale)
- **No video-based spawn reconstruction** except a small, explicitly-curated, high-value shortlist
  per zone. Everything else takes v31's layout.
- **Re-enable a v17 quest only if its NPCs are already spawned** in v31/v92. If a re-enable needs an
  unbuilt camp, either relocate the quest to an existing spawned NPC or defer it. Do not build camps
  from video as a default.
- **Do not attempt conditional/traveling-spawn fidelity.** Place one static spawn at the NPC's
  primary post and record the divergence.
- **Log every divergence** so "restored" never silently means "approximated."

## IoD wind-down (do not waste the sunk cost)

IoD is nearly complete under the old approach and we already have its video. Finish it as scoped:
place the 4 confirmed Leander's Outpost NPCs (Eria, Jehan, Ayrdoss, Lorin) that we have positions
for, hold Priscus and Leander per TRACKER decision 25, and treat IoD as the last zone done under the
old doctrine. Adopt the v31-primary doctrine starting with the next zone.

## Effort implication (honest estimate)

- Under v17-primary: each zone needs a gameplay video, a full 3-source reconciliation, and manual
  spawn reconstruction. Multiple sessions per zone, and hard-blocked on any zone without video.
- Under v31-primary: each zone is a bounded v31-to-v92 port plus a targeted v17 quest/reward/dialog
  overlay. No video dependency, far fewer failure modes, predictable per-zone cost.

Given the project spans many continents, v31-primary is the only posture that finishes in a
reasonable timeframe while still recovering the highest-value classic content (the quest spine,
rewards, and dialogs) that v17 uniquely and cheaply provides.
