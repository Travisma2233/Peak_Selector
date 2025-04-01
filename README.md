# 📈 Peak Selector Tool | 峰值选择工具 📉

This Python script provides an interactive graphical interface for selecting characteristic points (Left, Top, Right) of peaks from data series loaded from Excel or CSV files.

这是一个 Python 脚本，提供了一个交互式图形界面，用于从 Excel 或 CSV 文件加载的数据系列中选择峰值的特征点（左侧、顶部、右侧）。

---

![Profile](https://github.com/user-attachments/assets/794ec02b-3d9f-4236-8313-e1fd09469d72)


## ✨ Features | 功能 ✨

*   **Interactive Plotting:** Visualizes data row by row using Matplotlib. 📊
    **交互式绘图：** 使用 Matplotlib 逐行可视化数据。📊
*   **File Support:** Loads data from Excel (`.xlsx`, `.xls`) and CSV (`.csv`) files. Handles common CSV encodings (UTF-8, GBK, Latin1). 📄
    **文件支持：** 从 Excel (`.xlsx`, `.xls`) 和 CSV (`.csv`) 文件加载数据。支持常见的 CSV 编码（UTF-8, GBK, Latin1）。📄
*   **Peak Candidate Highlighting:** Automatically detects and highlights potential peaks using `scipy.signal.find_peaks`. 🟢
    **候选峰值高亮：** 使用 `scipy.signal.find_peaks` 自动检测并高亮显示潜在的峰值。🟢
*   **Point Selection:**
    *   **Mouse Click:** Select Left (🔴), Top (🔵), and Right (🟣) points by clicking near them on the plot. The closest actual data point is selected.
    *   **Manual Input:** Enter coordinates directly via the console (`m` key).
    **点选择：**
    *   **鼠标点击：** 通过在图上点击选择左侧 (🔴)、顶部 (🔵) 和右侧 (🟣) 点。脚本会自动选择距离点击位置最近的实际数据点。
    *   **手动输入：** 通过控制台直接输入坐标（按 `m` 键）。
*   **Navigation:** Easily navigate between data rows using arrow keys or dedicated buttons. ⬅️➡️
    **导航：** 使用键盘方向键或专用按钮轻松在数据行之间切换。⬅️➡️
*   **Data Saving:** Save the selected coordinates for all rows to a CSV file (`<input_filename>_peak_results.csv`). 💾
    **数据保存：** 将所有行选择的坐标保存到 CSV 文件 (`<输入文件名>_peak_results.csv`)。💾
*   **Plot Saving:**
    *   Save the plot of the current row as a PNG image (`p` key or button). 🖼️
    *   Save plots for all rows as PNG images (`a` key). 📚
    **绘图保存：**
    *   将当前行的绘图保存为 PNG 图片（按 `p` 键或按钮）。🖼️
    *   将所有行的绘图保存为 PNG 图片（按 `a` 键）。📚
*   **File Switching:** Switch to a different data file during runtime (`o` key or button). 🔄
    **文件切换：** 在运行时切换到不同的数据文件（按 `o` 键或按钮）。🔄
*   **Clear Selection:** Clear the selected points for the current row (`c` key). ❌
    **清除选择：** 清除当前行的选定点（按 `c` 键）。❌

---

## ⚙️ Requirements | 依赖项 ⚙️

*   Python 3.x
*   Libraries:
    *   `matplotlib`
    *   `pandas`
    *   `numpy`
    *   `scipy`
    *   `openpyxl` (for `.xlsx` files)
    *   `xlrd` (for `.xls` files)
    *   `tkinter` (usually included with Python standard library)

You can install the required libraries using pip:
```bash
pip install matplotlib pandas numpy scipy openpyxl xlrd
```
你可以使用 pip 安装所需的库：
```bash
pip install matplotlib pandas numpy scipy openpyxl xlrd
```

---

## 🚀 How to Use | 如何使用 🚀

1.  **Run the script:**
    ```bash
    python peak_selector.py
    ```
    **运行脚本：**
    ```bash
    python peak_selector.py
    ```
2.  **Select File:** A file dialog will appear. Choose the Excel or CSV file containing your data.
    *   The data should be structured with sample identifiers/labels in the first column and measurements across the subsequent columns.
    *   The script assumes the first row is a header and skips it.
    **选择文件：** 会弹出一个文件对话框。选择包含数据的 Excel 或 CSV 文件。
    *   数据结构应为：第一列是样本标识符/标签，后续列是测量值。
    *   脚本假定第一行是表头并会跳过它。
3.  **Interact with the Plot:**
    *   Use **Left/Right arrow keys** or the **"Previous Row" / "Next Row" buttons** to navigate.
    *   **Click** on the plot to select the **Left**, then **Top**, then **Right** points for the current peak. Click again after selecting 'Right' to reset the selection for the current row.
    *   Press **`c`** to clear the current selection.
    *   Press **`m`** to enter coordinates manually in the console.
    **与绘图交互：**
    *   使用 **左/右方向键** 或 **"Previous Row" / "Next Row" 按钮** 进行导航。
    *   在图上 **点击** 以选择当前峰值的 **左侧**、**顶部**、**右侧** 点。选择“右侧”点后再次点击将重置当前行的选择。
    *   按 **`c`** 键清除当前选择。
    *   按 **`m`** 键在控制台手动输入坐标。
4.  **Save Data/Plots:**
    *   Press **`s`** or click the **"Save Results" button** to save all selected coordinates to `<input_filename>_peak_results.csv`.
    *   Press **`p`** or click the **"Save Plot" button** to save the current plot to the `plots/` directory.
    *   Press **`a`** to save plots for all rows to the `plots/` directory.
    **保存数据/绘图：**
    *   按 **`s`** 键或点击 **"Save Results" 按钮** 将所有选定的坐标保存到 `<输入文件名>_peak_results.csv`。
    *   按 **`p`** 键或点击 **"Save Plot" 按钮** 将当前绘图保存到 `plots/` 目录。
    *   按 **`a`** 键将所有行的绘图保存到 `plots/` 目录。
5.  **Switch File:** Press **`o`** or click the **"Switch File" button** to load a new data file.
    **切换文件：** 按 **`o`** 键或点击 **"Switch File" 按钮** 加载新的数据文件。
6.  **Exit:** Close the plot window to exit the program.
    **退出：** 关闭绘图窗口以退出程序。

---

## 🔧 Configuration | 配置 🔧

You can adjust the following parameters at the beginning of the `peak_selector.py` script:

*   `PLOT_DIR`: The directory where plot images are saved (default: `'plots'`).
*   `PEAK_PROMINENCE`: Controls how much a peak must stand out vertically (default: `0.1`).
*   `PEAK_WIDTH`: The minimum required width of a peak (default: `1`).

你可以在 `peak_selector.py` 脚本的开头调整以下参数：

*   `PLOT_DIR`: 保存绘图图片的目录（默认为：`'plots'`）。
*   `PEAK_PROMINENCE`: 控制峰值需要垂直突出的程度（默认为：`0.1`）。
*   `PEAK_WIDTH`: 峰值所需的最小宽度（默认为：`1`）。

---

## 📝 Notes | 注意事项 📝

*   Ensure your data file is correctly formatted. Errors during loading will be printed to the console.
    请确保你的数据文件格式正确。加载过程中的错误将打印到控制台。
*   The `plots/` directory will be created automatically if it doesn't exist.
    如果 `plots/` 目录不存在，脚本会自动创建。
*   For keyboard shortcuts to work, the plot window must have focus.
    要使键盘快捷键生效，绘图窗口必须处于活动状态（获得焦点）。
