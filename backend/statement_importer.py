
import pymupdf
import re
import pandas as pd
from datetime import datetime


def import_gpay_pdf(pdf_path):
    transactions = []

    # Read the PDF from a file path or file-like object.
    if hasattr(pdf_path, "read"):
        pdf_bytes = pdf_path.read()
        document = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    else:
        document = pymupdf.open(pdf_path)

    with document:
        text = "\n".join(page.get_text() for page in document)

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    date_pattern = re.compile(r"^\d{1,2}\s+[A-Za-z]{3},\s+\d{4}$")
    time_pattern = re.compile(r"^\d{1,2}:\d{2}\s+(AM|PM)$", re.I)
    amount_pattern = re.compile(r"^₹\s*[\d,]+(?:\.\d{1,2})?$")

    i = 0

    while i < len(lines):
        if not date_pattern.match(lines[i]):
            i += 1
            continue

        date_text = lines[i]
        i += 1

        if i >= len(lines) or not time_pattern.match(lines[i]):
            continue

        i += 1  # Skip transaction time

        description = ""
        amount = None
        transaction_type = None

        while i < len(lines) and not date_pattern.match(lines[i]):
            line = lines[i]

            if line.lower().startswith("paid to "):
                description = line[8:].strip()
                transaction_type = "Expense"

            elif line.lower().startswith("received from "):
                description = line[len("received from "):].strip()
                transaction_type = "Income"

            elif amount_pattern.match(line):
                amount = float(
                    line.replace("₹", "").replace(",", "").strip()
                )

            i += 1

        if description and amount is not None and transaction_type:
            date = datetime.strptime(
                date_text, "%d %b, %Y"
            ).strftime("%d-%m-%Y")

            transactions.append({
                "Date": date,
                "Description": description,
                "Amount": amount,
                "Type": transaction_type,
            })

    return pd.DataFrame(
        transactions,
        columns=["Date", "Description", "Amount", "Type"]
    )


if __name__ == "__main__":
    pdf_path = input("Enter the full path to your Google Pay PDF: ").strip()
    pdf_path = pdf_path.strip('"').strip("'")

    df = import_gpay_pdf(pdf_path)
    print("\nTransactions extracted:", len(df))
    print(df.head(10).to_string(index=False))
