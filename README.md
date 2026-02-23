# Portfolio Simulator

A Streamlit application for Monte Carlo portfolio simulation. This tool allows users to project the future value of a portfolio based on the historical performance (returns and volatility) of its constituent assets.

## What Does This Simulate?

This application simulates **future portfolio value paths** over a specified time horizon. It projects how your portfolio *might* perform in the future based on how the assets in it have performed in the past.

Instead of predicting one specific future (e.g., "The stock will go up 5%"), it generates `N` (e.g., 100 or 1000) different imaginary timelines. By analyzing all of them, you can estimate the range of likely outcomes—best case, worst case, and expected value.

## Methodology: The Monte Carlo Simulation

### The Mathematical Model
The simulation uses a **Multivariate Geometric Brownian Motion (GBM)** model. This is the standard model for stock price dynamics in quantitative finance.

The core equation for the daily return ($R_t$) of an asset is:

$$ R_t = \mu + L \cdot Z_t $$

Where:
*   **$\mu$ (Drift):** The expected daily return. This is calculated directly from your input data as the **average historical daily log return**.
*   **$Z_t$ (Random Shock):** A vector of random numbers drawn from a standard normal distribution (mean=0, variance=1). This introduces the element of uncertainty.
*   **$L$ (Cholesky Matrix):** This is the key to the simulation's accuracy. It is a lower triangular matrix derived from the **Covariance Matrix** of your historical returns.

### How Volatility and Correlation are Calculated
The simulation does **not** use a single "volatility" number for the whole portfolio. Instead, it captures the complex risk structure of your assets using a **Covariance Matrix**:

1.  **Calculate Log Returns:** First, we compute the daily log returns from the historical prices you provide: $\ln(P_t / P_{t-1})$.
2.  **Compute Covariance Matrix:** We calculate the covariance matrix of these returns.
    *   **Diagonal elements:** Represent the **variance** (volatility squared) of each individual asset.
    *   **Off-diagonal elements:** Represent the **covariance** (correlation) between assets. This captures how assets move together (e.g., if Tech stocks go up, does Energy go down?).
3.  **Cholesky Decomposition:** We decompose this matrix ($C = L \cdot L^T$). Multiplying the random noise ($Z_t$) by $L$ transforms the uncorrelated noise into returns that share the **exact same volatility and correlation structure** as your historical data.

### Is This Mathematically Correct?
**Yes, it is mathematically consistent** for a standard "Historical Drift" Monte Carlo simulation, with the following standard assumptions:

*   **Historical Bias:** The model assumes that future returns (`mu`) and correlations (`cov`) will be identical to the historical period used for calibration. In reality, market regimes change.
*   **Normal Distribution:** It assumes returns follow a Normal (Bell) curve. Real markets often have "fat tails" (extreme crashes happen more often than predicted).
*   **Constant Parameters:** Drift and volatility are assumed to be constant over the simulation horizon.

## Project Structure

*   `app.py`: Main Streamlit application entry point.
*   `src/data.py`: Handles fetching historical data from Yahoo Finance.
*   `src/simulation.py`: Contains the core Monte Carlo logic and matrix operations.
*   `src/visualization.py`: Generates interactive plots using Plotly.

## Getting Started

### Prerequisites

This project uses `uv` for dependency management.

```bash
# Install dependencies
uv sync
```

### Running the Application

```bash
uv run streamlit run app.py
```

### Development

*   **Linting:** `uv run ruff check .`
*   **Formatting:** `uv run ruff format .`
