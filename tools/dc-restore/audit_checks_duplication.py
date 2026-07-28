"""The duplication check: an item reachable from more than one source."""

from __future__ import annotations

from auditlib import Corpus, Finding, Scope, check, item_label
from dclib import SOURCE_KINDS


@check("duplication", "reward-integrity",
       "An item granted by more than one source. High only on the two signatures "
       "that marked a real defect every time: identical item plus identical exp "
       "and gold across two quests, and an item both quest-granted and purchasable.")
def check_duplication(corpus: Corpus, scope: Scope) -> list[Finding]:
    """Deliberate duplication is legitimate, so severity is confidence.

    The 1304/1323 defect was two quests granting the identical 12-row weapon bag
    at the identical 800 exp and 80 gold: a copy-paste, not a design choice. The
    1315 defect was a quest granting the whole Kugai token shop for free, which
    is only visible with shops in evidence scope. Everything else is reported at
    info with the full source list, because the alternative is a tool that cries
    wolf on every intentionally shared reward.
    """
    findings: list[Finding] = []
    subject_quests = scope.subject_quests(corpus)

    # Signature (a): the same item at the same exp and gold in two quests.
    by_signature: dict[tuple, list[int]] = {}
    for gid in subject_quests:
        payload = corpus.rewards.get(gid)
        if not payload:
            continue
        for template, _qty, _cls in payload["items"]:
            if not template.isdigit():
                continue
            sig = (int(template), payload.get("exp", ""), payload.get("gold", ""))
            by_signature.setdefault(sig, []).append(gid)

    for (item_id, exp, gold), quests in sorted(by_signature.items()):
        quests = sorted(set(quests))
        if len(quests) < 2:
            continue
        findings.append(Finding(
            severity="high",
            check="duplication",
            subject=item_label(corpus, item_id),
            detail="+".join(str(q) for q in quests),
            message=(f"granted by quests {', '.join(str(q) for q in quests)} at "
                     f"identical exp {exp or '0'} and gold {gold or '0'}"),
            evidence={"quest": quests[0], "quests": quests, "item": item_id,
                      "exp": exp, "gold": gold},
        ))

    # Signature (b): quest-granted AND purchasable.
    granted: dict[int, list[int]] = {}
    for gid in subject_quests:
        payload = corpus.rewards.get(gid)
        if not payload:
            continue
        for template, _qty, _cls in payload["items"]:
            if template.isdigit():
                granted.setdefault(int(template), []).append(gid)

    sources = corpus.item_sources
    for item_id, quest_ids in sorted(granted.items()):
        families = sources.get(item_id, set()) - {"QuestCompensation"}
        purchasable = sorted(f for f in families if SOURCE_KINDS.get(f) == "purchase")
        quest_ids = sorted(set(quest_ids))
        if purchasable:
            findings.append(Finding(
                severity="high",
                check="duplication",
                subject=item_label(corpus, item_id),
                detail="+".join(str(q) for q in quest_ids) + ":" + "+".join(purchasable),
                message=(f"granted by quest {', '.join(str(q) for q in quest_ids)} and also "
                         f"purchasable via {', '.join(purchasable)}"),
                evidence={"quest": quest_ids[0], "quests": quest_ids, "item": item_id,
                          "purchasable_from": purchasable},
            ))
        elif families:
            findings.append(Finding(
                severity="info",
                check="duplication",
                subject=item_label(corpus, item_id),
                detail="+".join(str(q) for q in quest_ids),
                message=(f"granted by quest {', '.join(str(q) for q in quest_ids)} and also "
                         f"available from {', '.join(sorted(families))}"),
                evidence={"quest": quest_ids[0], "quests": quest_ids, "item": item_id,
                          "sources": sorted(families)},
            ))

    return findings
