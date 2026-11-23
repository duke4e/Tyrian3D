# Working on Tyrian3D

- When a task is done and checked, commit it and push it without asking (the user's standing approval, 2026-11-05). Stage only the files the task changed.
- Each time a task is done, also build the game the user plays (`build/game`, RelWithDebInfo) so it has the change. Work and test in `build/dev`; never rebuild `build/game` while its `tyrian3d.exe` runs (check the running processes' paths first), and say so if it had to wait.
- Never commit the `external/btbh-renderer` submodule pointer (`git status` shows it as ` m`); leave it unstaged.
- Branches made by side sessions are merged only when the user says so, and never pushed.
- When simulating a playtest (the autopilot, or any scripted run that stands in for a player), move the ship by Fitts's law: the time to reach a target grows with log2(distance / target size + 1), so the simulated player aims and dodges at a human's speed instead of snapping to where it wants to be (the user, 2026-11-23).
