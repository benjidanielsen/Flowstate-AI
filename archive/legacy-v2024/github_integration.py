import os
import json
import requests
import logging

logger = logging.getLogger(__name__)

class GitHubIntegration:
    def __init__(self, repo_owner, repo_name, github_token):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.base_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def create_issue(self, title, body=None, labels=None, assignees=None):
        """Creates a new GitHub issue."""
        url = f"{self.base_url}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": labels if labels else [],
            "assignees": assignees if assignees else []
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        if response.status_code == 201:
            response_data = response.json()
            logger.info(f"GitHub issue created: {response_data['html_url']}")
            return response_data
        else:
            logger.error(f"Failed to create GitHub issue: {response.status_code} - {response.text}")
            return None

    def update_issue(self, issue_number, title=None, body=None, state=None, labels=None, assignees=None):
        """Updates an existing GitHub issue."""
        url = f"{self.base_url}/issues/{issue_number}"
        data = {}
        if title: data["title"] = title
        if body: data["body"] = body
        if state: data["state"] = state
        if labels: data["labels"] = labels
        if assignees: data["assignees"] = assignees

        response = requests.patch(url, headers=self.headers, data=json.dumps(data))
        if response.status_code == 200:
            response_data = response.json()
            logger.info(f"GitHub issue {issue_number} updated: {response_data['html_url']}")
            return response_data
        else:
            logger.error(f"Failed to update GitHub issue {issue_number}: {response.status_code} - {response.text}")
            return None

    def create_pull_request(self, title, head, base, body=None):
        """Creates a new GitHub pull request."""
        url = f"{self.base_url}/pulls"
        data = {
            "title": title,
            "head": head,  # The name of the branch where your changes are implemented.
            "base": base,  # The name of the branch you want to merge your changes into.
            "body": body
        }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        if response.status_code == 201:
            response_data = response.json()
            logger.info(f"GitHub pull request created: {response_data['html_url']}")
            return response_data
        else:
            logger.error(f"Failed to create GitHub pull request: {response.status_code} - {response.text}")
            return None

    def get_issues(self, state="open", labels=None):
        """Retrieves a list of GitHub issues."""
        url = f"{self.base_url}/issues"
        params = {"state": state}
        if labels: params["labels"] = ",".join(labels)

        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get GitHub issues: {response.status_code} - {response.text}")
            return []

    def add_comment_to_issue(self, issue_number, body):
        """Adds a comment to a GitHub issue."""
        url = f"{self.base_url}/issues/{issue_number}/comments"
        data = {"body": body}
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        if response.status_code == 201:
            logger.info(f"Comment added to issue {issue_number}")
            return response.json()
        else:
            logger.error(f"Failed to add comment to issue {issue_number}: {response.status_code} - {response.text}")
            return None

# Example Usage (requires GITHUB_TOKEN environment variable)
# if __name__ == "__main__":
#     GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
#     if not GITHUB_TOKEN:
#         print("Please set the GITHUB_TOKEN environment variable.")
#     else:
#         github_client = GitHubIntegration("your_username", "your_repo_name", GITHUB_TOKEN)

#         # Create an issue
#         new_issue = github_client.create_issue(
#             title="Bug: Dashboard not loading",
#             body="The dashboard fails to load after recent changes.",
#             labels=["bug", "priority:high"],
#             assignees=["your_username"]
#         )

#         # Update an issue
#         if new_issue:
#             github_client.update_issue(
#                 new_issue["number"],
#                 state="closed",
#                 body="Resolved the dashboard loading issue."
#             )

#         # Get open issues
#         open_issues = github_client.get_issues(state="open")
#         print(f"Open issues: {len(open_issues)}")

#         # Create a pull request (example, requires branches to exist)
#         # github_client.create_pull_request(
#         #     title="Feature: Add new dashboard widget",
#         #     head="feature/new-widget",
#         #     base="main",
#         #     body="This PR adds a new widget to display real-time metrics."
#         # )
