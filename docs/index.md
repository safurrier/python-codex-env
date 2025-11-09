# Python Collab Template

A modern, collaborative Python project template with comprehensive tooling and best practices built-in.

## 🎯 Template Features

This template provides everything you need for a professional Python project:

- 🔧 **Modern Tooling**: UV package manager, Ruff formatting/linting, MyPy type checking
- 🧪 **Testing**: pytest with coverage reporting and CI integration
- 📚 **Documentation**: Optional MkDocs + Material theme with auto-generation
- 🧰 **BigQuery CLI**: Production-ready Click application with job analysis tools
- 🚀 **CI/CD**: GitHub Actions with quality checks and automated deployment
- 🐳 **Development**: Docker support and pre-commit hooks
- 📦 **Packaging**: Modern pyproject.toml configuration with hatchling

## 🚀 Quick Start

### Using This Template

1. **Create a new repository** from this template on GitHub
2. **Clone your new repository**:
   ```bash
   git clone https://github.com/your-username/your-project-name.git
   cd your-project-name
   ```
3. **Initialize your project**:
   ```bash
   make init
   ```
4. **Follow the prompts** to customize your project

### What `make init` Does

The initialization script will:
- Prompt for project name, description, and author information
- Update all configuration files with your project details
- Choose how to handle example code (keep, simplify, or remove)
- Optionally set up MkDocs documentation (default: yes)
- Rename directories and update imports
- Set up git repository and pre-commit hooks

## 📁 Template Structure

```
python-collab-template/
├── src/                        # Source code (renamed during init)
├── tests/                      # Test files
├── scripts/                    # Utility scripts (including init)
├── templates/                  # Documentation templates
├── docker/                     # Docker configuration
├── .github/workflows/          # CI/CD automation
├── pyproject.toml             # Project configuration
├── Makefile                   # Development commands
└── README.md                  # Project documentation
```

## 🛠️ Available Commands

After initialization, your project will have these commands:

- `make setup` - Set up development environment
- `make test` - Run tests with coverage
- `make check` - Run all quality checks
- `make docs-serve` - Serve documentation locally (if enabled)
- `make docs-build` - Build documentation (if enabled)

For complete usage instructions, see the [Getting Started](getting-started.md) guide.