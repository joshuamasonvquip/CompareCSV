import csv
import sys

# Path to the CSV file
CSV_PATH = 'all-deals.csv'

# Column name for unique identifier
DEAL_NAME_COL = 'Deal Name'

def load_existing_deal_names(csv_path=CSV_PATH):
    """
    Loads all unique 'Deal Name' values from the CSV into a set.
    Returns the set of deal names (stripped and lowercased for normalization).
    """
    deal_names = set()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')  # Tab-delimited
        for row in reader:
            deal_name = row.get(DEAL_NAME_COL)
            if deal_name:
                deal_names.add(deal_name.strip().lower())
    return deal_names

def is_new_lead(deal_name, existing_deal_names):
    """
    Checks if the given deal_name is new (not in existing_deal_names set).
    """
    return deal_name.strip().lower() not in existing_deal_names

def check_new_leads(new_leads_csv, existing_deal_names):
    """
    Reads new leads from a CSV and prints whether each is new or a duplicate.
    """
    with open(new_leads_csv, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            deal_name = row.get(DEAL_NAME_COL)
            if not deal_name:
                continue
            if is_new_lead(deal_name, existing_deal_names):
                print(f"New lead: {deal_name}")
            else:
                print(f"Duplicate: {deal_name}")

if __name__ == '__main__':
    # Load all existing deal names
    existing_deal_names = load_existing_deal_names()

    if len(sys.argv) < 2:
        print("Usage: python cross_reference_leads.py <new-leads.csv>")
        sys.exit(1)

    new_leads_csv = sys.argv[1]
    check_new_leads(new_leads_csv, existing_deal_names) 