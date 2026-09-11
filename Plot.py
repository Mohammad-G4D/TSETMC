import matplotlib.pyplot as plt


def Walk_Forward_Plot(dates_8_days, actual_prices, pred_prices, current_date):
    """
    Visualizes the 7-day walk-forward forecast compared to actual closing prices.
    """
    
    # Create a figure and axis with a defined size for the plot
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Plot the actual closing prices with circular markers
    ax.plot(dates_8_days, actual_prices, marker='o', color='#1f77b4', label='Actual priceClosing', linewidth=2)
    
    # Plot the 7-day predicted prices with a dashed line and square markers
    ax.plot(dates_8_days, pred_prices, marker='s', linestyle='--', color='#2ca02c', label='7-Day Prediction', linewidth=2)

    # Set the title showing the current base date and rotate x-axis labels for readability
    ax.set_title(f"Base Date: {current_date}", fontsize=12)
    ax.tick_params(axis='x', rotation=45)

    # Add a subtle grid, legend, and optimize element layouts
    ax.grid(True, alpha=0.3)
    ax.legend()
    plt.tight_layout()
    
    # Draw the plot, pause briefly for real-time interactive updates, and display it
    plt.draw()
    plt.pause(1.0)
    plt.show()