import pandas as pd

import matplotlib.pyplot as plt

# --- Load data ---

accounts = pd.read_csv("LI-Small_accounts.csv")

tx = pd.read_csv("LI-Small_Trans.csv")

# --- Clean column names ---

accounts.columns = accounts.columns.str.strip().str.lower().str.replace(" ", "_")

tx.columns = tx.columns.str.strip().str.lower().str.replace(" ", "_")

# --- Parse dates and amounts ---

tx['timestamp'] = pd.to_datetime(tx['timestamp'], dayfirst=True, errors='coerce')

# pick amount_received if it exists else amount_paid

amt_col = 'amount_received' if 'amount_received' in tx.columns else 'amount_paid'

tx[amt_col] = pd.to_numeric(tx[amt_col].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce')

# --- Enrich with entity & bank ---

acc_entity = dict(zip(accounts['account_number'], accounts['entity_name']))

acc_bank = dict(zip(accounts['account_number'], accounts['bank_name']))

tx['from_entity'] = tx['from_account'].map(acc_entity)

tx['to_entity'] = tx['to_account'].map(acc_entity)

tx['from_bank'] = tx['from_account'].map(acc_bank)

tx['to_bank'] = tx['to_account'].map(acc_bank)

# --- 1) Amount over time ---

daily = tx.groupby(tx['timestamp'].dt.date)[amt_col].sum().reset_index()

plt.figure(figsize=(8, 4))

plt.plot(daily['timestamp'], daily[amt_col], marker='o')

plt.title('Amount Over Time')

plt.xlabel('Date')

plt.ylabel('Total Amount (USD)')

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig('chart_time.png')

plt.show()

# --- 2) Top 10 receiving entities ---

top_recv = tx.groupby('to_entity')[amt_col].sum().nlargest(10).reset_index()

plt.figure(figsize=(8, 5))

plt.barh(top_recv['to_entity'], top_recv[amt_col], color='orange')

plt.title('Top 10 Receiving Entities')

plt.xlabel('Total Amount (USD)')

plt.tight_layout()

plt.savefig('chart_top_entities.png')

plt.show()

# --- 3) Payment format distribution ---

if 'payment_format' in tx.columns:
    pf = tx.groupby('payment_format')[amt_col].sum().sort_values(ascending=False).reset_index()

    plt.figure(figsize=(6, 4))

    plt.bar(pf['payment_format'], pf[amt_col], color='green')

    plt.title('Amount by Payment Format')

    plt.xlabel('Payment Format')

    plt.ylabel('Total Amount (USD)')

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.savefig('chart_payment_format.png')

    plt.show()

print("Charts saved as chart_time.png, chart_top_entities.png, chart_payment_format.png")
