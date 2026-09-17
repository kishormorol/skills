---
name: blast-radius
description: Before any bulk or destructive operation on real data — archiving users, revoking access, deleting rows, sending a batch of emails — measure what it would actually touch and prove the query means what you think it means. Use when a request implies writing to many rows at once, or when a filter is about to decide something about real people.
license: Apache-2.0
---

# Blast radius

A bulk operation is a claim about the world: *everyone matching this query deserves this
outcome.* The query is usually right about the rows and wrong about the world.

This skill is the gap between those two. Work through it before the write, not after.

## 1. Name the signal, then attack it

Write down the sentence the query implies, then try to falsify it.

> "No Discord account means they stopped working here."

Now check: of 505 active members, exactly **one** had ever left the server — and they
were active that same day. Eighty had simply never joined, including the Research
Director. The signal measured *joining*, not *working*. The sentence was false and the
query was fine.

Signals fail in recognisable ways. Check yours against these:

| Failure | What it looks like | How to catch it |
|---|---|---|
| **Absence ≠ departure** | "Not in the system" conflates *never arrived* with *left* | Split the two. They need different actions. |
| **Auto-generated rows fake activity** | Draft records created by a cron look like work | Filter to rows a human caused — `status != 'draft'` |
| **A field changed meaning** | A column was write-once until a fix landed | Find the commit. Data before it answers a different question. |
| **Status lags reality** | A row says `pending` while the thing already happened | Check the artifact (a token, a document), not the label |
| **Timestamps record the last edit** | Everything is "stale" at the same age | A tight age cluster is one bulk edit, not independent decay |
| **Loose matching invents members** | Surname or prefix matching pulls in strangers | Match on identity, never on a name fragment |

## 2. Classify every row before touching any

Do not act on the count. Resolve each row to a thing you can name.

Ninety-eight permission grants once looked stale. Classified, they were **74** ids
matching no user at all (bots, unlinked staff, people long gone), **6** senior staff
holding deliberate oversight, and **18** genuinely stale. Revoking "the 98" would have
cut off the service account and the team leads.

Every row lands in exactly one bucket:

- **act** — you can say who it is and why it qualifies
- **exclude** — it qualifies but something outranks the rule (a live paper, a paid
  contract, an accepted offer, ownership of something in flight)
- **unknown** — you cannot resolve it. **Unknown is never "act".**

Then check the buckets for people the rule was never meant to catch. If the most senior
person in the org is in `act`, the rule is wrong — not them.

## 3. Ask what each row takes with it

A row is not only itself. Before removing a person, an account or a record, check what
points at it: work in flight, things they own, things owed to them, anything mid-flight
that would break. Exclusions found this way are the point of the exercise, not friction.

## 4. Make the write refuse to be wrong

Encode the guard in the script, not in your care at the time:

- **Dry run prints every affected row**, and the apply path is a separate flag.
- **Refuse the ambiguous** — the script errors on a row it cannot classify rather than
  skipping it silently.
- **Refuse the already-done** — re-sending often rotates a token and invalidates a link
  someone already holds. Check for the artifact before writing.
- **Narrow the rule** rather than hand-listing exceptions, so it stays true next time.
- **Write the record after the side effect**, never before: a failed send must not leave
  a row marked as sent.
- **Fail closed on environment** — if a link would point at localhost, refuse the batch.
  That guard is worth more than any amount of attention.

## 5. Verify the outcome, not the call

The function returning success means it was accepted, not that it worked. Re-read the
state afterwards and check the number you expected actually moved. Then say plainly what
changed, what you skipped, and why — the skips are the useful half of the report.

## When the answer is "this cannot be done safely"

Sometimes the honest output is that the data cannot support the decision. Say so, say
what evidence would support it, and stop. A bulk write on a signal you could not verify
is worse than no write, because it looks authoritative afterwards.
