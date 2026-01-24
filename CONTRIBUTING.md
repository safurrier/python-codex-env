# Contributing to bq-util

Thank you for your interest in improving `bq-util`!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone git@github.com:your-username/bq-util.git`
3. Create a branch: `git checkout -b feature-name`
4. Install dependencies: `make setup`
5. Make your changes with accompanying tests and documentation updates
6. Run the full quality suite: `make check`
7. Commit: `git commit -m "Description of changes"`
8. Push: `git push origin feature-name`
9. Open a Pull Request

## Development Guidelines

- All code must be type annotated and pass `mypy`
- Add or update tests for new functionality (`pytest` is required)
- Keep documentation current with behavioural changes
- Ensure `make check` succeeds before submitting a PR

## Pull Request Checklist

- [ ] Update `README.md` or docs when behaviour changes
- [ ] Update `CHANGELOG.md`
- [ ] Provide clear descriptions of user-facing changes

## Questions?

Open an issue if anything is unclear or you need help getting started.
