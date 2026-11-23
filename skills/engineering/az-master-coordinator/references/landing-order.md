# Landing order

Measure collisions before ordering anything. List each workspace's changed files (committed, uncommitted and new), then compare pairs:

```bash
files() { { git -C "$1" diff --name-only "origin/$2...HEAD"; git -C "$1" diff --name-only HEAD; git -C "$1" ls-files --others --exclude-standard; } | sort -u; }
files <checkout-a> <base> > a.files; files <checkout-b> <base> > b.files
comm -12 a.files b.files
```

For a pair that shares files, test the real merge instead of reasoning about it: `git merge-tree --write-tree --name-only <head-a> <head-b>` exits 1 and names the conflicting files when the two conflict, and exits 0 when they merge cleanly.

Land the smallest, least-colliding change first, unless the user is waiting on one. The next change prepares and gates on its predecessor's pushed head while it waits. Once the predecessor merges, it rebases: if the rebased tree is identical to the one it gated (`git diff <gated> <rebased>` prints nothing), its proof still holds, so it pushes without a second gate. Tell each lead what lands before it and what it will have to absorb.

A file git can't merge (binary, encrypted, generated whole) gets one editor for the whole batch, the last lane to land. The others send that lane a short note of what they need, because two branches editing such a file conflict wholesale.

A PR opens only when its change is finished, tested, tried in the product, reviewed by its lead, rebased, and passing locally every command its CI runs. Until then the work stays local, because every push restarts CI and review. When a change's scope shrinks, update its test plan, its place in line and anything it has reserved in the same message, so it stops waiting for slots it no longer needs.

## The machine and the screen

Find out which jobs really compete for the machine (usually whole-tree test suites, builds and installs; rarely a single test) and allow one at a time: parallel heavy runs overload it, and their timeouts look like test failures. Follow the repo's lock if it has one, and never suspend a running job to make room.

The screen is shared too. No session brings a window to the front while the user works. Steps that truly need the app in front run early in a lane, when the user is away; after 30 minutes of waiting, the lead asks you, and you ask the user for a few minutes at the screen. A user who is waiting for the result never goes idle.
