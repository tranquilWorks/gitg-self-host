# 15.09 — Cybersecurity, fraud, and identity protection

## Triage a suspected compromise without confusing recovery stages

Start with the fictional account packet below. In about thirty minutes you will build a short incident record that separates warning signals, verified facts, containment actions and unresolved recovery. No credentials, real transactions or suspicious links are needed. The optional live step uses only an account you own or are authorized to manage; an actual incident requires prompt provider or organizational response rather than waiting to finish practice.

## An alert is a lead, not the whole incident

Phishing and social engineering try to make a requested action feel necessary: follow a link, reveal a code, approve access or move money. A convincing alert can be forged; a genuine alert can also reveal a genuine problem. Open the provider through an independently known app or address and check there. Do not use the suspicious message's phone number to verify the same message.

Email often supports password recovery for other accounts, so an attacker with email access may affect more than the inbox. A changed password may not address every active session, recovery setting or forwarding rule. Follow the provider's own recovery process, verify contact methods and inspect security settings; if unauthorized messages were sent, warn affected contacts through an appropriate trusted route without spreading the malicious link or private incident details. Organizational accounts belong with the authorized IT/security route. The FTC's recovery guide describes these account checks. See S09 in [SOURCES](../SOURCES.md). Do not improvise destructive resets or investigate systems beyond your authority.

Separate prevention, containment and recovery. A strong unique password or supported passkey, appropriate multifactor authentication, protected recovery options and supported software updates can reduce exposure. NCSC guidance supports strong separate credentials, appropriate second factors and supported passkeys (S21). No single setting makes an account invulnerable. Keep a viable recovery path while making changes; record the type of change, never the secret. A recovery code shared with a caller is exposed information even if the caller uses your name correctly. A security setting changed successfully is a narrower result than proving nobody retained access.

Financial fraud and identity misuse need additional routes. A posted unauthorized payment needs prompt contact with the relevant institution through an independently verified channel, even if the email account is now secure. A dispute receipt is not a refund. Suspected misuse of identity details may require a local identity-theft recovery process. FTC guidance illustrates U.S. reporting and recovery routes, including IdentityTheft.gov; other jurisdictions differ. See S10–S11. Do not promise reversal, deadlines or legal remedies from this exercise.

## Worked example

Alex changes an email password, then writes “incident resolved.” Their case still lists an unfamiliar recovery address and an unauthorized payment. Alex revises the status: password change complete; recovery address requires provider-guided checking; bank dispute requested; reimbursement unknown. This does not mean the password change was useless. It prevents a successful action from hiding unresolved parts of the incident.

## Original fictional account packet

You own the invented personal account “Cedar Mail.” Your usual device is available and believed trustworthy; no malware finding is supplied. There are no real URLs or passwords to use.

| Signal | Information available before verification |
| --- | --- |
| M1 | Email says “new device login; click here to undo”; message authenticity unknown |
| M2 | Independently opened bank app shows a posted 46-unit payment you do not recognize |
| M3 | Caller claiming to be support asks for a one-time recovery code; you have not shared it |
| M4 | A copy of an identity document was previously sent to an unverified rental contact; later use is unknown |
| M5 | A work account sends a separate alert; employer policy requires contacting IT, not changing its configuration yourself |

The fictional Cedar Mail help card, independently obtained for this exercise, says: use its official recovery route if unable to sign in; once access is verified, follow its instructions for password, sessions, recovery contacts and forwarding rules; check for unauthorized messages and protect recovery access. It supplies no guarantee about device cleanliness or other services. Your incident log has four columns: observation/source, scoped action/owner, result actually confirmed, unresolved next check.

## Work the incident in stages

1. For M1, identify the independent verification route. For M2–M5, assign the appropriate owner or institution and a concrete next action. Do not wait for M1 to become certain before reporting the posted payment or work alert.
2. Distinguish code requested from code disclosed. Decline M3's request and use the independent provider route if account help is needed. Do not classify the account as compromised solely because a caller asked; do not call the request harmless either.
3. Build a sequence for the personal email account using the supplied help card. Explain why working recovery access matters and which settings need checking after a password change. If the device is suspected compromised in a real incident, seek the provider/IT's appropriate trusted-device guidance; the packet does not establish a malware diagnosis.
4. Write the minimal information each recipient needs. Bank support needs the disputed transaction through its secure process; IT needs the work alert through its incident route. A public post does not need your identity document, recovery code or account number. Save only fictional labels in this exercise.
5. Choose one prevention improvement. In the fictional route, describe adding a supported second factor while preserving working recovery access. In an optional owned-account route, independently open official help and make one low-risk supported change only if you understand its recovery implications. Do not force a lockout, remove the sole recovery method or upload secrets as proof.
6. Preserve the first incident log, then open the [later packet](later-packet.md). Update each row separately. Write a closeout statement naming what is contained, what remains unresolved and who owns the next step.

## Evidence and follow-through

The default output is a five-signal triage log and a recovery sequence. A live setting change counts only if actually performed and confirmed; a hypothetical change remains a plan. Reported compromise, regained sign-in, removed forwarding, revoked sessions, investigated payment and restored funds are separate statuses. An unavailable provider response is unknown, not automatic resolution or automatic proof of continuing attack.

For a smaller task, do M1–M3 first, then add identity and work boundaries. Use text or dictation, hiding no recovery limitations. A trusted helper can navigate accessibility barriers without being given your password or codes. If coercive monitoring or abuse is relevant, account changes can alert another person; use an appropriate specialist safety route rather than applying this generic practice blindly.

For a harder paper case, make the usual device unavailable and remove the only recovery method. The sound answer is official recovery assistance with uncertainty, not inventing a bypass. For real transfer, maintain an accessible private list of independent provider and institution routes and review one owned account's supported security and recovery settings. Finish the [fresh checks](check-prompts.md) before the [key](check-answers.md).
