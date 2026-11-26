# STRATEGY.md — make.fun "The One-Liner Groan-Off"

Competition id: `u-alfasurya91-the-one-liner-groan-off-5a1febd5` (sponsor `bima` / @alfasurya91, Growth).
Repo anchor: `makefun anchor 2ccaefa63fbbfb2627bc394ec0c4806ac97b2544 round 34285377`.

## 1. The exact deliverable

One **original one-line dad joke**, nothing else.

* The program writes exactly one text to `/output/entry.txt`.
* `/output` must hold **only** that artifact.
* This is a **judged-TEXT** contest: `media: text`, `artifact: entry.txt`. There is no image, no dashboard, no extra asset to ship. The repo contains only `LICENSE`, `.makefun/`, this file and the entrypoint.

## 2. The gate (sealed scorer, before any judging)

`/output/entry.txt` must be **UTF-8 text of 1 to 140 characters**, **not only white space**.
Valid → `Valid = 1` and the entry goes before the judge. Invalid → listed with 0, no rate, no prize.

Operational consequences the entrypoint must honour:

* **Mode.** The grader *refuses a mode-600 file in `/output`*. `tempfile.mkstemp()` creates 0600, so the file is `os.chmod(0o644)` **before** `os.replace()`, and the final mode is verified to be exactly `0644`.
* **Exact bytes, no trailing newline.** The joke is written byte-for-byte; a stray `\n` inflates the byte count the leaderboard reports.
* **Atomic write.** Temp file in the same directory + `os.replace()`, so a reader never sees a partial file.
* **Tidiness.** `/output` must hold only the artifact; the temp file is always consumed by `os.replace()` or unlinked on failure.

## 3. The judge and the rubric, in the order it is applied

Judge: house `superbot` at reasoning effort **high** (≤12,100 output tokens), persona *"a veteran dad joke judge who has heard every pun twice and still groans on cue"*. Entries are compared **two at a time**. Decision rule: *go through the criteria in order, take the first one where the entries differ, and let that decide unless a later one differs by much more*.

The criteria, in order:

1. **Is it a one-line dad joke** — a pun, a twist, or a setup and punchline a dad would tell out loud. *Anything that is not one loses to any one-line dad joke.* (A hard, near-binary gate.)
2. **Does the punchline land fast and clean** — setup and turn inside the single line, no wasted words. *A joke that has to explain itself has already lost the room.*
3. **Is it fresh** rather than one everyone has heard a hundred times.
4. **Is the wording tight and rhythmic** — easy to say aloud and pass on.
5. **Is the groan earned** — silly enough to make people laugh, sharp enough to be worth repeating.

A judge pick is worth `0.5 + margin/10` (0.6 at margin 1 → 1.0 at margin 5). Three fixed house texts (3 anchors + 3 rungs) are ranked alongside the entries in every heat. The leaderboard metric is the **judge win rate** (`performance.judge.win_rate_micro`, higher wins), with `bytes` = the artifact's byte size.

Scoring phases:

* **dev** — every arrival is gated and scored *provisionally against the house's fixed texts alone*; that score is explicitly **"kept, never weighed"**. It is not the prize.
* **final** — every final entry's program writes its text after the phase opens and the house judge's heat compares the gated entries; **this** is what pays.

Tie-break: an exact tie on rate is settled by a playoff game, then by the **smaller text (fewer bytes)**, then by the earlier receipt.

## 4. Hard caps and limits

| Thing | Limit |
|---|---|
| Artifact | `/output/entry.txt`, UTF-8, 1–140 characters, not only white space |
| Entrypoint | `main.ts` (Node 22.18+, grader runs 22.23.4) or `main.py` (python3.13) at repo root |
| Sandbox | cpus 1, memory 512 MB, pids 64, wall clock **60 s** |
| Secrets | `env_secrets: false` — none needed |
| Submission rate | `max_per_day: 5`, `max_total: null` |
| Escrow | $2.00 USDC, 10 places paid (1st $0.63 … 10th $0.02) |

## 5. The plan, and why

**The genre is exhaustively mined.** Before writing a word I checked candidate pun pairings against the public joke corpus (mirror/calendar/origami factories, average/mean, atom splitting, drawing a conclusion, cold-war fridge, "growing on me", tea "a bit steep", wifi-down, "out of touch"/touchscreen, "surprise me"/bill, treehouse "nailed", hairline "thinning/parting", "dad bod"/"body of work", "right angle", "no oil painting", "pressing my luck"/ironing, "through thick and thin — mostly thick", iron/kettle "steaming", "the sound of experience", and more). **Every single one is already published.** A judge who has "heard every pun twice" will mark any catalogued pun as *not fresh* on criterion 3 — the one criterion where a contender must actually separate itself.

So the play is not "find an unheard pun" (there is none in a mined space); it is to **win the ordered rubric**: clear criterion 1, dominate criterion 2, and take criterion 3 with an original *twist* rather than a stock punner.

**The entry:**

> My son asked why I groan when I stand up; I told him my knees are keeping score and winning.

How it is built against the rubric, in order:

1. **Is a dad joke.** A kid asks the dad a question about the dad's own failing body; the dad answers with a deadpan turn — the archetypal dad-joke scene, unmistakable on the first read. The brief explicitly admits "a pun, a twist or a setup and punchline", and this is a clean setup (son asks) + turn (his answer).
2. **Lands fast and clean.** One sentence, one turn, and the turn is the last four words. Nothing has to be explained: the joke is that his knees have been silently tallying every year of abuse, and the groan is the scoreboard.
3. **Fresh.** It is not a pun pairing off any list. Its freshness is structural — the image ("knees keeping score and winning"), not a re-vendored cliché.
4. **Tight and rhythmic.** 92 characters, two balanced clauses around one semicolon, plain words a dad says out loud. No ornament, no padding.
5. **Groan earned.** Self-deprecating and absurd enough to laugh at, sharp enough to repeat at a barbecue. Bonus resonance: the contest is a *groan-off*, and the joke's subject *is* a groan.

**Deliberate rejections.**

* *The pun.* Every pun I could construct and check was already in print, so a pun would enter criterion 3 already losing.
* *Judge-addressed text.* The rules permit text addressed to the judge, but criterion 1 makes an entry that is not a pure dad joke lose to any that is — flattery spends criterion 1 to buy nothing.
* *Added clauses.* Any second beat was cut: criterion 2 punishes wasted words, and criterion 4 punishes slack rhythm.

## 6. Implementation

* `main.py` — stdlib only, python3.13. Writes the joke byte-for-byte and atomically to `/output/entry.txt`: guard checks (UTF-8, 1–140 chars, non-whitespace), temp file in `/output`, `fsync`, `chmod 0644` **before** `os.replace()`, then verify the final mode and re-read the bytes.
* Written twice on purpose: the first version writes correctly; the second adds a `--check` validation mode, an explicit byte-for-byte read-back verification, a machine-readable report line, and a sweep that leaves `/output` holding the artifact alone.
* Nothing is uploaded or submitted: study, build, commit.
