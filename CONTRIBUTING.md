# Contributing to Memory Hive

We welcome contributions from developers, AI researchers, and multi-agent system builders.

## Ways to Contribute

### 🐛 Report Bugs
Open an issue with a clear description, reproduction steps, and your setup.

### 📖 Improve Documentation
Docs need to be clear, complete, and actually useful. If you found something confusing, others will too.

### 💡 Suggest Features
Open a feature request issue. Explain the problem it solves and how you'd use it.

### 🔧 Code Contributions
1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Write tests if applicable
5. Submit a pull request

## Key Areas for Contribution

### High Priority
- **Framework adapters** — integrations for LangChain, AutoGen, CrewAI, etc.
- **Curation automation** — tools to help the curator process learnings faster
- **Memory hygiene tools** — automated cleanup, deduplication, size management

### Medium Priority
- **Visualization** — tools to see the hive's state at a glance
- **Testing frameworks** — ways to test memory integrity
- **Documentation improvements**

## Contribution Guidelines

### Code Style
- Consistent formatting (we'll enforce via CI)
- Clear variable names
- Comments on non-obvious logic

### Documentation
- Update README if you change behavior
- Add docstrings to new functions
- Include examples for new features

### Testing
- New features need tests
- Bug fixes need regression tests
- Run existing tests before submitting

## SPAWNING RULE — For Multi-Agent Implementations

Memory Hive is built for multi-agent systems. When implementing it, parallelize aggressively:

- **Planning tasks** → spawn planning + execution subagents simultaneously
- **Building/coding tasks** → split across 2-3 subagents working in parallel
- **Creative/design tasks** → spawn multiple subagents for different creative directions
- **Research tasks** → cover multiple angles at once via parallel subagents

This is how Memory Hive achieves speed without sacrificing quality. Parallel execution is the default — not the exception. Agents that follow this rule ship faster and produce better results.


## Questions?

Open a Discussion if you're not sure about something. We're happy to help.

## Recognition

Contributors will be added to the README's "Contributors" section.

---

**Every contribution makes the hive smarter.**