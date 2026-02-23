import plotly.graph_objects as go
import numpy as np


def plot_simulation_results(portfolio_paths):
    """
    Creates Plotly charts for the simulation results.

    Args:
        portfolio_paths (np.array): Shape (steps, N_simulations).

    Returns:
        tuple: (fig_line, fig_hist)
    """

    # --- Line Chart ---
    # Downsample for performance if too many paths (e.g., show max 50)
    n_paths_to_plot = min(50, portfolio_paths.shape[1])
    # Ensure we don't error if n_paths_to_plot is 0 (unlikely given app constraints)
    if n_paths_to_plot > 0:
        indices = np.random.choice(
            portfolio_paths.shape[1], n_paths_to_plot, replace=False
        )
        subset_paths = portfolio_paths[:, indices]
    else:
        subset_paths = portfolio_paths

    fig_line = go.Figure()

    # X-axis is time steps
    x_axis = np.arange(subset_paths.shape[0])

    for i in range(subset_paths.shape[1]):
        fig_line.add_trace(
            go.Scatter(
                x=x_axis,
                y=subset_paths[:, i],
                mode="lines",
                opacity=0.5,
                name=f"Sim {i + 1}",
                showlegend=False,
            )
        )

    fig_line.update_layout(
        title="Monte Carlo Simulation Paths (Subset)",
        xaxis_title="Trading Days",
        yaxis_title="Portfolio Value ($)",
        template="plotly_white",
    )

    # --- Histogram ---
    final_values = portfolio_paths[-1, :]

    fig_hist = go.Figure()
    fig_hist.add_trace(
        go.Histogram(
            x=final_values,
            nbinsx=50,
            name="Final Values",
            marker_color="#1f77b4",
            opacity=0.75,
        )
    )

    # Calculate percentiles
    p10 = np.percentile(final_values, 10)
    p50 = np.percentile(final_values, 50)
    p90 = np.percentile(final_values, 90)

    # Add vertical lines without text annotations (to avoid overlap)
    fig_hist.add_vline(x=p10, line_dash="dash", line_color="red", annotation_text="")
    fig_hist.add_vline(x=p50, line_dash="solid", line_color="green", annotation_text="")
    fig_hist.add_vline(x=p90, line_dash="dash", line_color="red", annotation_text="")

    # Add a dummy scatter trace to create a custom legend for the lines
    fig_hist.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="red", dash="dash"),
            name="10th/90th Percentile",
        )
    )
    fig_hist.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="lines",
            line=dict(color="green", dash="solid"),
            name="Median",
        )
    )

    fig_hist.update_layout(
        title="Distribution of Final Portfolio Values",
        xaxis_title="Portfolio Value ($)",
        yaxis_title="Frequency",
        template="plotly_white",
        showlegend=True,  # Enable legend to show what lines mean
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return fig_line, fig_hist
