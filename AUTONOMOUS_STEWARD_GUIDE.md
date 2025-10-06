# Autonomous VS Code Project Steward Guide

## Overview

The Autonomous VS Code Project Steward is a self-operating software engineer that continuously improves the repository with minimal user interaction. It follows a **DISCOVER → PLAN → EXECUTE → REPEAT** loop to deliver documented improvements to build, test, quality, documentation, and developer experience.

## Features

### 🛡️ Built-in Safety Rules

The steward automatically pauses and logs (but does not execute) operations that trigger any of these safety rules:

1. **Destructive operations**: `rm -rf`, `sudo`, database drops, registry edits
2. **Secrets handling**: Writing tokens/keys to files, handling credentials
3. **Irreversible external effects**: Publishing, deploying, emailing, production changes
4. **Resource abuse**: Jobs exceeding 30 minutes, heavy downloads, huge disk writes

When a safety rule triggers, the steward skips that task and moves to the next safe task.

### 🔄 Operating Loop

#### A) DISCOVER
- Parses README, package files, lockfiles, configs
- Scans for TODO/FIXME/NOTE tags
- Runs fast checks: formatter, linter, type-check, tests
- Logs findings in PROGRESS.md

#### B) PLAN
- Creates a task queue with 3-7 prioritized items
- Prioritizes by: **Impact ↑, Effort ↓, Risk ↓, Time ↓**
- Prefers small, independent, high-impact tasks (<60 min)

#### C) EXECUTE
For each task:
1. Creates a short-lived branch: `steward/<category>-<timestamp>`
2. Implements minimal, correct changes
3. Adds/adjusts tests to protect behavior
4. Runs: format → lint → type-check → test → build
5. Updates docs as needed
6. Commits with Conventional Commits format
7. Appends entry to PROGRESS.md
8. Merges locally (fast-forward)

#### D) REPEAT
- Picks next task immediately
- Never idles - always has something to do
- Cycles every 5 minutes when queue is empty

### 📋 Default Backlog

When no issues are found, the steward works on:

- **Code Quality**: Formatter/linter standardization and auto-fix
- **Type Safety**: Add types, fix implicit anys, enable strict modes
- **Test Health**: Stabilize flaky tests, raise coverage
- **CI/CD**: Fix GitHub Actions pipelines
- **Developer Experience**: Add helpful scripts, improve Makefiles
- **Dependency Hygiene**: Upgrade patch/minor versions, remove unused deps
- **Documentation**: Quickstart, setup, run/test instructions
- **Security**: Basic static checks, secret scanning
- **Dead Code**: Remove unused files/symbols, resolve warnings
- **Code Quality**: Small, safe, incremental refactors

## Usage

### Starting the Steward

```bash
# From the project root
python3 ai-gods/autonomous_steward.py
```

Or use the provided startup script:

```bash
# Make executable (first time only)
chmod +x START_AUTONOMOUS_STEWARD.sh

# Run
./START_AUTONOMOUS_STEWARD.sh
```

### Monitoring Progress

The steward continuously updates `PROGRESS.md` with:
- Discovery findings
- Tasks completed
- Commands executed
- Test/build status
- Next steps

You can also monitor the log file:

```bash
tail -f godmode-logs/autonomous-steward.log
```

### Stopping the Steward

Press `Ctrl+C` to gracefully stop the steward. It will finish its current task and exit.

## Commit Message Format

The steward uses **Conventional Commits**:

```
<type>(<scope>): <short imperative summary>

WHY: <1-2 lines of reasoning/impact>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `ci`

## PROGRESS.md Entry Format

```markdown
## YYYY-MM-DD HH:mm – <type>: <short summary>
- Why: <one-liner>
- Changes: <files/modules touched>
- Commands: <key commands executed>
- Result: <tests/build status, coverage delta if known>
- Next: <small follow-up, if any>
```

## Constraints

### What the Steward CAN Do

- Read/modify files within the current workspace
- Create/modify config, scripts, tests, docs, tooling
- Run local development commands (git, npm, pip, pytest, etc.)
- Create branches, commits, and local merges
- Manage a local task backlog and execute in priority order

### What the Steward CANNOT Do

- Touch files outside the workspace
- Make global system installs
- Make network calls except to package registries (npm, PyPI)
- Upload code or data to external services
- Change the public API without updating tests/docs

### Fallback Behavior

When blocked:
- Auto-installs missing tools locally (as dev dependencies)
- If still blocked, skips that task and chooses next highest-impact item
- Never stops - always finds work to do

## Success Criteria

- ✅ Each hour produces at least one merged, useful, low-risk improvement
- ✅ The repo becomes easier to build, test, understand, and change
- ✅ PROGRESS.md shows a continuous stream of atomic, reversible improvements

## Integration with Existing Systems

The Autonomous Steward complements existing systems:

- **autonomous_development.py**: Self-healing and improvement system
- **vscode_self_correction.py**: VSCode-specific error correction
- **autonomous_development_v2.py**: V2 async operations
- **run_10x10_tests.py**: Comprehensive test runner

The steward can coexist with these systems and focuses on continuous small improvements.

## Troubleshooting

### Steward Not Making Progress

Check:
1. Are there merge conflicts? Resolve manually
2. Is git in a clean state? Check `git status`
3. Are there permission issues? Check file permissions
4. Check logs: `cat godmode-logs/autonomous-steward.log`

### Tasks Being Skipped

Tasks are skipped when safety rules trigger. Check the log for:
- `Task blocked by safety rule: <reason>`
- The steward will automatically move to the next safe task

### Want to Disable Steward

Simply stop the process with `Ctrl+C` or kill the process. No cleanup needed.

## Configuration

The steward is designed to work out-of-the-box with sensible defaults. Configuration is intentionally minimal to support autonomous operation.

To customize:
- Edit task priorities in `autonomous_steward.py`
- Modify safety rules in the `SafetyChecker` class
- Adjust discovery patterns for your project structure

## Future Enhancements

Potential improvements (feel free to contribute):

- [ ] Support for more languages (Java, Go, Rust)
- [ ] Machine learning for task prioritization
- [ ] Integration with GitHub Issues for task tracking
- [ ] Performance benchmarking and optimization
- [ ] Code coverage tracking and improvement
- [ ] Automated security vulnerability scanning
- [ ] Integration with CI/CD for automated testing
- [ ] Support for monorepo structures
- [ ] Custom task plugins

## Contributing

The steward is part of the Flowstate-AI project. To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Run linting and tests
5. Submit a pull request

## License

Same as the main Flowstate-AI project (MIT License).

---

Built with 🤖 for autonomous, continuous improvement.
