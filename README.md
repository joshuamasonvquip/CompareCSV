# Lead Cross-Reference Tool

This is a simple web app for comparing new leads against your existing deals to identify duplicates. It is built with Flask and allows you to upload two CSV files:

- **Existing Deals** (`all_deals.csv`): This file should be exported from HubSpot and contains your current deals.
- **New Leads** (`new_leads.csv`): This file contains the new leads you want to check for duplicates.

## Features
- Upload and select which columns to compare from each file
- See which new leads are duplicates or unique
- Export results as CSV (new leads, duplicates, or filtered full rows)

## Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/joshuamasonvquip/CompareCSV.git
   cd CompareCSV
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open your browser to [http://localhost:5000](http://localhost:5000)

## Usage
1. Export your deals from HubSpot as a CSV (this will be your **Existing Deals** file).
2. Prepare your new leads CSV.
3. Upload both files in the app, select the columns to compare, and view/export the results.

## Notes
- Only standard comma-delimited CSV files are supported.
- No data is stored on the server after processing.

---

Feel free to contribute or open issues for improvements! 