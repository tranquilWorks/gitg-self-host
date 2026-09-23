# 14.08 — Synthetic media, deepfakes, and provenance

## Decide what the media can establish

Audio, images, video and documents can be generated, edited or placed in a misleading context. An authentic recording can carry a false claim; a synthetic illustration can accurately explain something. The useful task is to separate the asset's history from the truth of the proposition you might act on.

Allow 30 minutes for a written event case. You will inspect supplied transcripts and metadata descriptions, not actual suspicious files. No voice cloning, identity recognition, detector upload or public forwarding is required. Use paper or an accessible editor. Your output is a claim-by-claim decision record and a neutral update for someone affected.

## Four questions that should stay separate

**Origin:** Where did this copy come from, and is an earlier/full version available? **History:** What transformations are documented? **Integrity:** What does a validated signature actually bind? **Truth:** Which independent record supports the consequential claim? These questions can have different answers.

[C2PA's explainer](https://spec.c2pa.org/specifications/specifications/2.4/explainer/Explainer.html) describes Content Credentials as provenance information associated with an asset. Validation can support statements about the recorded history and signer under the tool's trust model. It cannot, by itself, establish factual truth. Provenance may be incomplete or removed, so absent credentials do not prove fabrication. A badge screenshot is also not a validation result for the file in front of you.

Do not rely on an impression that the mouth looks wrong or a voice sounds familiar. Compression, editing and ordinary recording conditions can change appearance; convincing alterations need not contain obvious glitches. A detector score is an additional fallible signal, not a verdict or a calibrated probability for every file.

Worked example: a signed photograph documents that a particular editor exported a file on Wednesday. A caption says it shows a flood yesterday. The export record does not establish when the scene occurred, where it was recorded, or whether the caption is accurate. Check those claims through event-specific records before issuing an alarm.

## Complete fictional event packet

It is 10:00 on June 11. All dates and times in this case are local to Cedar Town. You are deciding where to attend the community repair event on June 12 and whether payment is required.

| Asset / record | Supplied facts |
| --- | --- |
| A — forwarded audio transcript | “Tomorrow's repair event has moved to North Hall. Send a 15-unit entry fee using the link attached.” The forwarding account says the voice is the organizer. Original recording date, full context and creator are unknown. |
| B — image | A poster says “North Hall — entry 15.” It has a familiar club logo. The crop omits the date, event title and source. |
| C — document | A PDF says “Repair event, June 12, 10:00, North Hall, fee 15.” A screenshot of a green badge accompanies it. No validation of this PDF is supplied. |
| D — short video | A person introduces an event at North Hall. A supplied validator report says a trusted-listed editing tool signed this exact video file on June 10 and recorded an export/crop. No claim about the event date, speaker identity or truth of spoken claims was validated. |
| E — established event page | Directly opened from a pre-existing saved address: update June 9, repair event June 12 at 10:00, South Hall, free. It may have become stale. |
| F — known organizer route | A contact method held before the forwarded media; no reply yet. |

The logo, familiar voice and multiple formats make the material feel coherent, but the packet supplies no evidence that A–D were produced independently. The official page is stronger evidence of the published arrangement, while its update date leaves room for a later change.

### Action 1 — Split asset claims from event claims

Create one row for each asset: `known supplier | known history | missing context | claim made | corroboration needed`. List venue, date/time and fee separately. For D, write the narrow proposition supported by the validator report. For C, identify why the badge screenshot is insufficient. Avoid converting “not validated” into “fake.”

Write an initial action: do not pay through the forwarded route or change the venue solely because of these assets; seek a current verified update. You can suspend a consequential action without declaring all media false or accusing the organizer.

### Action 2 — Ask the independent questions

Draft a message through F: “For the June 12 repair event at 10:00, what venue and entry cost are currently confirmed? Has an update superseded the June 9 page?” Name how F was established before the forwarded material. Do not use A's embedded payment/contact link as your verification route.

Save your initial record and request before opening [the later packet](later-packet.md). Compare each later response only with the claims it addresses. A fee answer does not settle venue; a venue correction does not identify the media's creator. If two apparently authoritative records conflict, seek explicit reconciliation and retain the conflict rather than selecting whichever looks newer without context.

### Action 3 — Communicate a decision without overclaiming

Write an update of no more than 60 words for an attendee who already saw the claim. Include event date, current supported venue/cost, the known source and what remains unresolved about the media. Avoid reposting the clip or inventing an accusation. If the event itself remains uncertain, say what still needs confirmation and avoid making a consequential payment on that basis.

Attempt [fresh checks](check-prompts.md), then read [the key](check-answers.md). The completed artifact is a provenance/claim table, independent request and calibrated attendee update. A paper interpretation of a supplied validator report is not an actual cryptographic validation you performed.

## Adapt and apply

The text route works without hearing or vision; no learner must identify a person by voice or face. For private, threatening or intimate media, use appropriate platform and specialist support, avoid unknown detector services, and preserve only necessary lawful report evidence. Do not redistribute sensitive media to crowdsource a verdict.

Harder route: the organizer confirms North Hall but denies the fee. Revise venue and cost independently. You still do not know whether a file is synthetic, selectively edited, mistaken or copied from another event. Decisions about attending and paying may become possible before forensic questions are settled.

For real transfer, choose a harmless public announcement. Trace its original publisher and event date, inspect any available provenance within its stated limits, and corroborate the actionable claim through a known route. Record inaccessible information as inaccessible. No-match reverse searches and absent credentials remain missing evidence, not proof of fabrication.

**Supportive:** Consequential claims are corroborated independently and provenance limits remain visible. **Mixed:** The fee is resolved but venue or origin remains unknown. **Contradictory:** Appearance, a badge or a detector score becomes a truth guarantee. **Inconclusive:** The clip is circulated for opinions without an independent event check.

See [scope](SCOPE-MAP.md) and [sources](../SOURCES.md).
