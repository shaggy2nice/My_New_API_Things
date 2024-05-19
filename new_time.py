import requests
import csv

# Configuration
API_URL = "https://www.gitlab.com/api/v4?created_after=2024-04-01&created_before=2024-05-01"
TOKEN = ""
GROUP_ID = "XXX"
CSV_FILE = "/Path/To/File/group_issues_details.csv"  # Name of the CSV file to export data

# Headers for authentication
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def fetch_issues_from_group(group):
    """ Fetch all issues from given project with pagination """
    all_issues = []
    for group in group:
        page = 1
        while True:
            response = requests.get(f"{API_URL}/groups/{GROUP_ID}/issues?page={page}&per_page=100", headers=headers)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break
                all_issues.extend(data)
                page += 1
            else:
                print(f"Failed to fetch issues for group {GROUP_ID}: {response.status_code}")
                break
    return all_issues

def write_to_csv(issues):
    """ Write issues data to a CSV file """
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['Project ID', 'Issue ID', 'Assignee', 'Total Time Spent (s)', 'Time Spent (hr:min)', 'References'])
        # Write issue data
        for issue in issues:
            time_spent_seconds = issue.get('time_stats', {}).get('total_time_spent', 0)
            time_spent_hr_min = f"{time_spent_seconds // 3600}h:{(time_spent_seconds % 3600) // 60}m"
            references = ", ".join([mr['web_url'] for mr in issue.get('references', {}).get('merge_requests', [])])
            assignee_name = issue['assignee']['name'] if issue['assignee'] else 'Unassigned'
            writer.writerow([issue['project_id'], issue['id'], assignee_name, time_spent_seconds, time_spent_hr_min, references])

def main():
    all_issues = fetch_issues_from_group(GROUP_ID)
    
    # Export to CSV
    write_to_csv(all_issues)
    print(f"Data has been exported to {CSV_FILE}")

if __name__ == "__main__":
    main()