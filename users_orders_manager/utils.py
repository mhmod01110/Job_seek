import os
import pandas as pd
import ast

def load_and_concat_csvs(directory_path):
    # Get a list of all CSV files in the specified directory
    csv_files = [f for f in os.listdir(directory_path) if f.endswith('.csv')]
    
    # If no CSV files are found, return an empty DataFrame
    if not csv_files:
        return pd.DataFrame()

    # Read each CSV file and store DataFrames in a list
    dataframes = [pd.read_csv(os.path.join(directory_path, f)) for f in csv_files]
    
    # Concatenate all DataFrames along the rows (axis=0)
    concatenated_df = pd.concat(dataframes, axis=0, ignore_index=True)
    
    return concatenated_df


# Group by 'email' and aggregate to get unique values for 'city', 'region', and 'sectors'

def group_email_db(df: pd.DataFrame):
    # Safely parse the 'sectors' column
    def safe_literal_eval(value):
        try:
            return ast.literal_eval(value) if isinstance(value, str) else value
        except (ValueError, SyntaxError):
            return []  # Return an empty list if there's an error in evaluation

    # Apply the safe_literal_eval function to 'sectors' column
    df["sectors"] = df["sectors"].apply(safe_literal_eval)

    # Group the data
    return df.groupby('email').agg({
        'city': lambda x: list(x.unique()),
        'region': lambda x: list(x.unique()),
        'sectors': lambda x: list(set([item for sublist in x for item in sublist]))
    }).reset_index()