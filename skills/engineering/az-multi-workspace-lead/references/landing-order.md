# Landing order

Measure collisions before ordering anything. List each workspace's changed files (committed, uncommitted and new), then compare pairs:

```bash
files() { { git -C "$1" diff --name-only "origin/$2...HEAD"; git -C "$1" diff --name-only HEAD; git -C "$1" ls-files --others --exclude-standard; } | sort -u; }
files <checkout-a> <base> > a.files; files <checkout-b> <base> > b.files
comm -12 a.files b.files
```

Check the blast radius even when the file lists are disjoint. Ask each coordinator which command, API, or data format its change alters or depends on. Trace the affected caller in the other candidate or on the base. For example, a CLI flag rename can break a script in another workspace without a merge conflict.

Choose an order that leaves the caller working after each landing. If neither change can go first, have the coordinators stage a compatible transition, such as accepting both flag names until the caller moves. Among independent changes, land the smallest, least-colliding one first unless the user is waiting on another. Give the next coordinator the frozen revision to prepare on and any affected caller to verify.

A file git can't merge (binary, encrypted, generated whole) gets one editor for the whole batch, the last lane to land. The others send that lane a short note of what they need, because two branches editing such a file conflict wholesale.

A PR opens only when its change is finished, tested, tried in the product, reviewed by its coordinator and rebased. Until then the work stays local, because every push restarts CI and review. When a change's scope shrinks, update its test plan, its place in line and anything it has reserved in the same message, so it stops waiting for slots it no longer needs.

## The machine and the screen

Find out which jobs really compete for the machine (usually whole-tree test suites, builds and installs; rarely a single test) and allow one at a time: parallel heavy runs overload it, and their timeouts look like test failures. Follow the repo's lock if it has one, and never suspend a running job to make room.

The screen is shared too. No session brings a window to the front while the user works; steps that truly need the app in front wait until the user is away.
