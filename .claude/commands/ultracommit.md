~~~
🧠 UltraCommit Protocol: The Prime Directive

**Mission Objective:**
Before you commit, **attempt the commit**. If it succeeds, excellent — you're done.
If it fails due to pre-commit pipeline checks, **your mission begins**: resolve every issue with thoughtful, high-quality engineering solutions. You are authorized to take the time required to do this without compromise.

---

## ✅ Success Criteria:
- All pre-commit hooks pass.
- Lint, tests, and coverage thresholds are satisfied.
- Your commit is successfully recorded.
- It appears cleanly in the `git log`.

---

## 🧾 Writing a Great Commit Message (Conventional Format)

Follow the [Conventional Commits](https://www.conventionalcommits.org) style for clarity and automation-friendliness:

**Format:**
```
<type>(optional-scope): <short, imperative summary>
```

**Examples:**
```
feat(api): add batch trading endpoint
fix(auth): handle expired tokens more gracefully
refactor(core): simplify order book matching logic
test(trading): add fuzzing for market open edge cases
docs: clarify usage of trading fee tiers
```

**Best Practices:**
- Use the imperative mood (e.g., “add” not “adds”).
- Be concise but descriptive — ~50 characters for summary is ideal.
- Optionally follow with a blank line and more detail if needed.

---

## 🔬 Troubleshooting Workflow

If the commit fails:
1. **Read the output** carefully — understand the root cause.
2. **Fix each warning/error** thoroughly, not superficially.
3. Run `make test`.
4. Re-attempt commit.
5. Repeat until ✅.

---

## 💡 Philosophy

This is not a race. Every failed commit is a chance to **sharpen your engineering judgment** and **elevate the codebase**. Your commit reflects your professionalism.

The commit must **earn its place** in our shared history.

You got this. 🛠️

~~~

