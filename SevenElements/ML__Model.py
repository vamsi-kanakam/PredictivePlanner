import pandas as pd
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import KFold
import xgboost as xgb

def ML_Model():
    # Load datasets
    train_data = pd.read_csv('projects_dataset_250.csv')
    test_data = pd.read_csv('test_dataset.csv')  # Read all rows

    # Define features available in both datasets (excluding actual values, scores, and success)
    features = [
        'Project Type', 'Planned Budget ($)', 'Planned Schedule (Weeks)', 'Planned Scope (Story Points)','Project Manager Title', 
        'Project Manager Skill Level', 'Leadership Support', 'Team Collaboration Level', 'Stakeholder Engagement', 
        'Work-Life Balance (hrs/week)', 'Psychological Safety Score', 'Resource Availability', 'Turnover Rate (%)', 
        'Development Methodology', 'DevOps Adoption', 'Automated Testing Coverage (%)', 'CI/CD Pipeline Usage', 
        'Code Review Process', 'Technical Debt Level', 'Cloud-Based Development', 'Security Practices', 'Team Size', 
        'Average Experience Level',  'Expected Sprint Completion Rate (%)', 'Task Completion Rate (%)',
        'Expected Velocity (Story Points per Sprint)', 'Estimated Cycle Time (Days per Task)',
        'Defect Rate (Bugs per KLOC)', 'Number of Dependencies Blocked'
    ]

    # Define regression targets (scores)
    scores = [
        'Project Info Score', 'Environment Score', 'Technical Score', 'Stability Score',
        'Productivity Score', 'Resource Utilization Score', 'Risk Score', 'Total Score'
    ]

    # Identify categorical and numerical features
    categorical_features = [
        'Project Type', 'Project Manager Title', 'Leadership Support', 'Stakeholder Engagement',
        'Resource Availability', 'Development Methodology', 'DevOps Adoption', 'CI/CD Pipeline Usage',
        'Code Review Process', 'Technical Debt Level', 'Cloud-Based Development', 'Security Practices',
        'Average Experience Level'
    ]
    numerical_features = [col for col in features if col not in categorical_features]

    # Set up preprocessing pipeline
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features),
            ('num', 'passthrough', numerical_features)
        ]
    )

    # Prepare training and test data
    X_train = train_data[features]
    X_test = test_data[features]
    y_train_scores = train_data[scores]
    y_train_success = train_data['Project Success']

    # Fit preprocessor on training data
    preprocessor.fit(X_train)

    # Transform data
    X_train_transformed = preprocessor.transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # Step 1: Regression - Get out-of-fold predictions for training data
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    predicted_scores_train = np.zeros((len(X_train), len(scores)))

    for train_idx, val_idx in kf.split(X_train):
        X_tr, X_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
        X_tr_transformed = preprocessor.transform(X_tr)
        X_val_transformed = preprocessor.transform(X_val)

        for i, score in enumerate(scores):
            y_tr = y_train_scores.iloc[train_idx][score]
            model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
            model.fit(X_tr_transformed, y_tr)
            predicted_scores_train[val_idx, i] = model.predict(X_val_transformed)

    # Step 2: Train final regression models on full training data
    regressors = {}
    for i, score in enumerate(scores):
        model = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
        model.fit(X_train_transformed, y_train_scores[score])
        regressors[score] = model

    # Predict scores for test data
    predicted_scores_test = np.zeros((len(X_test), len(scores)))
    for i, score in enumerate(scores):
        predicted_scores_test[:, i] = np.round(regressors[score].predict(X_test_transformed),2)

    # Step 3: Classification - Prepare feature sets with predicted scores
    X_class_train = np.hstack((X_train_transformed, predicted_scores_train))
    X_class_test = np.hstack((X_test_transformed, predicted_scores_test))

    # Train XGBoost classifier
    classifier = xgb.XGBClassifier(objective='binary:logistic', n_estimators=100, random_state=42)
    classifier.fit(X_class_train, y_train_success)

    # Predict project success for test data
    y_pred_success = np.round(classifier.predict(X_class_test),2)

    # Combine results
    # results = pd.DataFrame(predicted_scores_test, columns=scores)
    # results['Predicted Project Success'] = y_pred_success
    # results = pd.concat([test_data['Project Title'], results], axis=1)

    # Combine predicted scores with the 'scores' column names (in the same order)
    for i, score in enumerate(scores):
        test_data[score] = np.round(predicted_scores_test[:, i], 2)

    # Add predicted project success to existing column if it exists, or create if not
    if 'Project Success' in test_data.columns:
        test_data['Project Success'] = y_pred_success
    else:
        test_data.insert(len(test_data.columns), 'Predicted Project Success', y_pred_success)

    # Save back to the same file
    test_data.to_csv('test_dataset.csv', index=False)

    print("Updated test_dataset.csv with predicted values.")

    # Print confirmation
    print("Updated test_dataset.csv with predicted scores and success label:")
    print(test_data.head())


    # returning scores

    # 1. Construct the full path to the CSV file
    file_path = 'test_dataset.csv'
    
    # 2. Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path)
    
    # Get the last record
    last_record = df.iloc[-1]

    scores_from_ml_model = ['Project Info Score', 'Environment Score', 'Technical Score', 'Stability Score',
        'Productivity Score', 'Resource Utilization Score', 'Risk Score', 'Total Score']
    for i in range(len(scores)):
        scores_from_ml_model[i] = last_record[scores[i]]

    return scores_from_ml_model

ML_Model()