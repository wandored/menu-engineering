# Code Documentation

This repository contains a Python script that imports sales mix and exports a menu engineering report to an Excel file.

## Prerequisites
- Python 3.x
- pandas library
- tkinter library (usually included with Python installations)
- numpy library

## Usage
1. Clone the repository to your local machine or download the script file.
2. Install the required dependencies (`pandas` and `numpy`) if you haven't already done so. You can install them using `pip`:

```
pip install pandas numpy
```

3. Update the file paths for the input CSV files in the `upload_product_mix` and `upload_menu_price_analysis` functions. Replace the `file_path` variables with the correct paths to your CSV files.
4. Run the script using Python:

```
python script.py
```

5. The script will prompt you to select the sorting criteria for the menu items (profit or quantity). Enter your choice in the tkinter window that appears.
6. The script will generate an Excel file for each location in the provided input CSV files. The Excel files will be saved in the specified output directory with the location name as the filename.

Note: The script includes some commented out code related to file dialogs for selecting input files. If you prefer to use file dialogs instead of specifying file paths directly in the code, you can uncomment and modify the relevant sections of the code accordingly.

## License
This code is released under the [MIT License](LICENSE).
