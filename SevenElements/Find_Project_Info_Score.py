import pandas as pd
import os
from django.conf import settings

def Find_Project_Info_Score():
    """
    Reads 'InputData.csv', calculates the Project Info Score for the last record,
    and updates that record with the calculated score.
    """
    # Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Get the last row
    last_row = df.iloc[-1]
    
    def compute_info_score(row):
        # Extract required values
        try:
            planned_budget = float(row["Planned Budget ($)"])
            actual_budget = float(row["Actual Budget ($)"])
            planned_schedule = float(row["Planned Schedule (Weeks)"])
            actual_schedule = float(row["Actual Schedule (Weeks)"])
            planned_scope = float(row["Planned Scope (Story Points)"])
            actual_scope = float(row["Actual Scope (Story Points)"])
            pm_skill = float(row["Project Manager Skill Level"])
        except KeyError as e:
            raise Exception("Missing expected column in CSV: " + str(e))
        except ValueError as e:
            raise Exception("Invalid data type in CSV: " + str(e))
        
        # Calculate factors (keeping existing calculations)
        budget_deviation = abs(actual_budget - planned_budget) / planned_budget * 100
        budget_factor = max(0, 10 - budget_deviation)
        
        schedule_deviation = abs(actual_schedule - planned_schedule) / planned_schedule * 100
        schedule_factor = max(0, 10 - schedule_deviation)
        
        scope_factor = (actual_scope / planned_scope) * 10 if planned_scope != 0 else 0
        scope_factor = min(scope_factor, 10)
        
        pm_skill_factor = (pm_skill / 5) * 10
        
        # Combine factors
        project_info_score = (0.3 * budget_factor + 0.3 * schedule_factor +
                            0.3 * scope_factor + 0.1 * pm_skill_factor)
        
        return round(project_info_score, 2)
    
    # Calculate score for the last row only
    score = compute_info_score(last_row)
    
    # Update the last row with the new score
    df.at[df.index[-1], "Project Info Score"] = score
    
    # Save the updated DataFrame back to CSV
    df.to_csv(file_path, index=False)
    
    return score  # Return just the calculated score instead of the entire DataFrame

Find_Project_Info_Score()