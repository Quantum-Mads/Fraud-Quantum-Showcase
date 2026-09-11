# Python-Schema

## 🚀 Getting Started

This guide explains how to set up and run the project using **UV** (the fast Python package manager) for efficient dependency management and environment creation. This project uses a **`pyproject.toml`** file to define dependencies across different environments (main, dev, pre-prod).

### 🛠️ Prerequisites

* **UV** (Ensure you have UV installed on your system).
* The system-level **Python** executable.

---

### 🔱 Generate Github branches

Execute python create_branches.py

## 🏗️ Setup & Installation

We use **UV** to handle the virtual environment and synchronize dependencies quickly.

### 1. Create the Virtual Environment

Use the simplified `uv venv` command. UV automatically creates an isolated environment, typically named **`.venv`**, in your current directory.

```bash
uv venv
```

2. Install Dependencies by Environment
Instead of requirements.txt, we use uv sync with the --extras flag to install specific dependency groups defined in pyproject.toml.

Development Environment (Dev)
Use this for coding, unit testing, and tooling (includes pytest).

Bash
```bash
uv sync --extra dev
```

Pre-Production Environment (Pre-Prod)
Use this for integration testing, staging, or QA (includes base dependencies + specific QA tools).

Bash
```bash
uv sync --extra pre-prod
```

Main Environment (Production)
To install only the minimal dependencies for production (base dependencies only, no extras):

Bash
```bash
uv sync
```
Note: There's no need to manually activate the environment. The uv run command handles activation automatically by detecting the .venv.

🔎 Security Audit
Run a security audit on your project's dependencies using uv run. This command executes the pip-audit tool within the active virtual environment to scan for known vulnerabilities in your installed packages.

Bash
```bash
uv run pip-audit .
```

🧪 Post-Audit Testing
After auditing your dependencies (and especially if you have updated any vulnerable packages), it is essential to launch your project's tests using pytest to verify that no functionality has been broken by the library updates.

Bash
```bash
uv run pytest -v
```

✨ Running the Project
To execute your main script, use uv run followed by the standard Python command.

Bash
```bash
uv run python main.py
```

🎨 Code Formatting
Standardize the codebase using the Black tool to ensure consistency and adherence to style standards.

Bash
```bash
uv run black .
```

📈 Results Report
After execution, you can view the results:

Open blablabla in your web browser.