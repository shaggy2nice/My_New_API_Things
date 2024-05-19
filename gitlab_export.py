import requests
import csv
from datetime import datetime

# Configuration
group_id = "groupid"  # Project ID or Group ID
access_token = ""
base_url = f"https://gitlab.com/api/v4/groups/{group_id}/issues?created_after=2024-04-01&created_before=2024-05-01"
csv_file_path = "/path/to/file/goeshere.csv"  # Path to the CSV file

# Function to fetch all issues with optional filters
def get_issues(state=None, include_labels=None):
    params = {
        "private_token": access_token,
        "per_page": 100
    }
    if state:
        params["state"] = state
    if include_labels:
        params["labels"] = ','.join(include_labels)
    
    exclude_label = "exclude_label"
    issues = []
    page = 1

    while True:
        params["page"] = page
        response = requests.get(base_url, params=params)
        print(f"Fetching page {page}: {response.url}")  # Debug: Show request URL
        if response.status_code != 200:
            print(f"Failed to fetch issues: {response.status_code}")
            break
        data = response.json()
        if not data:
            break  # No more data to process

        filtered_data = []
        for issue in data:
            issue_labels = issue.get('labels', [])  # Assume labels are a list of strings
            print(f"Issue ID {issue['id']} Labels: {issue_labels}")  # Debug: Print labels of each issue

            # Exclude issues that contain the 'Deployment-Passport' label
            if exclude_label not in issue_labels:
                filtered_data.append(issue)

        issues.extend(filtered_data)
        page += 1
    
    return issues

# Function to process issues data
def process_data(issues):
    opened_count = len(issues)
    closed_count = 0
    total_closure_time = 0
    
    for issue in issues:
        if issue["state"] == "closed":
            closed_count += 1
            created_at = datetime.fromisoformat(issue['created_at'].rstrip('Z'))
            closed_at = datetime.fromisoformat(issue['closed_at'].rstrip('Z'))
            closure_time_seconds = (closed_at - created_at).total_seconds()
            total_closure_time += closure_time_seconds

    # Calculate average closure time in days
    avg_closure_days = (total_closure_time / closed_count) / 86400 if closed_count > 0 else 0
    
    return opened_count, closed_count, avg_closure_days

# Output to CSV
def output_to_csv(opened, closed, avg_closure_days):
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Statistic", "Value"])
        writer.writerow(["Opened Tickets", opened])
        writer.writerow(["Closed Tickets", closed])
        writer.writerow(["Average Closure Time (days)", avg_closure_days])

# Fetching and processing the issues
issues = get_issues()
opened, closed, avg_closure = process_data(issues)

# Outputting the results to CSV
output_to_csv(opened, closed, avg_closure)
print(f"Statistics written to /Path/Goes/Here")