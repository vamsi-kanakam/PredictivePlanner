import pandas as pd
import os
from django.conf import settings

def Find_Risk_Score():
    """
    Reads 'InputData.csv', calculates Risk Score for the last record only,
    and updates that record with the Risk Score.

    Expected CSV Columns:
      - Planned Budget ($)
      - Actual Budget ($)
      - Planned Schedule (Weeks)
      - Actual Schedule (Weeks)
      - Planned Scope (Story Points)
      - Actual Scope (Story Points)
      - Turnover Rate (%)            (numeric, e.g. 5.0 for 5%)
      - Defect Rate (Bugs per KLOC)  (e.g., 2.5 means 2.5 bugs per KLOC)
      - Number of Dependencies Blocked
    """

    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'

    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Get the last record only
    last_record = df.iloc[-1:]

    # --------------------------------
    # HELPER FUNCTIONS FOR RISK FACTORS
    # --------------------------------

    def budget_overrun_factor(planned_budget, actual_budget):
        """
        Overrun% = ((Actual - Planned) / Planned) * 100
        Factor = min(10, max(0, Overrun%))

        If Actual < Planned, Overrun% could be negative => no overrun => 0 risk
        """
        if planned_budget <= 0:
            return 0
        overrun_percent = ((actual_budget - planned_budget) / planned_budget) * 100
        # Only consider positive overruns as a risk
        overrun_percent = max(0, overrun_percent)
        return min(10, overrun_percent)

    def schedule_slip_factor(planned_weeks, actual_weeks):
        """
        Slip% = ((Actual - Planned) / Planned) * 100
        Factor = min(10, max(0, Slip%))
        """
        if planned_weeks <= 0:
            return 0
        slip_percent = ((actual_weeks - planned_weeks) / planned_weeks) * 100
        slip_percent = max(0, slip_percent)
        return min(10, slip_percent)

    def scope_creep_factor(planned_scope, actual_scope):
        """
        Creep% = ((Actual - Planned) / Planned) * 100
        Factor = min(10, max(0, Creep%))
        If actual_scope < planned_scope, no creep => 0 risk
        """
        if planned_scope <= 0:
            return 0
        creep_percent = ((actual_scope - planned_scope) / planned_scope) * 100
        creep_percent = max(0, creep_percent)
        return min(10, creep_percent)

    def turnover_factor(turnover_rate):
        """
        If turnover_rate = 5.0 => factor = 5
        If turnover_rate = 25 => factor = 10 (capped)
        """
        return min(10, max(0, turnover_rate))

    def defect_factor(defect_rate):
        """
        If defect_rate = 3 bugs/KLOC => factor = min(10, 3 * 3.33 = ~9.99)
        If defect_rate = 5 => factor = min(10, 16.65 => 10)
        """
        return min(10, max(0, defect_rate * 3.33))

    def blocked_dependencies_factor(blocked):
        """
        Score = 2 points per blocked dependency, capped at 10
        """
        return min(10, max(0, 2 * blocked))

    # --------------------------------
    # MAIN FUNCTION TO COMPUTE RISK
    # --------------------------------

    def compute_risk_score(row):
        try:
            pb = float(row["Planned Budget ($)"])
            ab = float(row["Actual Budget ($)"])
            ps = float(row["Planned Schedule (Weeks)"])
            asch = float(row["Actual Schedule (Weeks)"])
            psc = float(row["Planned Scope (Story Points)"])
            asc = float(row["Actual Scope (Story Points)"])
            turnover = float(row["Turnover Rate (%)"])
            defect = float(row["Defect Rate (Bugs per KLOC)"])
            blocked = float(row["Number of Dependencies Blocked"])
        except KeyError as e:
            raise Exception("Missing expected column in CSV: " + str(e))
        except ValueError:
            return 0.0  # fallback if invalid data

        # Calculate each factor (0..10)
        bof = budget_overrun_factor(pb, ab)
        ssf = schedule_slip_factor(ps, asch)
        scf = scope_creep_factor(psc, asc)
        tf  = turnover_factor(turnover)
        dfc = defect_factor(defect)
        bdf = blocked_dependencies_factor(blocked)

        # Risk Score = average of six factors
        risk_score = (bof + ssf + scf + tf + dfc + bdf) / 6.0
        return round(risk_score, 2)

    # 3. Calculate risk score for the last record only
    risk_score = compute_risk_score(last_record.iloc[0])
    
    # 4. Update the last record in the original DataFrame
    df.loc[df.index[-1], "Risk Score"] = risk_score

    # 5. Write the updated DataFrame back to CSV
    df.to_csv(file_path, index=False)

    # 6. Return just the last record with its risk score
    return df.iloc[-1:]

Find_Risk_Score()