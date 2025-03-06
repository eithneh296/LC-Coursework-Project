import pandas as pd

input_file = '2018-Happiness-Index-Raw.csv'
df = pd.read_csv(input_file)
output_file = '2018-Happiness-Index-Cleaned.csv'

# Inspect the Data
print(df.head())

# Clean the Data
df = df.dropna()

# Function to check if a row contains spaces or asterisks
def contains_invalid_characters(row):
    for cell in row:
        if ' ' in cell or '*' in cell:
            return True
    return False

# Removing 'Overall rank' column
df = df.drop('Overall rank', axis=1)

# Dropping rows with missing data
df = df.dropna()

# Save Results
df.to_csv(output_file, index=False)
print("Filtered and sorted data saved successfully.")
ub