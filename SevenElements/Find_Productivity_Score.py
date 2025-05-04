import pandas as pd
import os
from django.conf import settings

def Find_Productivity_Score():
    """
    Reads 'InputData.csv' from the project directory, calculates a Productivity Score
    for the last record only, and returns that record as a DataFrame with the added
    'Productivity Score' column.

    Expected CSV Columns:
      - Expected Sprint Completion Rate (%)
      - Task Completion Rate (%)
      - Expected Velocity (Story Points per Sprint)
      - Estimated Cycle Time (Days per Task)
      - Defect Rate (Bugs per KLOC)
      - Number of Dependencies Blocked
    """
    
    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'
    
    # 2. Read the CSV file into a pandas DataFrame and get the last record
    df = pd.read_csv(file_path)
    last_record = df.iloc[[-1]]  # Get the last record as a DataFrame
    
    # -------------------------
    # HELPER FUNCTIONS FOR SUB-SCORES
    # -------------------------
    
    def map_sprint_completion(rate):
        """
        Convert sprint completion rate (%) to 0–10.
        100% -> 10, 0% -> 0
        """
        return min(10, max(0, (rate / 100.0) * 10))
    
    def map_task_completion(rate):
        """
        Convert task completion rate (%) to 0–10.
        100% -> 10, 0% -> 0
        """
        return min(10, max(0, (rate / 100.0) * 10))
    
    def map_velocity(velocity):
        """
        Map velocity range [20..60] -> [0..10].
        velocity <= 20 -> 0
        velocity >= 60 -> 10
        else -> linear in between
        """
        if velocity <= 20:
            return 0
        elif velocity >= 60:
            return 10
        else:
            return (velocity - 20) / (60 - 20) * 10
    
    def map_cycle_time(days):
        """
        Lower cycle time -> higher score.
        Example approach:
          2 days -> 10
          7 days -> 5
          12 days -> 0
        We'll do a simple linear approach: score = 10 - (days - 2), clamped [0..10].
        """
        score = 10 - (days - 2)
        return max(0, min(10, score))
    
    def map_defect_rate(defect):
        """
        Lower defect rate -> higher score.
        Example: 0 bugs/KLOC -> 10, 3 bugs/KLOC -> 0, linearly.
        We'll approximate with: score = 10 - (defect * 3.33), clamped [0..10].
        """
        score = 10 - (defect * 3.33)
        return max(0, min(10, score))
    
    def map_dependencies(blocked):
        """
        Fewer dependencies blocked -> higher score.
        Example: score = 10 - 2*blocked, clamped [0..10].
        """
        score = 10 - 2 * blocked
        return max(0, min(10, score))
    
    # -------------------------
    # FUNCTION TO COMPUTE PRODUCTIVITY
    # -------------------------
    
    def compute_productivity(row):
        try:
            sprint_rate = float(row["Expected Sprint Completion Rate (%)"])
            task_rate = float(row["Task Completion Rate (%)"])
            velocity = float(row["Expected Velocity (Story Points per Sprint)"])
            cycle_time = float(row["Estimated Cycle Time (Days per Task)"])
            defect_rate = float(row["Defect Rate (Bugs per KLOC)"])
            deps_blocked = float(row["Number of Dependencies Blocked"])
        except KeyError as e:
            raise Exception("Missing expected column in CSV: " + str(e))
        except ValueError:
            # Fallback if data is invalid
            return 0.0
        
        # Calculate each sub-score
        sc_score = map_sprint_completion(sprint_rate)
        tc_score = map_task_completion(task_rate)
        vel_score = map_velocity(velocity)
        ct_score = map_cycle_time(cycle_time)
        df_score = map_defect_rate(defect_rate)
        dep_score = map_dependencies(deps_blocked)
        
        # Average sub-scores
        total = sc_score + tc_score + vel_score + ct_score + df_score + dep_score
        prod_score = total / 6.0
        return round(prod_score, 2)
    
    # 3. Apply the compute_productivity function to the last record only
    last_record["Productivity Score"] = last_record.apply(compute_productivity, axis=1)
    
    # 4. (Optional) Write the last record with its score to the CSV file
    last_record.to_csv(file_path, index=False)
    
    # 5. Return the last record with its productivity score
    return last_record

Find_Productivity_Score()