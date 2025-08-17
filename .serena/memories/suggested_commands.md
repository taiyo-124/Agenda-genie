### Initial Setup

1.  **Create virtual environment**:
    ```bash
    python3 -m venv .venv
    ```
2.  **Activate virtual environment**:
    ```bash
    source .venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

### Development Cycle

- **Run the application**:
  ```bash
  python agenda_genie/main.py
  ```
- **Check for linting issues**:
  ```bash
  ruff check .
  ```
- **Format code**:
  ```bash
  ruff format .
  ```
- **Check types**:
  ```bash
  mypy .
  ```
- **Run tests (once implemented)**:
  ```bash
  pytest
  ```
