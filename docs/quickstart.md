# Quickstart

This is the shortest path to install and verify Converge locally.

## 1. Clone

```bash
git clone https://github.com/Zaoqu-Liu/converge-skill.git
cd converge-skill
```

## 2. Verify The Repository

```bash
python3 scripts/verify.py
```

Expected result:

```text
Repository verification passed.
```

## 3. Install To Local Agent Hosts

```bash
python3 skills/converge/scripts/sync_converge_install.py
```

This installs Converge into the supported H1 skill surfaces:

- Claude Code
- Cursor
- opencode
- Cline
- Google Antigravity

It also installs the Cursor rule bridge.

## 4. Check Local Install Consistency

```bash
python3 skills/converge/scripts/check_converge_release.py --source skills/converge --targets all
```

Expected result:

```text
Converge release check passed.
```

## 5. Use It

Invoke Converge explicitly when the user input is fuzzy or high-stakes:

```text
$converge help me think through this decision
```

Or rely on host skill discovery where supported by the active host.

## Claim Boundary

Successful install means H1 coverage. It does not prove native interactive question UI behavior or production-like behavior. Use `docs/host-support.md` before making stronger support claims.
