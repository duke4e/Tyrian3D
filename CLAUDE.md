# Working on Tyrian3D

- When a task is done and checked, commit it and push it without asking (the user's standing approval, 2026-11-05). Stage only the files the task changed.
- Each time a task is done, also build the game the user plays (`build/game`, RelWithDebInfo) so it has the change. Work and test in `build/dev`; never rebuild `build/game` while its `tyrian3d.exe` runs (check the running processes' paths first), and say so if it had to wait.
- Never commit the `external/btbh-renderer` submodule pointer (`git status` shows it as ` m`); leave it unstaged.
- Branches made by side sessions are merged only when the user says so, and never pushed.
