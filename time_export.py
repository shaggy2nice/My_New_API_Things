import requests
import csv

# Configuration
API_URL = "https://www.gitlab.com/api/v4"
TOKEN = ""
GROUP_ID = "xxx"
CSV_FILE = "/path/to/file/time_tracking_data.csv"  # Name of the CSV file to export data


# Headers for authentication
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def fetch_issues(group_id):
    """ Fetch issues from a specific group """
    response = requests.get(f"{API_URL}/groups/{group_id}/issues", headers=headers)
    return response.json()

def filter_issues_by_assignee(issues, assignee_ids):
    """ Filter issues by specific assignee IDs """
    filtered_issues = [issue for issue in issues if issue['assignee'] and issue['assignee']['id'] in assignee_ids]
    return filtered_issues

def write_to_csv(issues):
    """ Write issues data to a CSV file """
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['Issue ID', 'Assignee', 'Total Time Spent'])
        # Write issue data
        for issue in issues:
            time_spent = issue.get('time_stats', {}).get('total_time_spent', 'No time logged')
            assignee_name = issue['assignee']['name'] if issue['assignee'] else 'Unassigned'
            writer.writerow([issue['id'], assignee_name, time_spent])

def main():
    issues = fetch_issues(GROUP_ID)
    # Specify the IDs of the engineers
    engineer_ids = [x, xx, xxx]  # Example IDs
    specific_issues = filter_issues_by_assignee(issues, engineer_ids)
    
    # Export to CSV
    write_to_csv(specific_issues)
    print(f"Data has been exported to {CSV_FILE}")

if __name__ == "__main__":
    main()