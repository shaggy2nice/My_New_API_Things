import requests
import csv
from datetime import datetime

# Configuration
group_id = "831"  # Replace with your Group ID
access_token = ""  # Replace with your GitLab Personal Access Token
base_url = f"https://gitlab.com/api/v4/groups/{group_id}/issues?created_after=2024-05-01&label_name=Customer%20Created"
csv_file_path = "/Path/To/File/Goes/Here/output_may.csv"  # Specify your desired CSV path

def get_issues():
    headers = {
        "Private-Token": access_token
    }
    params = {
        "per_page": 100,
        "order_by": "created_at",
        "sort": "asc"
    }
    issues = []

    page = 1
    while True:  # Pagination using a while loop
        params["page"] = page
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues on page {page}: {e}")
            break

        data = response.json()
        if not data:  # Break the loop if no more issues are found on this page
            break

        for issue in data:
            issue_id = issue['iid']
            created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
            first_public_note = None
            notes_url = f"https://code.il2.gamewarden.io/api/v4/projects/{issue['project_id']}/issues/{issue_id}/notes"

            try:
                notes_response = requests.get(notes_url, headers=headers)
                notes_response.raise_for_status()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching notes for issue {issue_id}: {e}")
                continue

            notes = notes_response.json()
            print(f"Fetched {len(notes)} notes for issue {issue_id}")

            for note in notes:
                if not note.get('system') and not note.get('confidential'):
                    note_created_at = datetime.strptime(note['created_at'], '%Y-%m-%dT%H:%M:%S.%fZ')
                    first_public_note = note_created_at
                    break  # Exit the loop after finding the first public note

            time_difference = None
            if first_public_note:
                time_difference = first_public_note - created_at

            issues.append({
                "issue_title": issue['title'],  # Use issue title instead of ID
                "created_at": created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),  # Include opened time
                "first_public_note": first_public_note.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if first_public_note else "No public comments",
                "time_difference": str(time_difference) if time_difference else ""  # Formatted time difference
            })

        page += 1  # Increment to the next page

    return issues

def write_to_csv(issues):
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Ticket Title', 'Open Time', 'Comment Time', 'Time Difference'])  # Updated header
        for issue in issues:
            writer.writerow([issue['issue_title'], issue['created_at'],
                             issue.get('first_public_note', "No public comments"),
                             issue.get('time_difference', "")])

# Run the script
issues = get_issues()
write_to_csv(issues)
print("Data has been written to CSV.")