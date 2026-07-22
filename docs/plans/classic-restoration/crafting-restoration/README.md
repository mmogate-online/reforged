# Crafting Restoration Workstream (scoping stub)

Opened 2026-07-21 (user decision). A GLOBAL classic-restoration workstream, separate from any single
zone: import/reconcile the v31 crafting system onto v92 and restore deprecated craftable content to
usable. Surfaced while validating the IoD Berlon crafting-intro chain
(`../iod/data/padding-level2-berlon-proposal.md`).

Not IoD-scoped: recipes (`ItemProduceRecipe`) and item strings are single/regional entities, not
zone-partitioned. Follows the v31-primary DOCTRINE (`../DOCTRINE.md`): v31 is the source of truth,
every v92-only divergence gets an explicit PORT / KEEP / REMOVE disposition, and each divergence is
logged.

## Two axes (from the seed investigation)

### Axis A - deprecated-item usability ("no longer usable" -> usable)
Seed finding on 5 consumables (6000/6001/6016/6017/6197): the ONLY item-level difference from v31 is
the **ItemString tooltip** ("This item is no longer usable."). Every mechanical attribute
(`linkSkillId`, `combatItemType`, cooldowns, `requiredLevel`) is already byte-identical to v31.
- Restore = revert the tooltip to v31 functional text.
- CAVEAT: the real mechanical gate may live in the linked SkillData sheet (NOT exposed by the MCP
  servers). A tooltip-only restore may make an item READ usable but not FUNCTION. Every restored
  item needs an in-game function check or a skill-sheet inspection; restoring the linked skill/effect
  may be part of the fix.
- Open sub-question: how large is the deprecated-consumable set on v92? (These 5 were found via the
  Berlon chain; a full sweep of `ItemString` for the "no longer usable" tooltip is needed to size it.)

### Axis B - recipe import / reconciliation
Seed finding on the same items: recipes are ALREADY faithful to v31 on v92 (materials byte-identical).
The only recipe divergence found was v92 being MORE permissive - it flipped several recipes
`obtainable=false -> true` that v31 deliberately disabled (e.g. the processed and Major-tier potion
recipes 26758/26759/26774/26775/26859). So for these items there is nothing to "import"; if anything
v31 fidelity would DISABLE recipes v92 enabled - likely not the intent (the project wants more
craftable content, not less).
- The real Axis-B question is what v92 is MISSING or WRONGLY ALTERED vs the full v31 recipe set, which
  requires a full `ItemProduceRecipe` v31-vs-v92 diff (1552 recipes on v31), not just spot checks.
- Known non-material drift to adjudicate globally: `needSkillId` 6 -> 26 (skill remap),
  `needGrade` absent -> 0, `produceCriticalRate` retuned, `exp` recomputed. Decide KEEP (v92 schema)
  vs REVERT per attribute.

## Next steps (not started)

1. Full `ItemString` sweep for the "no longer usable" tooltip -> size the deprecated-item set (Axis A).
2. Full `ItemProduceRecipe` v31-vs-v92 diff -> classify every recipe PORT / KEEP / REMOVE (Axis B).
3. Resolve the linked-skill verification approach (in-game vs skill-sheet inspection outside MCP).
4. Patch placement: likely its own patch-001 spec range or a dedicated patch; decide with the user.
5. Economy-price reversion (buy/sell) is a separate call, not part of usability restore.

## Immediate slice already committed to (via the Berlon chain)

Restore 6000/6001/6016/6017/6197 to usable (tooltip + function verify) as part of the IoD Level 2
work. Everything else above is deferred until this workstream is scheduled.
