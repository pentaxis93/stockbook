- Always use the TDD approach by building comprehensive test coverage defining all expected behavior before writing a
  single line of implementation code.
  - Write tests first to define the expected behavior.
  - The tests should fail. At this point, simply allow the tests to fail, rather than skipping them or commenting them out.
  - Implement the code to make the tests pass.
  - Refactor the code to make it more readable.
- When you implement a temporary fix or defer a task in your code—like simplifying a class or postponing tests—document it with a clear TODO or FIXME comment that explains what needs to be done and why. This ensures the task isn’t forgotten and can be revisited during code reviews or sprint planning.
- When writing git commit messages, omit all references to authorship, and especially omit references to Claude.
- Always run `pytest`, `pylint`, `pyright`, `black`, and `isort` and fix all issues before making a commit.
- Always update the ROADMAP.md, TECHNICAL_DEBT.md, and README.md files in the project root with the latest changes.
