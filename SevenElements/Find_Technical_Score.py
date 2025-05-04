import pandas as pd
import os
from django.conf import settings

def Find_Technical_Score():
    """
    Reads 'InputData.csv', calculates Technical Score for the last record only,
    and updates that record with the score.
    
    Expected CSV Columns:
      - Development Methodology   (Agile, Scrum, Kanban, Waterfall)
      - DevOps Adoption          (Yes, No)
      - Automated Testing Coverage (%) (Numeric percentage)
      - CI/CD Pipeline Usage     (Yes, No)
      - Code Review Process      (None, Ad Hoc, Formal)
      - Technical Debt Level     (Low, Medium, High)
      - Cloud-Based Development  (Yes, No)
      - Security Practices       (Basic, Intermediate, Advanced)
    """
    # 1. Construct the full path to the CSV file
    file_path = 'predictor/templates/InputData.csv'
    
    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # 3. Define helper functions to map each attribute to a 0–10 sub-score
    def map_development_methodology(value):
        mapping = {
            "Agile": 10,
            "Scrum": 10,
            "Kanban": 8,
            "Waterfall": 5
        }
        return mapping.get(value, 0)  # default 0 if not recognized
    
    def map_devops_adoption(value):
        return 10 if value == "Yes" else 0
    
    def map_testing_coverage(coverage):
        try:
            coverage_val = float(coverage)
            # Coverage / 10, capped at 10
            return min(10, coverage_val / 10)
        except ValueError:
            return 0
    
    def map_cicd_usage(value):
        return 10 if value == "Yes" else 0
    
    def map_code_review(value):
        mapping = {
            "None": 0,
            "Ad Hoc": 5,
            "Formal": 10
        }
        return mapping.get(value, 0)
    
    def map_technical_debt(value):
        mapping = {
            "Low": 10,
            "Medium": 5,
            "High": 0
        }
        return mapping.get(value, 0)
    
    def map_cloud_development(value):
        return 10 if value == "Yes" else 0
    
    def map_security_practices(value):
        mapping = {
            "Basic": 5,
            "Intermediate": 7,
            "Advanced": 10
        }
        return mapping.get(value, 0)
    
    # 4. Define a function to compute the Technical Score from a single row
    def compute_technical_score(row):
        try:
            dev_method_val = row["Development Methodology"]
            devops_val = row["DevOps Adoption"]
            testing_val = row["Automated Testing Coverage (%)"]
            cicd_val = row["CI/CD Pipeline Usage"]
            code_review_val = row["Code Review Process"]
            tech_debt_val = row["Technical Debt Level"]
            cloud_val = row["Cloud-Based Development"]
            security_val = row["Security Practices"]
        except KeyError as e:
            raise Exception("Missing expected column in CSV: " + str(e))
        
        # Map each attribute to a sub-score
        dm_score = map_development_methodology(dev_method_val)
        devops_score = map_devops_adoption(devops_val)
        test_score = map_testing_coverage(testing_val)
        cicd_score = map_cicd_usage(cicd_val)
        cr_score = map_code_review(code_review_val)
        debt_score = map_technical_debt(tech_debt_val)
        cloud_score = map_cloud_development(cloud_val)
        sec_score = map_security_practices(security_val)
        
        # Sum sub-scores
        total_sub_score = (
            dm_score + devops_score + test_score + cicd_score +
            cr_score + debt_score + cloud_score + sec_score
        )
        
        # Average across 8 attributes
        technical_score = total_sub_score / 8.0
        
        return round(technical_score, 2)
    
    # 5. Get the last record
    last_record = df.iloc[-1:]
    
    # 6. Calculate Technical Score for the last record only
    last_record["Technical Score"] = last_record.apply(compute_technical_score, axis=1)
    
    # 7. Update the original DataFrame with the new score
    df.loc[df.index[-1], "Technical Score"] = last_record["Technical Score"].values[0]
    
    # 8. Write the updated DataFrame back to CSV
    df.to_csv(file_path, index=False)
    
    # 9. Return the last record with its Technical Score
    return last_record

Find_Technical_Score()