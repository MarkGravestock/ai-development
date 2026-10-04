---
name: promote-to-guardrail
description: Turn a problem that keeps recurring into a deterministic, tested rule in the project's check gauntlet. Use when the same review finding, agent mistake, spec or guideline violation, or escaped bug shows up a second time, or when asked "can we stop this happening again", "add a lint rule for", "enforce this convention", or "make this a guardrail". Proof of concept; Python-first (Ruff banned-api, import-linter, ast-grep), with the same steps applying to Java.
---

# Promote a repeat finding to a guardrail

Applies the loop in `growing-guardrails.md` (a synced copy beside this file;
`practices/growing-guardrails.md` in the source repo). Read its ladder before step 3.

## 1. Confirm it's a repeat and size it

- State the finding in one sentence, in the project's terms ("domain code reads the wall
  clock"), and where it was seen before (issue, PR comment, commit).
- Search the codebase for every existing instance. For a syntactic shape, prototype the
  pattern directly: `uvx --from ast-grep-cli ast-grep run --lang python -p 'datetime.now($$$)' src/`.
  The hit count decides step 5.
- One occurrence and no others: stop and record it (a `guardrail-candidate` issue). Rules
  are for repeats.

## 2. Remove before you detect

Ask whether a type, a sanctioned library, or generated code would make the mistake
impossible. If yes, propose that instead, and add a rule only to stop the old way creeping
back. Say which you chose and why.

## 3. Pick the cheapest tool

Walk the ladder in `growing-guardrails.md` from the top and stop at the first tool that can
express the rule:

| Rule shape | Tool | Where |
|---|---|---|
| Banned import or call | Ruff `banned-api` (`TID251`) | `pyproject.toml` |
| Layer or module dependency | import-linter contract | `importlinter.ini` |
| Syntactic pattern, optionally limited to paths | ast-grep rule | `rules/` (scaffold below) |
| Taint, or needs real Python logic | Opengrep or Fixit | Stop and propose it; out of scope for this PoC |

Check what the project already has (`pyproject.toml`, `importlinter.ini`, `sgconfig.yml`)
and extend it rather than adding a second tool for the same job.

## 4. Write the rule test first, then the rule

- **ast-grep**: copy `scaffold/` from this skill into the project root if `sgconfig.yml`
  is missing. Write `rule-tests/<id>-test.yml` with at least one `invalid` snippet taken
  from a real instance found in step 1 and one `valid` snippet showing the sanctioned
  alternative. Run `ast-grep test --skip-snapshot-tests` and see it fail, then write
  `rules/<id>.yml` until it passes.
- **Ruff / import-linter**: no rule-test runner, so prove it by hand: run the check on a
  real instance and see it fail, fix or suppress it, and see it pass.
- **The message is the fix.** `message` says what is wrong in one line; `note` says what to
  do instead and names the sanctioned path. `url` links where the finding was first raised.
- Scope with `files:` / `ignores:` (ast-grep) or per-file config so tests, scripts and
  adapters that legitimately need the construct aren't flagged.

## 5. Deal with existing violations

- A handful and mechanical: fix them in the same change.
- Many, or risky to touch: suppress each one with a reason, never by relaxing the rule.
  ast-grep: `# ast-grep-ignore: <id>` on the line above. Ruff: `# noqa: TID251 - <reason>`.
  Report the count; it should only go down.

## 6. Gate it

- Add the check to the project's gate (for python-templates projects, a `rules` task in
  `[tool.poe.tasks]` and a step in the `check` sequence):

  ```toml
  [tool.poe.tasks.rules]
  sequence = [{cmd = "ast-grep test --skip-snapshot-tests"}, {cmd = "ast-grep scan"}]
  help = "Project-specific guardrails grown from repeat findings"
  ```

  ast-grep must be on the path: a dev dependency (`ast-grep-cli`) keeps it inside `uv sync`.
- Severity `error` only. A warning is a prompt, and prompts are the weak quadrant.
- Run the full gate and show it passing.

## 7. Report

```
Rule: <id> (<tool>) — <one-line finding>
Origin: <link to first and second occurrence>
Removed instead? <yes/no and why>
Existing hits: <n> fixed, <n> suppressed with reasons
Tests: <valid/invalid counts>, passing
Gate: <task/step added>, full check passing
```
