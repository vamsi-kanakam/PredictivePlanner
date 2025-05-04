import pandas as pd
import os
from django.conf import settings

def Find_Stability_Score():
    """
    Reads 'InputData.csv', calculates Team Stability Score for the last record only,
    and returns that record with the added 'Stability Score'.
    
    Expected CSV Columns:
      - Team Size                   (Integer)
      - Average Experience Level    (Junior, Mid, Senior)
      - Senior to Junior(5)        (Integer, e.g., 2 => "2 seniors per 5 juniors")
    """
    
    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'
    
    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Get the last record only
    last_record = df.iloc[-1:]
    
    # 3. Define helper functions to map each attribute to a 0–10 sub-score
    
    # 3.1 Team Size
    def map_team_size(size):
        """
        Example mapping:
          <5     -> 4
          5–12   -> 10
          13–20  -> 7
          >20    -> 5
        """
        if size < 5:
            return 4
        elif size <= 12:
            return 10
        elif size <= 20:
            return 7
        else:
            return 5
    
    # 3.2 Average Experience Level
    def map_experience_level(level):
        """
        Example mapping:
          Junior -> 4
          Mid    -> 7
          Senior -> 10
        """
        mapping = {
            "Junior": 4,
            "Mid": 7,
            "Senior": 10
        }
        return mapping.get(level, 0)  # Default 0 if not recognized
    
    # 3.3 Senior to Junior(5)
    def map_senior_junior(ratio_val):
        """
        If the column 'Senior to Junior(5)' means "X seniors per 5 juniors":
          0 -> 3
          1 -> 5
          2 -> 8
          3 -> 10
        Adjust as needed for your scenario.
        """
        try:
            ratio = int(ratio_val)
        except ValueError:
            return 0  # fallback if data is invalid
        
        if ratio == 0:
            return 3
        elif ratio == 1:
            return 5
        elif ratio == 2:
            return 8
        elif ratio >= 3:
            return 10
        return 0
    
    # 4. Define a function to compute the Team Stability Score from a single row
    def compute_stability_score(row):
        try:
            size = row["Team Size"]
            experience = row["Average Experience Level"]
            sr_jr_val = row["Senior to Junior(5)"]
        except KeyError as e:
            raise Exception("Missing expected column in CSV: " + str(e))
        
        # Map each attribute to a sub-score (0–10)
        team_size_score = map_team_size(size)
        experience_score = map_experience_level(experience)
        sr_jr_score = map_senior_junior(sr_jr_val)
        
        # Simple average across the three sub-scores
        stability_score = (team_size_score + experience_score + sr_jr_score) / 3.0
        return round(stability_score, 2)
    
    # 5. Calculate stability score for the last record only
    last_record.loc[:, "Stability Score"] = last_record.apply(compute_stability_score, axis=1)
    
    # 6. Update the last record in the original DataFrame
    df.loc[df.index[-1], "Stability Score"] = last_record["Stability Score"].iloc[0]
    
    # 7. Write the updated DataFrame back to CSV
    df.to_csv(file_path, index=False)
    
    # 8. Return only the last record with its stability score
    return last_record

Find_Stability_Score()