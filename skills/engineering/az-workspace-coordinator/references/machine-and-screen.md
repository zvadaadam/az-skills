# The machine and the screen

Find out which jobs really compete for the machine (usually whole-tree test suites, builds and installs; rarely a single test) and run one at a time, following the repo's lock if it has one. While yours runs, keep the other builders on edits. Check the load before starting the next job and never suspend a running one: a suspended test outlives its timeout and reads as a failure. Rerun any test partition that straddled a sleep.

The screen is shared the same way: no session brings a window to the front while the user works. A session that writes its own test harness defaults to a visible window, so every brief that runs the product says how to launch it: browsers headless, desktop apps in the background (`open -g` on macOS).

Steps that must come to the front, like opening an app link or dragging from Finder, go to the checker as one batch. It runs them itself once the user has been idle for 5 minutes, or on another machine or VM. This prints the idle seconds on macOS:

```bash
ioreg -c IOHIDSystem | awk '/HIDIdleTime/ {print int($NF/1000000000); exit}'
```
