import os
import requests

USERNAME = "mohitroscen"
TOKEN = os.getenv("GITHUB_TOKEN")

def get_stats():
    if not TOKEN:
        print("No GITHUB_TOKEN provided. Using fallback values.")
        return {"repos": "XX", "stars": "XX", "followers": "XX", "commits": "XX"}
    
    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    followers = 0
    repos = 0
    stars = 0
    commits = 0
    
    # GraphQL Query
    query = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        followers {
          totalCount
        }
        repositories(first: 100, after: $cursor, ownerAffiliations: OWNER, isFork: false) {
          totalCount
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            stargazers {
              totalCount
            }
          }
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """
    
    cursor = None
    has_next_page = True
    
    while has_next_page:
        variables = {"login": USERNAME, "cursor": cursor}
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": variables},
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code} {response.text}")
            break
        
        data = response.json()
        if "errors" in data:
            print(f"GraphQL errors: {data['errors']}")
            break
        
        user_data = data["data"]["user"]
        
        # We only need to fetch these once
        if cursor is None:
            followers = user_data["followers"]["totalCount"]
            repos = user_data["repositories"]["totalCount"]
            commits = user_data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
        
        # Accumulate stars
        stars += sum(repo["stargazers"]["totalCount"] for repo in user_data["repositories"]["nodes"])
        
        page_info = user_data["repositories"]["pageInfo"]
        has_next_page = page_info["hasNextPage"]
        cursor = page_info["endCursor"]
    
    return {
        "repos": str(repos),
        "stars": str(stars),
        "followers": str(followers),
        "commits": str(commits)
    }

def update_readme():
    stats = get_stats()
    
    # Read the template
    with open("README_TEMPLATE.md", "r", encoding="utf-8") as f:
        template = f.read()
    
    # Replace placeholders
    readme_content = template.format(**stats)
    
    # Write the updated README
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("README.md has been updated successfully!")
    print(f"Stats fetched: {stats}")

if __name__ == "__main__":
    update_readme()
