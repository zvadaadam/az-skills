# Landing order

Measure collisions before ordering anything. List each workspace's changed files (committed, uncommitted and new), then compare pairs:

```bash
files() { { git -C "$1" diff --name-only "origin/$2...HEAD"; git -C "$1" diff --name-only HEAD; git -C "$1" ls-files --others --exclude-standard; } | sort -u; }
files <checkout-a> <base> > a.files; files <checkout-b> <base> > b.files
comm -12 a.files b.files
```

Land the smallest, least-colliding change first, unless the user is waiting on one. The next change prepares on its frozen predecessor while it waits. Tell each lead what lands before it and what it will have to absorb.

A file git can't merge (binary, encrypted, generated whole) gets one editor for the whole batch, the last lane to land. The others send that lane a short note of what they need, because two branches editing such a file conflict wholesale.

A PR opens only when its change is finished, tested, tried in the product, reviewed by its lead and rebased. Until then the work stays local, because every push restarts CI and review. When a change's scope shrinks, update its test plan, its place in line and anything it has reserved in the same message, so it stops waiting for slots it no longer needs.

## The machine and the screen

Find out which jobs really compete for the machine (usually whole-tree test suites, builds and installs; rarely a single test) and allow one at a time: parallel heavy runs overload it, and their timeouts look like test failures. Follow the repo's lock if it has one, and never suspend a running job to make room.

The screen is shared too. No session brings a window to the front while the user works; steps that truly need the app in front wait until the user is away.
