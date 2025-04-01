import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from matplotlib.widgets import Button # Import Button widget
import sys
import os # Add os import for directory creation
import os.path # Import for path manipulation
from tkinter import Tk, filedialog # Import for file dialog

# --- Configuration ---
PLOT_DIR = 'plots' # Directory to save plots
# Adjust these based on your data characteristics if needed
PEAK_PROMINENCE = 0.1 # How much a peak stands out from the surrounding baseline
PEAK_WIDTH = 1       # Minimum width of a peak

# --- Global Variables ---
data = None
data_filepath = None # Will be set after user selection at startup or via 'o'
current_row_index = 0
num_rows = 0
fig, ax = None, None
line = None
scatter_peaks = None
scatter_selected = None
selected_points = {'top': None, 'left': None, 'right': None}
results = {} # To store results for each row
current_x_data = None # Store x data for snapping
current_y_data = None # Store y data for snapping
peak_candidates = {} # To store peak candidates for each row

# --- Functions ---

def get_base_filename(filepath):
    """Extracts the base name of a file without extension."""
    if not filepath:
        return "unknown_file"
    base = os.path.basename(filepath)
    name, _ = os.path.splitext(base)
    # Sanitize the name for use in filenames
    safe_name = "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in name).rstrip()
    return safe_name

def load_data(filepath):
    """Loads data from the specified Excel or CSV file, skipping header and using the first column as index."""
    try:
        _, file_extension = os.path.splitext(filepath)
        file_extension = file_extension.lower()

        if file_extension in ['.xlsx', '.xls']:
            print(f"Loading Excel file: {filepath}")
            df = pd.read_excel(filepath, header=None, skiprows=1, index_col=0)
        elif file_extension == '.csv':
            print(f"Loading CSV file: {filepath}")
            # Try common encodings for CSV files
            encodings_to_try = ['utf-8', 'gbk', 'latin1'] # GBK is common in Chinese Windows environments
            df = None
            last_exception = None
            for encoding in encodings_to_try:
                try:
                    print(f"Attempting to read CSV with encoding: {encoding}")
                    # Adjust parameters if your CSV structure is different (e.g., separator, header row)
                    df = pd.read_csv(filepath, header=None, skiprows=1, index_col=0, encoding=encoding)
                    print(f"Successfully read CSV with encoding: {encoding}")
                    break # Exit loop if successful
                except UnicodeDecodeError as e:
                    print(f"Encoding {encoding} failed: {e}")
                    last_exception = e
                except Exception as e: # Catch other potential pandas errors
                    print(f"Error reading CSV with encoding {encoding}: {e}")
                    last_exception = e
                    # Decide if you want to break on other errors or try next encoding
                    # break # Uncomment to stop on first non-Unicode error

            if df is None:
                print(f"Error: Could not read CSV file '{filepath}' with any attempted encoding.")
                if last_exception:
                    print(f"Last error encountered: {last_exception}")
                return None # Return None if all encodings failed
        else:
            print(f"Error: Unsupported file type '{file_extension}'. Please select an Excel (.xlsx, .xls) or CSV (.csv) file.")
            return None # Return None for unsupported types

        # Convert to numeric, coercing errors
        df = df.apply(pd.to_numeric, errors='coerce')
        # Drop rows/columns that are entirely NaN after coercion if necessary
        df.dropna(axis=0, how='all', inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        print(f"Loaded data with shape: {df.shape}")
        return df
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None # Return None on file not found
    except Exception as e:
        print(f"Error loading data file '{filepath}': {e}")
        return None # Return None on other errors

def find_potential_peaks(y_data):
    """Finds potential peaks in the data."""
    # Ensure data is numpy array
    y_data_np = np.array(y_data)
    # Handle NaN values if any - replace with interpolation or a constant (e.g., 0 or mean)
    nan_mask = np.isnan(y_data_np)
    if np.any(nan_mask):
        print(f"Warning: NaN values found in row {current_row_index}. Replacing with 0 for peak finding.")
        y_data_np[nan_mask] = 0 # Simple replacement, consider interpolation for better results

    peaks, properties = find_peaks(y_data_np, prominence=PEAK_PROMINENCE, width=PEAK_WIDTH)
    print(f"Found {len(peaks)} potential peaks in row {current_row_index}.")
    return peaks, properties

def update_plot():
    """Updates the plot for the current row."""
    global scatter_peaks

    if data is None or data.empty or current_row_index >= len(data):
        ax.clear()
        ax.set_title("No data loaded or invalid row index")
        ax.text(0.5, 0.5, "Load a valid data file (Excel/CSV)", ha='center', va='center', transform=ax.transAxes)
        fig.canvas.draw_idle()
        return

    # Get current row data
    row_data = data.iloc[current_row_index]
    x_data = row_data.index.values
    y_data = row_data.values

    # Get row label for display
    row_label = data.index[current_row_index]

    # Clear the plot
    ax.clear()

    # Plot the data
    ax.plot(x_data, y_data, 'b-', linewidth=1)

    # Find peaks if not already stored
    if current_row_index not in peak_candidates:
        peaks, _ = find_peaks(y_data, prominence=PEAK_PROMINENCE, width=PEAK_WIDTH)
        peak_candidates[current_row_index] = [(x_data[p], y_data[p]) for p in peaks]
        print(f"Found {len(peaks)} potential peaks in row {row_label}.")

    # Plot peak candidates
    peak_x = [p[0] for p in peak_candidates[current_row_index]]
    peak_y = [p[1] for p in peak_candidates[current_row_index]]
    scatter_peaks = ax.scatter(peak_x, peak_y, color='green', s=50, alpha=0.5)

    # Get current selections for this row
    current_selections = results[current_row_index]

    # Plot current selections if they exist
    points_to_plot = []
    if current_selections['left']:
        points_to_plot.append(('left', current_selections['left'], 'red'))
    if current_selections['top']:
        points_to_plot.append(('top', current_selections['top'], 'blue'))
    if current_selections['right']:
        points_to_plot.append(('right', current_selections['right'], 'purple'))

    # If there are selected points to plot
    if points_to_plot:
        for label, point, color in points_to_plot:
            ax.scatter(point[0], point[1], color=color, s=100)
            ax.annotate(f"{label.upper()}: ({point[0]:.2f}, {point[1]:.2f})",
                       (point[0], point[1]),
                       xytext=(10, 10), textcoords='offset points',
                       color=color, fontweight='bold')

    # Set title and labels
    ax.set_title(f'Row: {row_label} - Click to select LEFT, TOP, RIGHT points in order')
    ax.set_xlabel('X Values')
    ax.set_ylabel('Y Values')
    ax.grid(True)

    # Add coordinates text box
    coord_text = f"Row: {row_label}\n"
    if current_selections['left']:
        x, y = current_selections['left']
        coord_text += f"LEFT: ({x:.2f}, {y:.2f})\n"
    if current_selections['top']:
        x, y = current_selections['top']
        coord_text += f"TOP: ({x:.2f}, {y:.2f})\n"
    if current_selections['right']:
        x, y = current_selections['right']
        coord_text += f"RIGHT: ({x:.2f}, {y:.2f})"

    # Add text box with coordinates
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    ax.text(0.02, 0.98, coord_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    # Update the figure
    fig.canvas.draw_idle()

def on_click(event):
    """Handles mouse clicks for point selection."""
    if event.inaxes != ax or data is None or data.empty:  # Ignore clicks outside plot or if no data
        return

    # Get current row data
    row_data = data.iloc[current_row_index]
    x_data = row_data.index.values
    y_data = row_data.values

    # Find the closest actual data point to where the user clicked
    distances = [(x - event.xdata)**2 + (y - event.ydata)**2 for x, y in zip(x_data, y_data)]
    closest_idx = np.argmin(distances)
    closest_x = x_data[closest_idx]
    closest_y = y_data[closest_idx]

    # Get the current selections for this row
    current_selections = results[current_row_index]

    # Determine which point type to set next
    if current_selections['left'] is None:
        point_type = 'left'
        color = 'red'
    elif current_selections['top'] is None:
        point_type = 'top'
        color = 'blue'
    elif current_selections['right'] is None:
        point_type = 'right'
        color = 'purple'
    else:
        # If all points are already set, reset them
        results[current_row_index] = {'left': None, 'top': None, 'right': None}
        update_plot()  # Redraw the plot
        return

    # Store the selected point (using the closest actual data point)
    results[current_row_index][point_type] = (closest_x, closest_y)
    print(f"Selected {point_type.upper()} point at ({closest_x:.4f}, {closest_y:.4f})")

    # Update the plot to show the selection
    update_plot()

    # If this completes a set, provide feedback
    if point_type == 'right':
        print(f"All points selected for row {data.index[current_row_index]}.")

def on_key(event):
    """Handles key presses for navigation and manual input."""
    global current_row_index

    if data is None or data.empty: # Don't process keys if no data
        print("No data loaded, cannot process key events.")
        return

    print(f"Key pressed: '{event.key}'") # DEBUG: Print the detected key

    if event.key == 'right':
        current_row_index = (current_row_index + 1) % num_rows
        print(f"Navigating to next row: {data.index[current_row_index]}")
        update_plot()
    elif event.key == 'left':
        current_row_index = (current_row_index - 1 + num_rows) % num_rows
        print(f"Navigating to previous row: {data.index[current_row_index]}")
        update_plot()
    elif event.key == 'm': # Manual input
        manual_input()
    elif event.key == 'c': # Clear selection for current row
        clear_selection()
    elif event.key == 's': # Save results
        save_results()
    elif event.key == 'o': # Open new file
        change_data_file()
    elif event.key == 'p': # 保存当前图表
        save_plot()
    elif event.key == 'a': # 保存所有图表
        save_all_plots()

def clear_selection():
    """Clears the selection for the current row."""
    global selected_points, scatter_selected
    if data is None or data.empty:
        print("No data loaded, cannot clear selection.")
        return
    print(f"Clearing selection for row {data.index[current_row_index]}")
    selected_points = {'top': None, 'left': None, 'right': None}
    results[current_row_index] = selected_points # Update stored results
    # Re-draw plot to remove points visually
    update_plot()

def manual_input():
    """Allows manual input of coordinates via the console."""
    global selected_points
    if data is None or data.empty:
        print("No data loaded, cannot perform manual input.")
        return

    print("\n--- Manual Input ---")
    print("Enter coordinates as 'x,y' or leave blank to skip.")

    try:
        top_str = input("Enter TOP coordinates (x,y): ")
        if top_str:
            x_str, y_str = top_str.split(',')
            selected_points['top'] = (float(x_str.strip()), float(y_str.strip()))

        left_str = input("Enter LEFT coordinates (x,y): ")
        if left_str:
            x_str, y_str = left_str.split(',')
            selected_points['left'] = (float(x_str.strip()), float(y_str.strip()))

        right_str = input("Enter RIGHT coordinates (x,y): ")
        if right_str:
            x_str, y_str = right_str.split(',')
            selected_points['right'] = (float(x_str.strip()), float(y_str.strip()))

        print("Manual input complete.")
        results[current_row_index] = selected_points # Store selection
        update_plot()

    except ValueError:
        print("Invalid input format. Please use 'x,y'. Try again.")
    except Exception as e:
        print(f"An error occurred during manual input: {e}")

def save_results():
    """Saves the selected peak data to a CSV file named after the input file."""
    global data_filepath # Ensure we are using the global variable

    if not data_filepath:
        print("Error: No data file loaded. Cannot save results.")
        return
    if data is None or data.empty:
        print("Error: No data loaded. Cannot save results.")
        return

    base_name = get_base_filename(data_filepath)
    output_filename = f"{base_name}_peak_results.csv"

    print(f"\nSaving results to {output_filename}...")
    output_data = []
    for row_idx, points in results.items():
        # Ensure row_idx is valid before accessing data.index
        if row_idx < len(data):
            row_label = data.index[row_idx]
            output_data.append({
                'RowLabel': row_label,
                'Left_X': points['left'][0] if points['left'] else None,
                'Left_Y': points['left'][1] if points['left'] else None,
                'Top_X': points['top'][0] if points['top'] else None,
                'Top_Y': points['top'][1] if points['top'] else None,
                'Right_X': points['right'][0] if points['right'] else None,
                'Right_Y': points['right'][1] if points['right'] else None,
            })
        else:
             print(f"Warning: Skipping invalid row index {row_idx} during save.")


    results_df = pd.DataFrame(output_data)
    try:
        results_df.to_csv(output_filename, index=False)
        print(f"Results saved successfully to {output_filename}.")

        # 同时保存当前行的图表, 传递文件名基础部分
        print(f"Saving plot for current row {data.index[current_row_index]}...")
        save_plot(filename_prefix=base_name) # Pass the base name

    except Exception as e:
        print(f"Error saving results or plot: {e}")

def prev_row_button_clicked(event):
    """Navigate to the previous row"""
    global current_row_index
    if data is None or data.empty: return
    current_row_index = (current_row_index - 1 + num_rows) % num_rows
    print(f"Navigating to previous row: {data.index[current_row_index]}")
    update_plot()

def next_row_button_clicked(event):
    """Navigate to the next row"""
    global current_row_index
    if data is None or data.empty: return
    current_row_index = (current_row_index + 1) % num_rows
    print(f"Navigating to next row: {data.index[current_row_index]}")
    update_plot()

def save_button_clicked(event):
    """Callback for save button"""
    save_results()

def switch_file_button_clicked(event):
    """Callback for switch file button"""
    change_data_file()

def change_data_file():
    """Allow user to select a new data file (Excel or CSV)"""
    global data, data_filepath, current_row_index, num_rows, results, peak_candidates

    try:
        root = Tk()
        root.withdraw()  # Hide main window
        new_file = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("Supported Files", "*.xlsx *.xls *.csv"),
                       ("Excel files", "*.xlsx *.xls"),
                       ("CSV files", "*.csv"),
                       ("All files", "*.*")]
        )
        root.destroy()

        if not new_file:  # User canceled
            print("No new file selected, continuing with current file.")
            return

        print(f"Attempting to load new file: {new_file}")
        new_data = load_data(new_file) # Load the new data

        if new_data is None or new_data.empty:
            print("Error: Failed to load the selected file or file is empty. Keeping previous data.")
            # Optionally, show an error message to the user in the plot window
            ax.clear()
            ax.set_title("Error Loading File")
            ax.text(0.5, 0.5, f"Could not load:\n{os.path.basename(new_file)}\n\nPlease check the file format and content.", ha='center', va='center', transform=ax.transAxes, color='red')
            fig.canvas.draw_idle()
            return # Stop further processing in this function if load failed
        else:
            # Reset data and results
            data = new_data # Assign the successfully loaded data
            data_filepath = new_file # Update the global filepath
            num_rows = data.shape[0]
            current_row_index = 0
            # Initialize results dictionary for the new data size
            results = {i: {'top': None, 'left': None, 'right': None} for i in range(num_rows)}
            peak_candidates.clear() # Clear peak candidates for new file
            update_plot() # Update plot with the first row of new data
            print(f"Successfully loaded new data file '{data_filepath}' with {num_rows} rows.")

    except Exception as e:
        print(f"Error changing data file: {e}")

def save_plot(row_idx=None, filename_prefix=None):
    """保存当前图表为图片文件到 'plots' 文件夹, 文件名包含来源文件和行标签"""
    global data_filepath # Needed if prefix is not provided

    if data is None or data.empty:
        print("Error: No data loaded, cannot save plot.")
        return

    if row_idx is None:
        row_idx = current_row_index

    # 如果未提供前缀，则从全局 data_filepath 生成
    if filename_prefix is None:
        if not data_filepath:
            print("Error: Cannot determine filename prefix, no file loaded.")
            return
        filename_prefix = get_base_filename(data_filepath)

    # 确保 row_idx 有效
    if row_idx >= len(data):
         print(f"Error: Invalid row index ({row_idx}) for saving plot.")
         return

    row_label = data.index[row_idx]

    # Create the plots directory if it doesn't exist
    if not os.path.exists(PLOT_DIR):
        try:
            os.makedirs(PLOT_DIR)
            print(f"Created directory: {PLOT_DIR}")
        except OSError as e:
            print(f"Error creating directory {PLOT_DIR}: {e}")
            return # Exit if directory creation fails

    # 使用来源文件前缀和行标签作为文件名一部分, 并加入目录路径
    # Ensure row_label is safe for filenames
    safe_row_label = "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in str(row_label)).rstrip()
    filename = f"{filename_prefix}_peak_plot_{safe_row_label}.png"
    filepath = os.path.join(PLOT_DIR, filename)

    try:
        # 保存当前图表
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"图表已保存至：{filepath}")
    except Exception as e:
        print(f"保存图表时出错 ({filepath}): {e}")

def save_all_plots():
    """保存所有行的图表到 'plots' 文件夹, 文件名包含来源文件"""
    global data_filepath # Ensure we are using the global variable
    current_idx = current_row_index  # 保存当前位置

    if not data_filepath:
        print("Error: No data file loaded. Cannot save all plots.")
        return
    if data is None or data.empty:
        print("Error: No data loaded. Cannot save all plots.")
        return

    base_name = get_base_filename(data_filepath)
    print(f"\nAttempting to save all {num_rows} plots for '{base_name}' to '{PLOT_DIR}' directory...")
    saved_count = 0
    error_count = 0
    try:
        # 遍历所有行并保存
        for idx in range(num_rows):
            current_row_index = idx
            update_plot()  # 更新为当前行的图表
            # Add a small pause for the plot to potentially render if needed, though usually not necessary for saving
            # plt.pause(0.01)
            try:
                save_plot(idx, filename_prefix=base_name) # Pass the base name
                saved_count += 1
            except Exception as plot_e:
                print(f"Error saving plot for row {data.index[idx]}: {plot_e}")
                error_count += 1

        print(f"Finished saving plots: {saved_count} saved, {error_count} errors. Files saved to '{PLOT_DIR}' directory.")
    except Exception as e:
        print(f"保存所有图表时发生意外错误：{e}")
    finally:
        # 恢复原来的位置
        current_row_index = current_idx
        update_plot()

# --- Main Execution ---
if __name__ == "__main__":
    # Ensure the plot directory exists at startup as well
    if not os.path.exists(PLOT_DIR):
        try:
            os.makedirs(PLOT_DIR)
            print(f"Created directory: {PLOT_DIR}")
        except OSError as e:
            print(f"Error creating directory {PLOT_DIR} at startup: {e}")
            # Decide if you want to exit or continue without saving plots
            # sys.exit(1)

    # --- Ask user for the initial file ---
    root = Tk()
    root.withdraw() # Hide the main Tk window
    initial_file = filedialog.askopenfilename(
        title="Select Initial Data File",
        filetypes=[("Supported Files", "*.xlsx *.xls *.csv"),
                   ("Excel files", "*.xlsx *.xls"),
                   ("CSV files", "*.csv"),
                   ("All files", "*.*")]
    )
    root.destroy()

    if not initial_file:
        print("No file selected. Exiting program.")
        sys.exit(0)

    data_filepath = initial_file # Set the global variable
    print(f"Loading initial file: {data_filepath}")
    data = load_data(data_filepath) # Use the updated global variable

    if data is None or data.empty:
        print("Failed to load initial data file or file is empty. Exiting program.")
        # Maybe show a simple Tkinter error message box here?
        sys.exit(1)

    num_rows = data.shape[0]

    # Initialize results dictionary
    results = {i: {'top': None, 'left': None, 'right': None} for i in range(num_rows)}

    # Create plot - adjust layout to make space for buttons
    fig, ax = plt.subplots(figsize=(12, 7)) # Increased height slightly
    plt.subplots_adjust(bottom=0.2) # Increase bottom margin for buttons

    # Initialize plot elements that will be updated
    scatter_peaks = None

    # Connect event handlers
    fig.canvas.mpl_connect('button_press_event', on_click)
    fig.canvas.mpl_connect('key_press_event', on_key)

    # Initial plot
    update_plot()

    print("\n--- INSTRUCTIONS ---")
    print(" - LEFT/RIGHT arrow keys: Navigate between rows (ensure plot window has focus).")
    print(" - Mouse clicks: Select LEFT point first, then TOP point, then RIGHT point.")
    print("   (Clicking again after RIGHT will reset selection for current row).")
    print(" - 'm' key: Enter manual input mode in console.")
    print(" - 'c' key: Clear selection for current row.")
    print(" - 's' key or Save button: Save all collected results to a CSV file named after the input file.")
    print(" - 'o' key or Switch File button: Open a new data file (Excel or CSV).")
    print(f" - 'p' key or Save Plot button: Save current plot as image to '{PLOT_DIR}' folder.")
    print(f" - 'a' key: Save all plots as images to '{PLOT_DIR}' folder.")
    print(" - Close the plot window to exit the program.")
    print("---------------------")

    # Add navigation buttons
    ax_prev_button = plt.axes([0.25, 0.025, 0.15, 0.06]) # Position: [left, bottom, width, height]
    prev_btn = Button(ax_prev_button, 'Previous Row ←')
    prev_btn.on_clicked(prev_row_button_clicked)

    ax_next_button = plt.axes([0.45, 0.025, 0.15, 0.06])
    next_btn = Button(ax_next_button, 'Next Row →')
    next_btn.on_clicked(next_row_button_clicked)

    # Add other buttons with adjusted positions
    ax_save_button = plt.axes([0.8, 0.025, 0.15, 0.06])
    save_btn = Button(ax_save_button, 'Save Results')
    save_btn.on_clicked(save_button_clicked)

    ax_switch_button = plt.axes([0.65, 0.025, 0.15, 0.06])
    switch_btn = Button(ax_switch_button, 'Switch File')
    switch_btn.on_clicked(switch_file_button_clicked)

    # 添加保存图表按钮
    ax_save_plot_button = plt.axes([0.05, 0.025, 0.15, 0.06])
    save_plot_btn = Button(ax_save_plot_button, 'Save Plot')
    # 修改保存图表按钮的回调，使其也使用正确的文件名逻辑
    save_plot_btn.on_clicked(lambda event: save_plot()) # save_plot now handles prefix internally if needed

    plt.show()

    print("\nProgram exited.")
