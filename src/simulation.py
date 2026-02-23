import numpy as np
import pandas as pd


def run_monte_carlo(prices, weights, T, N, initial_portfolio_value):
    """
    Runs a Monte Carlo simulation for portfolio prices.

    Args:
        prices (pd.DataFrame): Historical prices (index=Date, cols=Tickers).
        weights (list/np.array): Initial weights (must sum to 1).
        T (int): Simulation time horizon in years.
        N (int): Number of simulation runs.
        initial_portfolio_value (float): Initial investment amount.

    Returns:
        np.array: Portfolio value paths (shape: steps+1, N).
    """

    # 1. Setup simulation parameters
    n_days = 252  # Trading days in a year
    steps = T * n_days
    weights = np.array(weights)

    # 2. Calculate Log Returns
    # Ensure prices is a DataFrame
    if isinstance(prices, pd.Series):
        prices = prices.to_frame()

    log_returns = np.log(prices / prices.shift(1)).dropna()

    # Ensure log_returns is a DataFrame for consistent matrix operations
    if isinstance(log_returns, pd.Series):
        log_returns = log_returns.to_frame()

    # 3. Calculate Mean (Drift) and Covariance Matrix
    mu = log_returns.mean().values  # Daily mean log returns (1D array)
    cov_matrix = log_returns.cov().values  # Daily covariance of log returns (2D array)

    # 4. Perform Cholesky Decomposition
    # L * L.T = cov_matrix
    try:
        L = np.linalg.cholesky(cov_matrix)
    except np.linalg.LinAlgError:
        # If matrix is not positive definite (rare but possible with sparse data),
        # force symmetry or check eigenvalues
        cov_matrix = (cov_matrix + cov_matrix.T) / 2
        min_eig = np.min(np.real(np.linalg.eigvals(cov_matrix)))
        if min_eig < 0:
            cov_matrix -= 10 * min_eig * np.eye(cov_matrix.shape[0])
        L = np.linalg.cholesky(cov_matrix)

    n_assets = len(weights)

    # 5. Generate Random Normal Shocks (Standard Normal)
    # Shape: (steps, N, n_assets)
    Z = np.random.normal(0, 1, size=(steps, N, n_assets))

    # 6. Correlate Shocks using Cholesky Matrix
    # We want correlated returns: R = mu + L * Z
    # Broadcasting: (steps, N, n_assets) dot (n_assets, n_assets).T
    # Result: correlated_returns shape (steps, N, n_assets)
    correlated_returns = mu + np.einsum("sna,ba->snb", Z, L)

    # 7. Calculate Simulated Price Paths for Each Asset
    # P_t = P_0 * exp(cumsum(returns))
    # Shape: (steps, N, n_assets)
    cumulative_returns = np.cumsum(correlated_returns, axis=0)

    # Add initial state (zeros) for cumulative returns at t=0
    # Shape becomes (steps+1, N, n_assets)
    cumulative_returns = np.vstack([np.zeros((1, N, n_assets)), cumulative_returns])

    # Get last known prices (ensure shape matches n_assets)
    last_prices = prices.iloc[-1].values

    # Calculate simulated prices
    # Shape: (steps+1, N, n_assets)
    simulated_prices = last_prices * np.exp(cumulative_returns)

    # 8. Aggregate Asset Paths into Portfolio Value Paths
    # Calculate initial number of shares based on initial weights and prices
    # Allocation for each asset based on weights
    initial_allocations = initial_portfolio_value * weights

    # Number of shares bought at t=0
    shares = initial_allocations / last_prices

    # Portfolio Value = Sum(Price_i * Shares_i)
    # The sum is over the asset dimension (axis=2)
    # Result shape: (steps+1, N)
    portfolio_paths = np.sum(simulated_prices * shares, axis=2)

    return portfolio_paths
