import pandas as pd
import os
from django.conf import settings

def Find_Total_Score():
    """
    Reads 'InputData.csv' from the project directory, calculates a Total Score
    for the last record, and returns that record with the added 'Total Score'.
    """
    
    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'
    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # 3. Get the last record
    last_record = df.iloc[-1:]
    
    # 4. Define a helper function to compute Total Score
    def compute_total_score(row):
        """
        total_score = (Resource Utilization Score + (10 - Risk Score)) / 2
        """
        try:
            resource_util = float(row["Resource Utilization Score"])
            risk = float(row["Risk Score"])
        except KeyError as e:
            raise Exception(f"Missing column in CSV: {str(e)}")
        except ValueError:
            # fallback if invalid data
            return 0.0
        
        inverted_risk = 10 - risk  # The higher the risk, the lower this term
        total_score = (resource_util + inverted_risk) / 2.0
        return round(total_score, 2)
    
    # 5. Calculate Total Score for the last record
    last_record.loc[:, "Total Score"] = last_record.apply(compute_total_score, axis=1)
    
    # 6. Update the last record in the original DataFrame
    df.loc[df.index[-1], "Total Score"] = last_record["Total Score"].values[0]
    
    # 7. Write the updated DataFrame back to CSV
    df.to_csv(file_path, index=False)
    
    # 8. Return just the last record with its Total Score
    return last_record

Find_Total_Score()