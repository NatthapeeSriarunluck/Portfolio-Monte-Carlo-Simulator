# AGENTS.md

This document serves as the primary reference for AI agents and developers working on the `portfolio_simulator` repository. It outlines the build process, testing procedures, code style guidelines, and architectural decisions.

## 1. Project Overview & Architecture

**Goal:** A Streamlit application for Monte Carlo portfolio simulation using historical data from Yahoo Finance.

**Structure:**
- `app.py`: Main entry point. Handles UI logic and orchestrates data flow.
- `src/data.py`: Data fetching layer. Handles API calls to `yfinance` and caching via `@st.cache_data`.
- `src/simulation.py`: Core mathematical engine. Performs Cholesky decomposition and vectorized Monte Carlo simulations using `numpy`.
- `src/visualization.py`: Presentation layer. Generates interactive Plotly charts.

**Key Design Principles:**
- **Separation of Concerns:** UI (`app.py`), Logic (`src/simulation.py`), and Data (`src/data.py`) must remain decoupled.
- **Vectorization:** Simulation logic must use `numpy` matrix operations. Avoid Python loops for calculation steps.
- **Caching:** Expensive operations (data fetching) must be cached to prevent API rate limits.

## 2. Environment & Build Commands

The project uses `uv` for dependency management and execution.

### Setup
```bash
# Install dependencies
uv sync

# Install dev dependencies (if not installed by default)
uv sync --dev
```

### Running the Application
```bash
uv run streamlit run app.py
```

### Linting & Formatting
We adhere to `ruff` defaults for linting and formatting.

```bash
# Run linter
uv run ruff check .

# Fix linting issues automatically
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Testing
*Note: Currently, no test suite exists. Agents adding features must add corresponding tests.*

Recommended command for running tests (once added):
```bash
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_simulation.py

# Run a specific test function
uv run pytest tests/test_simulation.py::test_monte_carlo_logic
```

## 3. Code Style Guidelines

All code modifications must strictly follow these guidelines.

### formatting
- **Line Length:** 88 characters (standard Black/Ruff compatible).
- **Indentation:** 4 spaces.
- **Quotes:** Double quotes `"` for strings.

### Imports
Organize imports in three blocks, separated by a blank line:
1.  **Standard Library** (`import os`, `import sys`)
2.  **Third-Party** (`import pandas`, `import streamlit`)
3.  **Local Application** (`from src.data import get_stock_data`)

```python
import numpy as np
import pandas as pd

from src.simulation import run_monte_carlo
```

### Type Hinting
**Mandatory** for all function signatures. Use standard types (`list`, `dict`, `tuple`) or `typing` module for complex structures.

```python
def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    ...
```

### Naming Conventions
- **Variables/Functions:** `snake_case` (e.g., `calculate_portfolio_variance`).
- **Classes:** `PascalCase` (e.g., `PortfolioSimulator`).
- **Constants:** `UPPER_CASE` (e.g., `TRADING_DAYS = 252`).
- **Private Members:** Prefix with `_` (e.g., `_internal_helper`).

### Documentation
- **Docstrings:** Required for all public modules, classes, and functions. Use Google-style docstrings.
- **Comments:** Explain *why*, not *what*.

```python
def get_data(ticker: str) -> pd.DataFrame:
    """
    Fetches historical data for a given ticker.

    Args:
        ticker (str): The stock symbol (e.g., 'AAPL').

    Returns:
        pd.DataFrame: A dataframe containing 'Adj Close' prices.
    """
    pass
```

### Error Handling
- Use specific exception types (e.g., `ValueError`, `ConnectionError`) rather than bare `except Exception:`.
- External API calls (like `yfinance`) must be wrapped in `try/except` blocks to handle network failures or invalid tickers gracefully.
- In `app.py`, catch errors and display user-friendly messages using `st.error()`.

## 4. Specific Implementation Details

### Data Fetching (`src/data.py`)
- Always use `auto_adjust=True` in `yfinance` to get split/dividend-adjusted prices.
- Handle `MultiIndex` columns returned by `yfinance` when fetching multiple tickers.
- Use `@st.cache_data` for data fetching functions to improve performance.

### Simulation (`src/simulation.py`)
- Use **Cholesky Decomposition** for correlating asset returns.
- Ensure the covariance matrix is positive semi-definite. If `np.linalg.cholesky` fails, implement a fallback (e.g., finding the nearest positive definite matrix).

### Visualization (`src/visualization.py`)
- Use `plotly.graph_objects` for maximum control over interactivity.
- Downsample simulation paths (e.g., show only first 50-100) in line charts to prevent browser rendering lag.

## 5. Agent Operational Rules
1.  **Read First:** Before modifying `app.py` or `src/`, read the file to understand the current context.
2.  **Verify:** After making changes, run `ruff check .` to ensure no linting errors were introduced.
3.  **Test:** If adding logic, create a minimal reproduction script or test case to verify correctness before finalizing.
