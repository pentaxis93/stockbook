- Always use the TDD approach by building comprehensive test coverage defining all expected behavior before writing a
  single line of implementation code.
  - Write tests first to define the expected behavior.
  - The tests should fail. At this point, simply allow the tests to fail, rather than skipping them or commenting them out.
  - Implement the code to make the tests pass.
  - Refactor the code to make it more readable.

- Full type safety is mandatory in all production code and test code.
  - All code must pass the strictest static type checking (`pyright --strict`) before it can be committed.
  - Do not rely on type inference alone; use explicit type annotations where appropriate.
  - Begin with type safety in mind from the start, as retrofitting types later is discouraged and inefficient.

- When you implement a temporary fix or defer a task in your code—like simplifying a class or postponing tests—document it with a clear TODO or FIXME comment that explains what needs to be done and why. This ensures the task isn’t forgotten and can be revisited during code reviews or sprint planning.

- When writing git commit messages, omit all references to authorship, and especially omit references to Claude.

- Always run all quality checks and fix all issues before making a commit.
  - Use `make test` to run ALL quality checks (linting, formatting, type checking, tests, coverage, security)
  - This is the ONLY command that should be used for testing and quality checks
  - This single command runs the same checks as pre-commit hooks and CI/CD
  - Use `make help` to see all available commands

- Always update the docs/DEVELOPMENT_ROADMAP.md and README.md files with the latest changes when significant progress is made.

- NEVER disable the pre-commit hooks.

- NEVER force a commit if the pre-commit hooks fail.

- NEVER use `--no-verify` to bypass pre-commit hooks. If your code does not pass tests or checks, fix it. Bypassing verification is never acceptable and will result in a rejected commit.
