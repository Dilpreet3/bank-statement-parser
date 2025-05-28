import re

def parse_bank_statement(text):
    """
    Parses Indian bank statement format from raw text.
    
    Matches lines like:
    | 1.|19-FEB-25|UPI/...|15,400.00|Cr|
    
    Returns a list of dictionaries with:
    - Date
    - Description
    - Debit / Credit
    """

    # Improved regex to handle inconsistent spacing in table
    pattern = re.compile(
        r'\| *(\d+\.) *\| *([\d\-A-Z]+) *\| *(.+?) *\| *([\d,]+\.\d{2}) *\| *([CD]r) *\|',
        re.IGNORECASE
    )

    transactions = []
    matches = pattern.findall(text)

    print(f"[DEBUG] Found {len(matches)} matches")  # Log how many rows were matched

    for sr, date, desc, amount, ttype in matches:
        try:
            amount_clean = float(amount.replace(',', ''))
            transactions.append({
                'Date': date,
                'Description': desc.strip(),
                'Debit': amount_clean if ttype == 'Dr' else '',
                'Credit': amount_clean if ttype == 'Cr' else ''
            })
        except Exception as e:
            print(f"[ERROR] Failed to parse row: {e}")

    return transactions
