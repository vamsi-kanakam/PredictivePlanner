import pandas as pd
import os
from django.conf import settings

def Find_Environment_Score():
    """
    Reads 'InputData.csv', calculates the Environment Score for the last record,
    and updates that record with the calculated score.
    
    Expected CSV Columns:
      - Leadership Support           (High, Medium, Low)
      - Team Collaboration Level     (1-10)
      - Stakeholder Engagement       (Strong, Moderate, Weak)
      - Work-Life Balance (hrs/week) (35, 40, 50)
      - Psychological Safety Score   (1-10)
      - Resource Availability        (Adequate, Limited, Insufficient)
      - Turnover Rate (%)            (Numeric)
    """
    
    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'
    
    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Get the last record
    last_record = df.iloc[-1]
    print(last_record)
    # 3. Define a helper function to map each attribute to a 0-10 sub-score
    def map_leadership_support(value):
        mapping = {"High": 10, "Medium": 7, "Low": 4}
        return mapping.get(value, 0)  # default to 0 if not found
    
    def map_team_collaboration(value):
        # Should be 1-10; clamp if needed
        return max(0, min(10, float(value)))
    
    def map_stakeholder_engagement(value):
        mapping = {"Strong": 10, "Moderate": 7, "Weak": 4}
        return mapping.get(value, 0)
    
    def map_work_life_balance(value):
        # Example direct mapping
        if value == 35:
            return 9
        elif value == 40:
            return 10
        elif value == 50:
            return 7
        else:
            # fallback approach if other numbers appear
            # e.g., 10 - the deviation from 40 hrs
            # clamp to [0, 10]
            deviation = abs(float(value) - 40) * 0.5
            return max(0, min(10, 10 - deviation))
    
    def map_psychological_safety(value):
        # Should be 1-10; clamp if needed
        return max(0, min(10, float(value)))
    
    def map_resource_availability(value):
        mapping = {"Adequate": 10, "Limited": 7, "Insufficient": 4}
        return mapping.get(value, 0)
    
    def map_turnover_rate(value):
        # Lower turnover => higher score
        # Score = 10 - (Turnover% / 2), clamp to [0, 10]
        rate = float(value)
        return max(0, min(10, 10 - (rate / 2.0)))
    
    # 4. Calculate Environment Score for the last record only
    try:
        # Extract raw values from the last record
        leadership_val = last_record["Leadership Support"]
        team_collab_val = last_record["Team Collaboration Level"]
        stakeholder_val = last_record["Stakeholder Engagement"]
        wlb_val = last_record["Work-Life Balance (hrs/week)"]
        psych_safe_val = last_record["Psychological Safety Score"]
        resource_val = last_record["Resource Availability"]
        turnover_val = last_record["Turnover Rate (%)"]
        
        # Map each attribute to a 0-10 sub-score
        ls_score = map_leadership_support(leadership_val)
        tc_score = map_team_collaboration(team_collab_val)
        se_score = map_stakeholder_engagement(stakeholder_val)
        wlb_score = map_work_life_balance(wlb_val)
        ps_score = map_psychological_safety(psych_safe_val)
        ra_score = map_resource_availability(resource_val)
        tr_score = map_turnover_rate(turnover_val)
        
        # Calculate environment score
        environment_score = (
            ls_score + tc_score + se_score +
            wlb_score + ps_score + ra_score +
            tr_score
        ) / 7.0
        
        environment_score = round(environment_score, 2)
        print(environment_score)
        # Update the last record with the calculated score
        df.at[df.index[-1], "Environment Score"] = environment_score
        
        # Write the updated DataFrame back to the CSV
        df.to_csv(file_path, index=False)
        
        # Return only the last record as a DataFrame
        return df.iloc[[-1]]
        
    except KeyError as e:
        raise Exception("Missing expected column in CSV: " + str(e))

Find_Environment_Score()