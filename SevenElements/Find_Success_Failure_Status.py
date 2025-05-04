import pandas as pd
import os
from django.conf import settings

def Find_Success_Failure_Status(threshold=6.0):
    """
    Reads 'InputData.csv', processes only the last record,
    and appends 'Project Success' value (1 if Total Score >= threshold, else 0).
    
    :param threshold: The cutoff above which a project is considered a success.
    :return: The updated DataFrame with 'Project Success' column.
    """
    
    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'
    
    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # 3. Check for 'Total Score' column
    if 'Total Score' not in df.columns:
        raise Exception("Missing 'Total Score' column in CSV.")
    
    # 4. Get the last record only
    last_record = df.iloc[-1:]
    
    # 5. Determine success or failure based on threshold for the last record
    success_value = 1 if last_record['Total Score'].iloc[0] >= threshold else 0
    df.loc[df.index[-1], 'Project Success'] = success_value
    
    # 6. Write the updated DataFrame back to CSV
    df.to_csv(file_path, index=False)
    
    # 7. Return only the last record
    return df.iloc[-1:]

Find_Success_Failure_Status()