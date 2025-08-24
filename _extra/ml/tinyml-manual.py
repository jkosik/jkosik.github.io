import math
import matplotlib.pyplot as plt

# Training data (optimal outcome: y=2x-1)
x = [-1.0, 0.0, 1.0, 2.0, 3.0, 4.0] # input
y = [-3.0, -1.0, 1.0, 3.0, 5.0, 7.0] # ground truth output

# Guess the model (y=x * w + b)
w = 3
b = 1

# Make a prediction
y_pred = []

for x_val in x:
    y_guess = x_val * w + b
    y_pred.append(y_guess)

print("Ground truth:", y)
print("Prediction:", y_pred)

# Calculate individual losses and overall loss using RMSE (Root Mean Squared Error).
individual_losses = []
print("\nIndividual Losses (Squared Errors):")
for i in range(len(x)):
    error = y_pred[i] - y[i]
    squared_error = error ** 2
    individual_losses.append(squared_error)

print(individual_losses)

# Calculate overall loss (Root Mean Squared Error)
mse = sum(individual_losses) / len(individual_losses)
rmse = math.sqrt(mse)
print(f"\nOverall Loss (Root Mean Squared Error): {rmse:.2f}")


# Plot with annotations
plt.figure(figsize=(10, 6))
plt.scatter(x, y, color='blue', label='Ground Truth', s=100, zorder=3)
plt.scatter(x, y_pred, color='red', label='Prediction', s=100, marker='x', zorder=3)
plt.vlines(x, y, y_pred, color='green', linestyle='--', alpha=0.7, linewidth=2, label='Error', zorder=1)

# Add title and axis labels
plt.title('Manual Linear Model: Ground Truth vs Prediction', fontsize=16, fontweight='bold')
plt.xlabel('Input (x)', fontsize=12)
plt.ylabel('Output (y)', fontsize=12)

# Add grid
plt.grid(True, alpha=0.3, linestyle=':')

# Add legend
plt.legend(fontsize=12)

# Annotate each point with its values
for i in range(len(x)):
    error = y_pred[i] - y[i]
    # Annotate ground truth points
    plt.annotate(f'({x[i]}, {y[i]})',
                xy=(x[i], y[i]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=9,
                color='blue',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.7))

    # Annotate error in the middle of each line
    mid_y = (y[i] + y_pred[i]) / 2
    plt.annotate(f'err: {error:+.1f}',
                xy=(x[i], mid_y),
                xytext=(10, 0),
                textcoords='offset points',
                fontsize=8,
                color='green',
                ha='left',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='lightgreen', alpha=0.6))

# Add model equation as text
plt.text(0.02, 0.98, f'Model: y = {w}x + {b}',
         transform=plt.gca().transAxes,
         fontsize=12,
         verticalalignment='top',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.8))

# Add error statistics
differences = [y_pred[i] - y[i] for i in range(len(x))]
mse_plot = sum(error**2 for error in differences) / len(differences)
rmse_plot = math.sqrt(mse_plot)

plt.text(0.02, 0.85, f'RMSE: {rmse_plot:.2f}',
         transform=plt.gca().transAxes,
         fontsize=11,
         bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7))

plt.tight_layout()
plt.show()