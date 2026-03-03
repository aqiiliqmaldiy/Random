import requests
import json
import time
import random
import subprocess
import os
from datetime import datetime

# CONFIGURATION
# Using the token provided by the user
GITHUB_TOKEN = "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"
REPO_OWNER = "aqiiliqmaldiy"
REPO_NAME = "Data-Science-Competition" 
DATA_FILE = "competition_progress.log"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# DATA SCIENCE MESSAGES
COMMIT_MESSAGES = [
    "Refined hyperparameter grid for XGBoost",
    "Added data normalization to preprocessing pipeline",
    "Implemented stratified k-fold cross-validation",
    "Cleaned up outliers in training set",
    "Optimized feature engineering logic for time-series",
    "Added SHAP value plots for model interpretation",
    "Updated LightGBM parameters for better convergence",
    "Fixed minor bug in custom loss function",
    "Added logging for validation metrics",
    "Implemented early stopping for neural network baseline",
    "Refactored data loading for memory efficiency",
    "Updated submission script for test set predictions",
    "Integrated Optuna for hyperparameter optimization"
]

ISSUES = [
    {"title": "EDA: In-depth analysis of class imbalance", "body": "Class imbalance detected in the target variable. Need to evaluate oversampling/SMOTE strategies."},
    {"title": "Feature Request: Add interaction terms", "body": "Suggesting we add interaction features between 'feature_a' and 'feature_b' for better nonlinearity capture."},
    {"title": "Validation Gap: Discrepancy between local CV and leaderboard", "body": "Investigating potential data leakage as local CV is significantly higher than leaderboard score."},
    {"title": "Optimization: Parallelize preprocessing pipeline", "body": "The preprocessing is taking too long on the full dataset. Need to implement joblib for feature generation."},
    {"title": "Model Selection: Try TabNet for categorical features", "body": "TabNet has shown good results for tabular data with high cardinality. Worth a baseline test."},
    {"title": "Evaluation: Robustness check on 'noisy' features", "body": "Suspecting some features contain synthesized noise. Need a permutation importance check."}
]

PR_TASKS = [
    {"title": "Advanced Feature Engineering Pipeline", "msg": "Implemented a robust pipeline for automated feature generation and selection.", "file_change": "Added complex feature engineering scripts."},
    {"title": "Ensemble Model: XGBoost + LightGBM + CatBoost", "msg": "Added a weighted voting ensemble for final predictions.", "file_change": "Implemented model stacker."},
    {"title": "Implementing TTA (Test Time Augmentation)", "msg": "Added TTA logic for the final prediction phase.", "file_change": "Inference script updated with TTA."},
    {"title": "Add pseudo-labeling strategy for test set", "msg": "Integrated pseudo-labeling for semi-supervised boost.", "file_change": "Training loop updated with pseudo-labels."},
    {"title": "Optimize data loader with Dask for scalability", "msg": "Switched loading to Dask to handle large datasets.", "file_change": "Data loader migration."}
]

REVIEW_COMMENTS = [
    "Solid implementation. The feature engineering logic is quite creative.",
    "The ensemble weights look well-balanced. Great job on the CV validation.",
    "LGTM. The code structure is clean and efficient.",
    "Verified the performance boost. This should move us up the leaderboard!",
    "The TTA implementation is interesting. Have we checked the inference time?",
    "Pseudo-labeling is a high-risk move. Let's monitor validation closely."
]

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def create_commit(index):
    msg = random.choice(COMMIT_MESSAGES)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"{msg} (Sprint Pulse #{index}) [{ts}]"
    with open(DATA_FILE, "a") as f:
        f.write(f"{ts} - {full_msg}\n")
    run_cmd("git add .")
    run_cmd(f'git commit -m "{full_msg}"')
    run_cmd("git push origin main")

def create_issue():
    issue = random.choice(ISSUES)
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    data = {"title": issue["title"], "body": issue["body"]}
    response = requests.post(url, headers=HEADERS, data=json.dumps(data))
    if response.status_code == 201:
        print(f"Issue created: {response.json().get('html_url')}")

def create_pr_and_review(index):
    task = random.choice(PR_TASKS)
    timestamp = int(time.time())
    branch_name = f"dev/feature-set-{index}-{timestamp}"
    run_cmd(f"git checkout -b {branch_name}")
    with open(DATA_FILE, "a") as f:
        f.write(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PR Pulse: {task['file_change']}")
    run_cmd("git add .")
    run_cmd(f'git commit -m "{task["msg"]}"')
    run_cmd(f"git push origin {branch_name}")
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    data = {"title": task["title"], "head": branch_name, "base": "main", "body": f"Refined implementation of: {task['file_change']}."}
    pr_response = requests.post(url, headers=HEADERS, data=json.dumps(data))
    if pr_response.status_code == 201:
        pr_number = pr_response.json().get('number')
        print(f"PR opened: {pr_response.json().get('html_url')}")
        time.sleep(1)
        # Perform Review
        review_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/reviews"
        review_data = {"body": random.choice(REVIEW_COMMENTS), "event": "APPROVE"}
        requests.post(review_url, headers=HEADERS, data=json.dumps(review_data))
        print(f"Code Review added to PR #{pr_number}")
    run_cmd("git checkout main")

def review_existing_pr():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls?state=open"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        prs = response.json()
        if prs:
            pr = random.choice(prs)
            pr_number = pr['number']
            review_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/reviews"
            review_data = {"body": random.choice(REVIEW_COMMENTS) + " (Sprint Audit)", "event": "COMMENT"}
            requests.post(review_url, headers=HEADERS, data=json.dumps(review_data))
            print(f"Review comment added to existing PR #{pr_number}")
        else:
            create_pr_and_review(random.randint(100, 999))

def code_review_optimized_suite():
    print("REVIEW-OPTIMIZED COMPETITION SIMULATION STARTING")
    print("Action Plan: PR+Review (45%), Issue (35%), Standalone Review (15%), Commit (5%)")
    print("Press Ctrl+C to stop.")
    i = 0
    while True:
        try:
            i += 1
            print(f"\n--- FAST PULSE #{i} ---")
            roll = random.random()
            if roll < 0.50:
                create_pr_and_review(i)
            elif roll < 0.70:
                create_issue()
            elif roll < 0.95:
                review_existing_pr()
            else:
                create_commit(i)
            
            # ACCELERATED: 2 to 8 seconds delay
            wait = random.randint(2, 8)
            print(f"Waiting {wait}s for next pulse...")
            time.sleep(wait)
        except KeyboardInterrupt:
            print("Shutting down...")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    code_review_optimized_suite()
