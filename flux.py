import requests
from datetime import datetime
from git import Repo

# Configuration
YOUR_API_KEY = "YOUR_API_KEY"
DATA_FILE_PATH = "data.json"
API_URL = "https://api.askflux.ai/v1/query"

# Query to collect data
query = """
{
  search(query: "python") {
    results {
      title
      url
      description
      createdAt
    }
  }
}
"""

# Function to fetch data from AskFlux.ai API
def fetch_data(query):
    headers = {"Authorization": f"Bearer {YOUR_API_KEY}"}
    response = requests.post(API_URL, json={"query": query}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"API request failed with status code: {response.status_code}")

# Function to store data in a JSON file
def store_data(data, file_path):
    with open(file_path, "w") as f:
        f.write(json.dumps(data, indent=4))

# Function to commit and push changes to Git repository
def commit_and_push(repo, message):
    repo.index.add([DATA_FILE_PATH])
    repo.index.commit(message)
    origin = repo.remote("origin")
    origin.push()

# Main execution
if __name__ == "__main__":
    data = fetch_data(query)
    store_data(data, DATA_FILE_PATH)

    # Initialize Git repository
    repo = Repo(".")

    # Commit and push changes
    commit_and_push(repo, f"Data collected from AskFlux.ai on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("Data successfully collected and stored in Fun_API_Works repository.")