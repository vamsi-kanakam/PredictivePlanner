import pandas as pd
import os
from django.conf import settings

def Find_Resource_Utilization_Score():
    """
    Reads the last record from 'InputData.csv', calculates its Resource Utilization Score,
    and updates that record with the score.
    
    Expected CSV Columns:
      - Planned Budget ($)
      - Actual Budget ($)
      - Planned Schedule (Weeks)
      - Actual Schedule (Weeks)
      - Planned Scope (Story Points)
      - Actual Scope (Story Points)
      - Team Size
      - Resource Availability       (Adequate, Limited, Insufficient)
      - Turnover Rate (%)
      - Expected Sprint Completion Rate (%)
      - Task Completion Rate (%)
      - Expected Velocity (Story Points per Sprint)
      - Estimated Cycle Time (Days per Task)
      - Number of Dependencies Blocked
    """
    
    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'
    
    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # 3. Get the last record
    last_record = df.iloc[-1:]
    
    # -------------------------
    # HELPER FUNCTIONS: MAPPINGS
    # -------------------------
    
    # A) BUDGET FACTOR (BU)
    def budget_factor(planned_budget, actual_budget):
        """
        Deviation = (|Actual - Planned| / Planned) * 100
        Score = max(0, 10 - Deviation)
        """
        if planned_budget <= 0:
            return 0  # fallback if data is invalid
        deviation = abs(actual_budget - planned_budget) / planned_budget * 100
        return max(0, 10 - deviation)
    
    # B) TIME FACTOR (TU)
    def time_factor(planned_weeks, actual_weeks):
        """
        Deviation = (|Actual - Planned| / Planned) * 100
        Score = max(0, 10 - Deviation)
        """
        if planned_weeks <= 0:
            return 0
        deviation = abs(actual_weeks - planned_weeks) / planned_weeks * 100
        return max(0, 10 - deviation)
    
    # C) SCOPE FACTOR (SU)
    def scope_factor(planned_scope, actual_scope):
        """
        Score = min(10, (Actual / Planned) * 10)
        """
        if planned_scope <= 0:
            return 0
        ratio = (actual_scope / planned_scope) * 10
        return min(10, ratio)
    
    # D) TEAM FACTOR (TF)
    #   - Team Size
    #   - Resource Availability
    #   - Turnover Rate
    # Combine sub-scores by averaging them
    def map_team_size(size):
        # Example mapping
        if size < 5:
            return 4
        elif size <= 12:
            return 10
        elif size <= 20:
            return 7
        else:
            return 5
    
    def map_resource_availability(availability):
        mapping = {
            "Adequate": 10,
            "Limited": 7,
            "Insufficient": 4
        }
        return mapping.get(availability, 0)
    
    def map_turnover_rate(turnover):
        """
        Score = max(0, 10 - (turnover / 2))
        """
        return max(0, 10 - (turnover / 2.0))
    
    def team_factor(team_size, resource_avail, turnover):
        size_score = map_team_size(team_size)
        ra_score = map_resource_availability(resource_avail)
        to_score = map_turnover_rate(turnover)
        # Average
        return (size_score + ra_score + to_score) / 3.0
    
    # E) PRODUCTIVITY FACTOR (PF)
    #    Combine: Sprint Completion, Task Completion, Velocity, Cycle Time, Dependencies
    def map_sprint_completion(rate):
        return min(10, max(0, (rate / 100.0) * 10))
    
    def map_task_completion(rate):
        return min(10, max(0, (rate / 100.0) * 10))
    
    def map_velocity(velocity):
        """
        Map velocity range 20->0, 60->10 (example). Clamp to [0, 10].
        """
        if velocity <= 20:
            return 0
        elif velocity >= 60:
            return 10
        else:
            return (velocity - 20) / (60 - 20) * 10
    
    def map_cycle_time(days):
        """
        2 days -> 10, 7 days -> 5, 12 days -> 0
        We'll do a linear approach: Score = 10 - (days - 2)
        Then clamp to [0, 10].
        """
        score = 10 - (days - 2)
        return max(0, min(10, score))
    
    def map_dependencies(blocked):
        """
        0 -> 10, each blocked -> -2 points
        Score = 10 - 2 * blocked
        clamp to [0, 10]
        """
        score = 10 - 2 * blocked
        return max(0, min(10, score))
    
    def productivity_factor(sprint_rate, task_rate, velocity, cycle_time, blocked):
        sc_score = map_sprint_completion(sprint_rate)
        tc_score = map_task_completion(task_rate)
        vel_score = map_velocity(velocity)
        ct_score = map_cycle_time(cycle_time)
        dep_score = map_dependencies(blocked)
        # Average
        total = sc_score + tc_score + vel_score + ct_score + dep_score
        return total / 5.0
    
    # -------------------------
    # CALCULATE Resource Utilization Score
    # -------------------------
    
    # Calculate RU Score for the last record only
    def compute_ru_score(row):
        try:
            # Extract needed columns
            pb = float(row["Planned Budget ($)"])
            ab = float(row["Actual Budget ($)"])
            ps = float(row["Planned Schedule (Weeks)"])
            asch = float(row["Actual Schedule (Weeks)"])
            psc = float(row["Planned Scope (Story Points)"])
            asc = float(row["Actual Scope (Story Points)"])
            tsize = float(row["Team Size"])
            ravail = row["Resource Availability"]
            to_rate = float(row["Turnover Rate (%)"])
            scr = float(row["Expected Sprint Completion Rate (%)"])
            tcr = float(row["Task Completion Rate (%)"])
            vel = float(row["Expected Velocity (Story Points per Sprint)"])
            ctime = float(row["Estimated Cycle Time (Days per Task)"])
            deps = float(row["Number of Dependencies Blocked"])
        except KeyError as e:
            raise Exception("Missing expected column in CSV: " + str(e))
        except ValueError:
            return 0.0  # fallback if invalid data
        
        # Calculate factors
        bf = budget_factor(pb, ab)
        tf_time = time_factor(ps, asch)
        sf = scope_factor(psc, asc)
        tf_team = team_factor(tsize, ravail, to_rate)
        pf = productivity_factor(scr, tcr, vel, ctime, deps)
        
        # Weighted sum
        RU = (0.2 * bf) + (0.2 * tf_time) + (0.2 * sf) + (0.15 * tf_team) + (0.25 * pf)
        
        return round(RU, 2)
    
    # Calculate score for the last record
    ru_score = compute_ru_score(last_record.iloc[0])
    
    # Update the last record with the new score
    df.loc[df.index[-1], "Resource Utilization Score"] = ru_score
    
    # Write the updated DataFrame back to CSV
    df.to_csv(file_path, index=False)
    
    # Return just the last record with its score
    return df.iloc[-1:]

Find_Resource_Utilization_Score()