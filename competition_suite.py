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
REPO_NAME = "Random"
DATA_FILE = "competition_progress.log"

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "GitHubContributionSim/1.0 (Data Science Competition Simulation)"
}

BACKOFF_TIME = 60 # Seconds to wait after hitting secondary rate limit
backoff_until = 0

def log_event(message):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_msg = f"[{ts}] {message}"
    print(full_msg)
    with open(DATA_FILE, "a") as f:
        f.write(full_msg + "\n")

def handle_api_response(response, action_name):
    global backoff_until
    if response.status_code in [200, 201]:
        log_event(f"SUCCESS: {action_name} created/updated. URL: {response.json().get('html_url')}")
        return response.json()
    elif response.status_code == 403 and "secondary rate limit" in response.text.lower():
        log_event(f"CRITICAL: Secondary Rate Limit hit during {action_name}. Backing off for {BACKOFF_TIME}s.")
        backoff_until = time.time() + BACKOFF_TIME
        return None
    else:
        log_event(f"ERROR: {action_name} failed with status {response.status_code}. Response: {response.text[:200]}")
        return None

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
    log_event(f"COMMIT: {full_msg}")
    run_cmd("git add .")
    run_cmd(f'git commit -m "{full_msg}"')
    run_cmd("git push origin main")

def create_issue():
    issue = random.choice(ISSUES)
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    data = {"title": issue["title"], "body": issue["body"]}
    response = requests.post(url, headers=HEADERS, data=json.dumps(data))
    handle_api_response(response, f"Issue: {issue['title']}")

def create_pr_and_review(index):
    task = random.choice(PR_TASKS)
    timestamp = int(time.time())
    branch_name = f"dev/feature-set-{index}-{timestamp}"
    run_cmd(f"git checkout -b {branch_name}")
    log_event(f"PR BRANCH: Created {branch_name} for {task['title']}")
    run_cmd("git add .")
    run_cmd(f'git commit -m "{task["msg"]}"')
    run_cmd(f"git push origin {branch_name}")
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls"
    data = {"title": task["title"], "head": branch_name, "base": "main", "body": f"Refined implementation of: {task['file_change']}."}
    pr_response = requests.post(url, headers=HEADERS, data=json.dumps(data))
    pr_data = handle_api_response(pr_response, f"PR: {task['title']}")
    
    if pr_data:
        pr_number = pr_data.get('number')
        time.sleep(2) # Slight delay before review
        # Perform Review
        review_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/pulls/{pr_number}/reviews"
        review_data = {"body": random.choice(REVIEW_COMMENTS), "event": "APPROVE"}
        rev_response = requests.post(review_url, headers=HEADERS, data=json.dumps(review_data))
        handle_api_response(rev_response, f"Review for PR #{pr_number}")
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
            rev_response = requests.post(review_url, headers=HEADERS, data=json.dumps(review_data))
            handle_api_response(rev_response, f"Existing PR Review #{pr_number}")
        else:
            create_pr_and_review(random.randint(100, 999))

def code_review_optimized_suite():
    log_event("REVIEW-OPTIMIZED COMPETITION SIMULATION STARTING (ULTRA-FAST MODE)")
    print("Action Plan: Issue (30%), PR (30%), Review (30%), Commit (10%)")
    print("Press Ctrl+C to stop.")
    i = 0
    while True:
        try:
            # Check if we are in backoff
            current_time = time.time()
            if current_time < backoff_until:
                wait_remaining = int(backoff_until - current_time)
                print(f"Snoozing due to secondary rate limit... {wait_remaining}s left.")
                time.sleep(min(5, wait_remaining))
                continue

            i += 1
            print(f"\n--- FAST PULSE #{i} ---")
            roll = random.random()
            if roll < 0.30:
                create_issue()
            elif roll < 0.60:
                create_pr_and_review(i)
            elif roll < 0.90:
                review_existing_pr()
            else:
                create_commit(i)
            
            # ULTRA-FAST: 0.05 to 0.2 seconds delay
            wait = random.uniform(0.05, 0.2)
            print(f"Waiting {wait:.2f}s for next pulse...")
            time.sleep(wait)
        except KeyboardInterrupt:
            print("Shutting down...")
            break
        except Exception as e:
            log_event(f"UNEXPECTED ERROR: {e}")
            time.sleep(10)

if __name__ == "__main__":
    code_review_optimized_suite()
