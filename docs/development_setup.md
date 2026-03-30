# Development Setup

## Setup

1. Install uv:
   - With the offical [installer](https://docs.astral.sh/uv/getting-started/installation).
   - With Pip:
      ```bash
      pip install uv
      ```

2. Sync dependencies:
   ```bash
   uv sync
   ```

3. Install Precommit:
   ```bash
   uv tool install pre-commit --with pre-commit-uv
   pre-commit install
   ```
