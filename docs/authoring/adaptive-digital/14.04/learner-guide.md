# 14.04 — Cybersecurity and account resilience

## Secure access has to survive an ordinary loss

Account resilience combines protection against unwanted access with a usable route for the owner when something fails. Strong authentication, device maintenance, encryption and backups solve different problems. A password change alone cannot demonstrate them all, and several recovery methods can still fail together if every one depends on the missing phone.

Allow 35 minutes for the complete fictional dependency exercise. Use paper or an accessible notes tool. No real login, security testing, password, recovery code, device wipe or account lockout is required. Optional real work uses only an account you control, current provider instructions and a retained working session. Managed accounts follow their administrator's rules.

## Match a control to the failure it addresses

A unique strong password reduces harm from reuse elsewhere; a suitable password manager can help maintain it. Multiple authentication factors reduce reliance on a password alone. [FTC guidance](https://consumer.ftc.gov/articles/use-two-factor-authentication-protect-your-accounts) explains additional factors and verification-code scams. A password plus a second memorized answer is still two pieces of knowledge, not two different factor categories. Do not disclose a code to an unsolicited caller or approve an unexpected prompt.

[NIST's authentication guidance](https://pages.nist.gov/800-63-4/sp800-63b.html) distinguishes phishing-resistant authentication from manually entered one-time codes. Where supported and accessible, an appropriate passkey/security-key route can reduce phishing exposure, but its recovery and device dependencies still need checking. A label such as “passkey” does not tell you where it is stored or how it can be restored.

Updates address software vulnerabilities; a screen lock limits casual access. Storage encryption protects data at rest under its actual configuration, but does not repair an already-compromised signed-in session or replace a backup. Losing the only decryption key can defeat recovery. Keep recovery material private and accessible through an appropriate independent route. Do not put the secret itself into a learning record.

## Worked example: two backups, one point of failure

A person stores both a recovery code and instructions in the email account those materials are supposed to recover. With the phone unavailable and no signed-in session, neither is reachable. Renaming one note “offline backup” changes nothing. A useful recovery plan records prerequisites and establishes an available route outside the failed dependency. A plan on paper is still not a tested sign-in.

## Complete case: Owen loses access to a phone

Owen owns the fictional Postbox account and a trusted laptop. No actual credentials appear here. The provider's **invented training rules** are complete for this case:

| Item | Stipulated requirement or state |
| --- | --- |
| Normal Postbox sign-in | Correct account password AND a phone-generated code |
| Alternative Postbox sign-in | Correct account password AND a valid unused paper recovery code |
| Account password | Stored in Owen's local vault; not assumed memorized |
| Local vault | Opens on the trusted laptop with a separate vault passphrase Owen knows; offline access has been verified |
| Existing recovery-code copy | Inside Postbox only; inaccessible before signing in |
| Proposed paper recovery copy | Can be generated/stored through official settings while signed in; initially not prepared |
| Device | Laptop screen lock and updates checked; storage encryption enabled; recovery-key location not yet verified |
| Backup | Harmless sample restored from separate storage; other data not tested |

For the loss scenario, the **phone and every existing Postbox session are unavailable**; the trusted laptop and vault passphrase remain available. A retained session can support safe setup beforehand, but is deliberately not a recovery prerequisite in the scenario. Real providers have different recovery rules, so these toy rules are not login instructions.

### Action 1 — Trace every prerequisite

Draw arrows or make a table: `desired resource | all required inputs | where each is held | available under loss? | evidence`. Trace phone code, account password, vault access and the current recovery-code copy. Determine whether any complete sign-in route exists before the proposed improvement. Count routes only when every required input is confirmed, not when a promising label exists.

Add separate rows for device encryption/key recovery, updates, backup coverage and safe-device use. Keep the unverified encryption-key location visible even if the Postbox route can be improved. These are different failure scenarios; one successful sign-in would not validate all of them.

### Action 2 — Plan a safe improvement, then inspect its evidence

Before simulating loss, use the official settings in a retained working session to prepare the provider-supported independent recovery material. The plan must retain current access, keep the material private, and verify the supported method without deliberately removing every fallback. Save your proposed sequence before opening [the later packet](later-packet.md). Do not invent a recovery code or type a real secret into your notes.

For a real service, inspect how verification works first. A successful test may consume a one-time recovery code, and generating a new set may invalidate old copies. Follow the provider's documented process and keep a currently valid unused route; never assume a consumed test code remains available. If the provider offers no safe non-destructive test, record that limitation and obtain official guidance.

### Action 3 — Re-run loss and compromise scenarios

Apply each later status literally. Report whether the route is **planned**, **material prepared**, **method tested**, or **available in the stated paper scenario**. Those statements are not interchangeable. Then consider an unexpected approval prompt and an unexplained active session: do not approve or share codes; reach the provider's incident guidance independently from a trusted device. Preserve needed evidence and follow its session/password/recovery instructions rather than clicking an unsolicited “support” link.

Complete [three fresh checks](check-prompts.md) before [the key](check-answers.md). The finished artifact is a dependency table, safe setup sequence, later-result audit and an unresolved-gap list. It contains statuses and locations described generically, never credentials.

## Supported, harder and later routes

Choose provider-supported methods compatible with your device, budget and access needs; no particular hardware purchase is required by this exercise. A trusted helper may explain controls without possessing secrets. If privacy from a coercive person is part of the threat, a visible paper card may be unsuitable; obtain appropriate support and use a safe route. Do not change another person's account.

Harder scenario: both phone and laptop are unavailable, and the local vault has no other verified copy. Does the paper Postbox code alone solve the missing-password problem? Show the dependency that remains. Next, consider an encrypted backup whose key is stored only on the lost device: a valid backup file is not sufficient.

For later real transfer, audit one account you own. Make one appropriate improvement through its official interface, retain working access, verify what can safely be verified, and record a review trigger such as a changed phone, obsolete recovery contact or unexplained session. Separate a real tested route from the scenario you only rehearsed. Unlike 14.02's file-maintenance exercise, this tests how controls and recovery behave under specific loss or compromise paths. It does not establish immunity to attack.

**Supportive:** A supported improvement reduces a named exposure and leaves a usable, independently reachable recovery route.

**Mixed:** Authentication improves, but a missing key or second-device dependency remains unresolved.

**Contradictory:** Codes are shared, unexpected prompts approved, or every fallback is removed to make a demonstration look decisive.

**Inconclusive:** Settings look stronger, but access/recovery prerequisites and actual test results are unknown.

See [scope](SCOPE-MAP.md) and [sources](../SOURCES.md).
