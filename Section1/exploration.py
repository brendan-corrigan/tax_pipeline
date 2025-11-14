import pandas as pd

df = pd.read_csv("test_data/individual_tax_returns.csv")

print(df["filing_status"].unique())
