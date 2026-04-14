# CC-SDLC Bootstrap

This file bootstraps the cc-sdlc framework in your project. Say **"Bootstrap SDLC"** or **"Initialize SDLC"** in Claude Code.

## Source

```
repo: https://github.com/Inpacchi/cc-sdlc
branch: master
```

## Bootstrap Instructions

When the user asks to bootstrap or initialize SDLC, follow these steps:

### Step 1: Fetch the Framework

Clone the cc-sdlc repo to a temporary location:

```bash
git clone --depth 1 https://github.com/Inpacchi/cc-sdlc.git /tmp/cc-sdlc-bootstrap
```

### Step 2: Install the Initialize Skill

Copy the initialize skill to this project:

```bash
mkdir -p .claude/skills
cp -r /tmp/cc-sdlc-bootstrap/skills/sdlc-initialize .claude/skills/
```

### Step 3: Run Initialization

Read and execute `.claude/skills/sdlc-initialize/SKILL.md`. Pass `/tmp/cc-sdlc-bootstrap` as the cc-sdlc source path.

The skill handles:
- Installing all framework files (skills, agents, knowledge, process docs)
- Writing CLAUDE.md
- Creating domain agents
- Seeding knowledge stores
- Verification

### Step 4: Cleanup (Mandatory)

After initialization completes successfully, clean up:

```bash
rm -rf /tmp/cc-sdlc-bootstrap
rm -f .claude/BOOTSTRAP.md BOOTSTRAP.md
```

The framework is now installed — this bootstrap file is no longer needed.

---

## Notes for Claude Code

1. **Clone to temp** — Don't pollute the user's project with the full cc-sdlc repo. Always clone to `/tmp/cc-sdlc-bootstrap`.
2. **Verify before proceeding** — Check that `skeleton/manifest.json` exists after clone. If the clone failed, stop and report the error.
3. **Pass the source path** — The initialize skill needs to know where the source is. Pass `/tmp/cc-sdlc-bootstrap` as `$ARGUMENTS`.
4. **Preserve existing work** — Never overwrite existing CLAUDE.md. The skill augments, not replaces.
5. **Clean up on success** — Remove both `/tmp/cc-sdlc-bootstrap` AND this bootstrap file when done. The bootstrap file served its purpose.
6. **Clean up on failure** — If initialization fails partway, still remove `/tmp/cc-sdlc-bootstrap` but leave the bootstrap file so the user can retry.

---

## One-Liner Install

```bash
curl -fsSL https://raw.githubusercontent.com/Inpacchi/cc-sdlc/master/BOOTSTRAP.md -o .claude/BOOTSTRAP.md
```

Then in Claude Code: **"Bootstrap SDLC"**
