# 14.12 — Automation dependence and operational resilience

## Preserve the useful activity when a service is unavailable

Operational resilience starts with the activity you need to perform. “Have a backup” is too vague if the file cannot be opened, is stale, or omits the one contact route you need. An export preserves some data; a fallback makes a minimum activity possible under a specified failure. Recovery then restores normal operation without duplicating actions or silently losing changes.

Allow 40 minutes with the harmless local materials supplied here. Use an accessible editor or paper. The meeting, contact desk and request IDs are fictional; never send them to a service. Do not disable a real account, device, network, medical system or utility. The exercise makes a dependency unavailable only by putting its information aside.

## Trace prerequisites, then remove one on paper

A cloud calendar may require device, power, network, account and authentication. An AI summarizer can add another dependency even when the underlying information is available. A connected lock may depend on a different combination. If every fallback still requires the failed item, the apparent redundancy is circular.

[NCSC's backup guidance](https://www.ncsc.gov.uk/collection/small-organisations-guide-to-cyber-security/backing-up-your-data) supports making and checking appropriate backups. A copy is not a demonstrated recovery until you can retrieve and use it. This exercise adds an original meeting-continuity task; it is not a complete disaster-recovery design or a test of NCSC recommendations.

Worked example: a calendar export contains “see online map for room and contact.” It opens offline but cannot answer where to go or whom to contact. The format worked; the minimum service failed. Add authorized location text and an independent contact route, then test those specific questions again.

## Complete materials and failure assumptions

The packet contains [event-v1.txt](materials/event-v1.txt), [event-v2.txt](materials/event-v2.txt), [outbox.txt](materials/outbox.txt) and [server-receipts.txt](materials/server-receipts.txt). All are plain UTF-8 text; [the material index](materials/README.md) describes their roles. Do not read server-receipts until Action 3.

The minimum service is to answer the meeting's date/time, exact room, entry directions and an independent way to reach the organizer. The cloud calendar and AI assistant are unavailable in the scenario. Your paper/local copy and ordinary ability to ask the staffed desk in person remain available. No telephone, email delivery or online map is assumed. This is why an in-person contact route is supplied rather than a fake working phone number.

Version 1: revision September 18 at 09:00; event September 24 at 14:00 local time; room Willow; east entrance, then staffed reception; ask reception for meeting coordinator; reception staffed 13:30–14:30. Version 2: revision September 23 at 16:00; the same event and contact arrangement, **room Birch**, with directions “east entrance, ask reception for the level route to Birch.” Version 2 supersedes version 1. No attendee list is needed.

### Action 1 — Define what must survive

Draw the normal dependency chain and write the failure assumption. Name the four minimum answers and the freshness requirement: the latest confirmed event revision, checked again if an update arrives. Decide where a real minimal copy could be kept privately and accessibly. A locked file whose only key is in the unavailable account is not an independent fallback.

Read version 2, then create your own paper or local fallback card. If copying files, use a separate practice folder and a new filename; do not overwrite source materials. Record revision and event date separately. A creation timestamp on your copy cannot prove its contents are current.

### Action 2 — Actually retrieve and use the fallback

Put the normal source page and any AI tool aside. Open your local card or retrieve your paper copy. Answer the four minimum questions using only it. Then compare your recorded answers against version 2. Mark **retrieved**, **correct**, **missing** or **unknown** for each requirement. Do not silently repair the answers while claiming the first attempt succeeded.

If you discover a stale room or online-only contact, correct the card and repeat the same retrieval constraint. Record first attempt and retest separately. A paper exercise can genuinely demonstrate that you made and used a card, while a fictional outage remains a fictional outage. Neither proves the real reception desk or a real network worked.

### Action 3 — Reconcile before resuming automation

Read outbox.txt: two fictional requests, R-41 and R-42, are pending locally after an interrupted sync. “Pending locally” does not prove the server failed to accept them. Open server-receipts.txt and [the later packet](later-packet.md). Match exact IDs before deciding which requests need further action. The toy service treats repeated identical IDs as the same request; creating a new ID creates a new request. These are stipulated exercise rules, not a guarantee about real services.

Write a reconciliation table: `request ID | local status | server evidence | next action | uncertainty`. An acknowledgment of R-41 says nothing about R-42. If server status is unknown, check it or hold rather than blindly resending with a new identity. Do not send any actual request.

Finish with refresh, recovery and retirement triggers: a changed event requires an updated copy; service return requires status comparison; an expired real event copy should be removed or retained only for an appropriate purpose. Avoid spreading unnecessary personal information across “backup” locations.

Complete [fresh checks](check-prompts.md), then [the key](check-answers.md). Retain the dependency map, actual card/retrieval results and simulated reconciliation decisions.

## Different capacities and harder failures

A large-print card, audio note available offline or chosen helper can supply access. Verify that the format itself works without the original service. If the helper is the single point of failure, plan a consented alternative. For care, finance or safety-critical equipment, use the responsible provider's approved continuity arrangements; test only a harmless representation here.

Harder route: the device holding your local file is also unavailable. The local-file fallback then fails, while a separately held paper card might survive that particular loss. Do not claim every failure is solved by adding more copies; consider privacy, freshness and actual reachability.

For transfer, choose one authorized ordinary dependency and test a minimal fallback without disrupting service. An AI-dependent writing task can be rehearsed manually from a short source; a cloud route can be rehearsed with a current offline record. Specify exactly which task and failure you covered.

**Supportive:** The minimum task succeeds from a current independent fallback and reconciliation avoids duplication. **Mixed:** Retrieval works but the contact or freshness requirement fails. **Contradictory:** Real safety systems are disabled or pending actions are blindly duplicated. **Inconclusive:** An export is saved but never opened or used.

See [scope](SCOPE-MAP.md) and [sources](../SOURCES.md).
