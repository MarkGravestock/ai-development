# ai-development

Working practice for AI-assisted software delivery. The process comes first:
a short, iterative loop — walking skeleton, thinnest next slice, always
releasable, real feedback over up-front planning. The guardrails thesis and
the skills below exist to keep that loop fast and safe, and are synced to
Claude Code, Tabnine and opencode.

## Process

Delivery runs as an OODA loop — Observe, Orient, Decide, Act — at the
smallest grain that produces real signal, not as sequential phases.

Reasoning and evidence: [practices/delivery-process.md](practices/delivery-process.md).

## Thesis (guardrails)

Deterministic guardrails beat prompt volume. Frameworks shipping large prompt
corpora ("software factories") underperform their marketing; the reproducible
gain comes from the computational controls they happen to bundle — formatters,
type checkers, architecture rules, tests — rather than from personas and
workflow ceremony. Spend on sensors. This is what makes the Act step of the
loop above fast without being reckless.

Reasoning and evidence: [tooling/approach.md](tooling/approach.md).

## Contents

Three areas, ordered by half-life.

```
ai-development/
├── practices/  what good development is — durable, agent or no agent
├── skills/     that knowledge in the form an agent loads on demand
└── tooling/    what installs it and configures the harness — expires fastest
```

`skills/` is its own category, not a subdirectory of either. A skill is a durable
body in a perishable envelope: if the `SKILL.md` format died tomorrow you would
rewrite four lines of frontmatter and keep every word of Beck, North and
Khononov underneath. `tooling/harness/opencode/models.md` is the opposite —
perishable all the way through, which is what earns it a place there. That is
the same fourth principle
[`tooling/harness/README.md`](tooling/harness/README.md) already states:
investment proportionate to half-life.

| Path | What |
|---|---|
| `practices/delivery-process.md` | The OODA loop, walking skeleton, MVP slicing, why short feedback loops |
| `practices/guardrails-catalogue.md` | Guardrails by category and type, Java and Python |
| `practices/dependencies.md` | Libraries as guardrails; supply-chain gates |
| `skills/` | On-demand skills — analysis, design, testing, writing (catalogue: [skills/README.md](skills/README.md)) |
| `tooling/approach.md` | Guardrails thesis, control taxonomy, evidence base, known limits |
| `tooling/harness/` | Harness configuration and the principles behind it — opencode two-tier model setup ([tooling/harness/README.md](tooling/harness/README.md)) |
| `tooling/sync.py` | Installs skills into Claude Code, Tabnine and opencode (via `uv run poe sync`) |

## Rules

- Deterministic tools own everything they can judge. Skills cover only the rest.
- Auto-fix over review comment; gate over suggestion.
- Any rule expressible as a check becomes a check, not prose.
- Never weaken a quality check to reach green.
- Harness-agnostic where possible. The gauntlet survives a harness swap; a
  prompt corpus does not.
- Spend words on the example, not the exposition. "Agents readily produce tests
  that assert nothing, and only PIT or mutmut will notice" carries a paragraph
  of description about mutation testing.

## Install / sync

```bash
uv run poe sync                      # copy everything to every target below
uv run poe sync-link                 # symlink instead — edits in this repo apply live
uv run poe sync -- design/cupid      # narrow to one topic or skill dir, recursively

python tooling/sync.py [copy|link] [subdir]   # same, without uv/poe — stdlib-only
```

| Harness | Install target | Override |
|---|---|---|
| Claude Code | `~/.claude/skills` | `CLAUDE_SKILLS_DIR` |
| Tabnine | `~/.tabnine/agent/skills` | `TABNINE_SKILLS_DIR` |
| opencode | `~/.config/opencode/skills` (`$XDG_CONFIG_HOME/opencode/skills` when set) | `OPENCODE_SKILLS_DIR` |

One script, stdlib-only: it walks `skills/` for any directory holding a `SKILL.md` and
installs it under that file's `name:` frontmatter (`skills/design/cupid/python/` installs as
`cupid-python`). Names are flat — the topic dirs organise the repo, not the install targets.

<details>
<summary>How the sync works — narrowing, companion files, symlink mode</summary>

Pure Python, so it behaves the same on Windows, macOS and Linux; `uv run poe ...` is only a
wrapper over `python tooling/sync.py`, which needs nothing but a Python 3.9+ interpreter on `PATH`. A
`subdir` argument narrows the walk to one topic or a single skill (`design`, `design/cupid`,
`design/cupid/python`).

A few skills need a canonical file copied in beside their `SKILL.md`, because an installed
skill only ever sees its own directory — the CUPID stack skills need `cupid-properties.md`.
Declared in `COMPANION_FILES` near the top of `tooling/sync.py`. The notes tooling target is
overridable via `NOTES_ROOT`.

Symlink mode (`sync-link`) needs Developer Mode on Windows (Settings > Privacy & security >
For developers) or an elevated shell — unprivileged `os.symlink` is blocked otherwise.

</details>

<details>
<summary>opencode — verifying an install, and the duplicate-skill warning</summary>

opencode has no CLI for installing skills (`opencode --help` covers agents, plugins and MCP
servers, not skills), so the sync writes directories like the other two targets. It scans
`{skill,skills}/**/SKILL.md` under its config dir, keyed on the `name:` frontmatter rather
than the directory name — the same convention `tooling/sync.py` already uses. Verify an install with
`opencode debug skill`, which lists every skill it can see and where each was loaded from.

opencode also reads `~/.claude/skills/**/SKILL.md` and `~/.agents/skills` by default, so
anything synced for Claude Code already reaches it. Installing to both means each skill is
found twice and opencode logs a `duplicate skill name` warning; the content is identical, so
this is noise rather than breakage. Set `OPENCODE_DISABLE_CLAUDE_CODE` to stop it reading the
Claude directory, or `OPENCODE_DISABLE_EXTERNAL_SKILLS` to stop both, if the warnings bother
you.

</details>

## Skills

The full skill catalogue, plus the altitude model that explains how the design skills
compose with each other, lives in [skills/README.md](skills/README.md).
