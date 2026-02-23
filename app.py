import streamlit as st
import pandas as pd
import numpy as np
from src.data import get_stock_data
from src.simulation import run_monte_carlo
from src.visualization import plot_simulation_results

# Set page config
st.set_page_config(page_title="Monte Carlo Portfolio Simulator", layout="wide")

st.title("Monte Carlo Portfolio Simulator 📈")
st.markdown("""
This app simulates the future performance of a portfolio using Monte Carlo methods.
It uses historical data to estimate the mean and covariance of asset returns and projects thousands of potential future paths.
""")

# --- Sidebar Inputs ---
st.sidebar.header("Portfolio Configuration")

# Tickers Input
tickers_input = st.sidebar.text_input(
    "Tickers (comma-separated)", value="SPY, TLT, GLD"
)
tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]

# Weights Input
weights_input = st.sidebar.text_input(
    "Weights (comma-separated)", value="0.6, 0.3, 0.1"
)
try:
    weights = [float(w.strip()) for w in weights_input.split(",") if w.strip()]
except ValueError:
    st.error("Invalid weights format. Please enter numbers separated by commas.")
    st.stop()

# Simulation Parameters
forecast_years = st.sidebar.slider("Forecast Years (Future)", 1, 30, 10)
historical_years = st.sidebar.slider("Historical Data Lookback (Past Years)", 1, 30, 10)
initial_investment = st.sidebar.number_input(
    "Initial Investment ($)", value=10000, step=1000
)
n_simulations = st.sidebar.number_input(
    "Number of Simulations (N)", min_value=10, max_value=10000, value=1000, step=50
)

# Validation
if not tickers:
    st.warning("Please enter at least one ticker.")
    st.stop()

if len(tickers) != len(weights):
    st.error(
        f"Number of tickers ({len(tickers)}) must match number of weights ({len(weights)})."
    )
    st.stop()

# Normalize weights if they don't sum to 1
total_weight = sum(weights)
if not np.isclose(total_weight, 1.0):
    weights = [w / total_weight for w in weights]
    st.sidebar.info(f"Weights normalized to sum to 1.0: {weights}")

# --- Main Execution ---

if st.sidebar.button("Run Simulation"):
    with st.spinner("Fetching data and running simulation..."):
        # 1. Get Data
        # Use a reasonable lookback window (e.g., 5 years or same as forecast)
        # For better covariance estimation, 10 years is good
        end_date = pd.Timestamp.today().strftime("%Y-%m-%d")
        start_date = (
            pd.Timestamp.today() - pd.DateOffset(years=historical_years)
        ).strftime("%Y-%m-%d")

        prices = get_stock_data(tickers, start_date, end_date)

        if prices.empty:
            st.error("No data found for the provided tickers.")
            st.stop()

        # Ensure we have all tickers
        missing_tickers = [t for t in tickers if t not in prices.columns]
        if missing_tickers:
            st.warning(
                f"Could not fetch data for: {', '.join(missing_tickers)}. Calculating with remaining assets."
            )
            # Adjust weights for missing assets
            valid_indices = [i for i, t in enumerate(tickers) if t in prices.columns]
            tickers = [tickers[i] for i in valid_indices]
            weights = [weights[i] for i in valid_indices]
            # Renormalize
            total_w = sum(weights)
            weights = [w / total_w for w in weights]

        if not tickers:
            st.error("No valid tickers remaining.")
            st.stop()

        # Check effective data range (intersection of all assets)
        valid_data = prices.dropna()
        if valid_data.empty:
            st.error(
                "No overlapping data found for the selected tickers. They may not have traded simultaneously."
            )
            st.stop()

        first_valid_date = pd.to_datetime(valid_data.index[0]).date()
        if first_valid_date > pd.to_datetime(start_date).date():
            st.info(
                f"⚠️ Simulation uses data starting from **{first_valid_date}** (limited by the asset with the shortest history)."
            )

        # 2. Run Simulation
        portfolio_paths = run_monte_carlo(
            prices, weights, forecast_years, n_simulations, initial_investment
        )

        # 3. Visualizations
        fig_line, fig_hist = plot_simulation_results(portfolio_paths)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_line, use_container_width=True)
        with col2:
            st.plotly_chart(fig_hist, use_container_width=True)

        # 4. Summary Statistics
        final_values = portfolio_paths[-1, :]
        mean_val = np.mean(final_values)
        median_val = np.median(final_values)
        p10 = np.percentile(final_values, 10)
        p90 = np.percentile(final_values, 90)

        # CAGR Calculation: (End/Start)^(1/n) - 1
        # Use the Median final value for a "typical" CAGR
        cagr = (median_val / initial_investment) ** (1 / forecast_years) - 1

        st.subheader("Summary Statistics")
        stats_col1, stats_col2, stats_col3, stats_col4, stats_col5 = st.columns(5)

        stats_col1.metric("Mean Final Value", f"${mean_val:,.2f}")
        stats_col2.metric("Median Final Value", f"${median_val:,.2f}")
        stats_col3.metric("10th Percentile (Risk)", f"${p10:,.2f}")
        stats_col4.metric("90th Percentile (Upside)", f"${p90:,.2f}")
        stats_col5.metric("Median CAGR", f"{cagr:.2%}")

        # --- Detailed Tables ---
        st.markdown("### Detailed Return Distribution")

        col_table1, col_table2 = st.columns(2)

        with col_table1:
            st.markdown("**Projected Portfolio Values**")
            percentiles = [10, 25, 50, 75, 90]
            perc_values = np.percentile(final_values, percentiles)

            df_percentiles = pd.DataFrame(
                {
                    "Percentile": [f"{p}th" for p in percentiles],
                    "Portfolio Value": [f"${v:,.2f}" for v in perc_values],
                    "Total Return": [
                        f"{(v / initial_investment - 1):.1%}" for v in perc_values
                    ],
                }
            )
            st.table(df_percentiles)

        with col_table2:
            st.markdown("**Probability of Success**")
            # Calculate probabilities
            prob_break_even = np.mean(final_values >= initial_investment)
            prob_double = np.mean(final_values >= initial_investment * 2)
            prob_triple = np.mean(final_values >= initial_investment * 3)

            df_probs = pd.DataFrame(
                {
                    "Scenario": [
                        "Break Even (> Initial)",
                        "Double Money (> 2x)",
                        "Triple Money (> 3x)",
                    ],
                    "Probability": [
                        f"{prob_break_even:.1%}",
                        f"{prob_double:.1%}",
                        f"{prob_triple:.1%}",
                    ],
                }
            )
            st.table(df_probs)

        with st.expander("Show Raw Data Head"):
            st.write(prices.head())
            st.caption(
                "Note: 'None' values indicate missing data for that date (e.g., company not yet public)."
            )

else:
    st.info("Adjust settings in the sidebar and click 'Run Simulation' to start.")
