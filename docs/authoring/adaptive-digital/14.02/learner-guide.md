# 14.02 — Digital competence and data hygiene

## Recover a known version, not a reassuring icon

Data hygiene connects ordinary organization with recoverable, usable services. You need to know which file is authoritative, where copies live, which accounts and devices they depend on, and how maintenance affects access. A “backup complete” message is useful information, but opening the recovered content is stronger evidence that the selected file can be restored.

Allow 30–40 minutes with a device and an ordinary file manager, or use the supplied paper comparison route. No account login, purchase, upload, deletion or command line is required. Work in a new folder you own. Do not use confidential documents, managed system directories or a real restore that overwrites current work.

## Five distinctions worth keeping

**Copying** creates another instance. **Synchronization** keeps selected locations aligned and can propagate an unwanted edit or deletion. **Version history** may retain earlier states, subject to a service's actual rules. A **backup** is a deliberately recoverable copy with understood location and retention. A **restore** retrieves a chosen state into a usable location. A second folder on one device is a useful copying rehearsal, but does not protect against losing that device.

The [NCSC backup guide](https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/always-back-up-your-most-important-data) explains separate storage and recovery options. Your own coverage must be checked: files, apps, account access and an entire device are different restoration targets. Protect copies according to their sensitivity. Encryption needs usable key recovery; an inaccessible encrypted copy is not a tested recovery.

Keep accounts identifiable without writing secret values into your learning notes. Record provider, purpose, ownership, recovery status and where the official instructions are found. Unique credentials and a suitable password manager can help; detailed authentication/recovery work is in 14.04. For device updates, use official settings and the organization's policy where applicable. [NCSC update guidance](https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/install-the-latest-software-and-app-updates) explains their security purpose. Save work and check access/backup needs before a change; an unfamiliar warning deserves investigation rather than dismissal.

## Worked example: the filename lies by omission

Two folders contain `meeting.txt`. One says “Room Cedar”; the other says “Room Birch.” Matching filenames do not establish the same version. Preserve the current source, identify the required content and copy the selected version into a new destination. Renaming the stale file “latest” does not make it current.

## Supplied materials: a harmless meeting note

The [materials folder](materials/README.md) contains two original synthetic files:

| File | Purpose | Exact lines |
| --- | --- | --- |
| meeting-v1.txt | Earlier version | Community meeting; Room Cedar; Bring one pencil |
| meeting-v2.txt | Required current version | Community meeting; Room Birch; Bring one pencil |

All source files use UTF-8, one line per item and a final newline. Content comparison in an ordinary editor can tolerate a platform's newline convention, but must preserve all three words/lines correctly. The exercise's byte-level test uses the supplied bytes.

### Action 1 — Set up a traceable working area

Create a new empty folder called `practice-recovery` in an authorized location. Inside it create `original`, `copy` and a **new empty** `restore-check` folder. If any already exists, choose a different new parent name; do not clear existing contents. Copy both supplied files into `original`, preserving the downloadable source files. Open v2 and confirm the three lines before proceeding.

Record where the working area resides, whether all three folders share a device, and what loss that arrangement cannot withstand. Add one device-maintenance row and one account/privacy row from the fictional inventory below; no real credentials are needed.

| Item | Supplied status | Useful next check |
| --- | --- | --- |
| Personal laptop | Official update offered; restart not yet performed | Save work, confirm sample copy and follow official update guidance at a suitable time |
| Photo service | Owner account; recovery status unknown | Inspect official account settings later; do not label access recoverable yet |
| Shared folder | Another collaborator has access | Do not place personal documents there merely because upload works |
| Unrecognized warning | “Destination is full” during copy | Check destination capacity and copy result; do not delete unrelated files to finish |

### Action 2 — Perform a non-destructive copy and retrieval

Copy `original/meeting-v2.txt` into `copy`. Then copy it **from `copy`** into `restore-check`; do not use the original as the retrieval source. Open the retrieved file and compare each line with the known v2 reference. Record the source, destination, version, opened result and whether any original was changed. This tests the actual copy route if you perform it. It does not test cloud recovery, device-loss recovery or protection of every real file.

If saving/opening fails, retain the non-sensitive error and stop claiming success. For a wrong version, create another new destination and retrieve the correct version; preserve the failed output as evidence. Do not repair the copy by manually retyping it and then call that a successful restore.

### Action 3 — Diagnose changed results and choose maintenance

Save your receipt before [the later records](later-packet.md). Assess each independent branch against the required v2 content. Draft a small maintenance plan covering the important data category, backup location/retention, one future restore check, official update review, account recovery and unnecessary sharing. Include a trigger such as device replacement, changed recovery contact or failed backup; do not claim a plan has already run.

Use [fresh checks](check-prompts.md) before [the key](check-answers.md). Complete output is the retrieved harmless file or explicitly labeled paper comparison, receipt, branch decisions and maintenance plan. A paper route practices reasoning and leaves actual file operations untested.

## Supported and harder routes

Use an accessible file manager, voice input or a trusted helper describing controls without taking passwords. An audio document is possible for later transfer, but the supplied text case keeps the exact comparison self-contained. On managed equipment, use its approved training area or the paper route.

Harder route: with an already-authorized separate backup destination, repeat the same harmless-file retrieval while preserving originals. Identify what happens if the original device or the same cloud account becomes unavailable. Record whether the alternative was actually tested or only reasoned through. Do not disconnect your only working recovery route to demonstrate a failure.

For later real transfer, select one important category, review destination privacy and retention, and test one harmless representative file before moving sensitive material. Troubleshoot through observation, a single reversible change and a retest; stop for suspected compromise or unexplained loss and use official support. This is operational organization and recoverability; 14.04 separately examines attackers and authentication failure paths.

**Supportive:** The selected version is retrieved from the intended source, opened and compared with originals preserved.

**Mixed:** Retrieval works but returns an older version; the procedure is corrected and retested.

**Contradictory:** Real originals are deleted or private data uploaded to an unverified destination for the exercise.

**Inconclusive:** A success icon or copy count is recorded without inspecting the recovered content.

See [scope](SCOPE-MAP.md) and [sources](../SOURCES.md).
