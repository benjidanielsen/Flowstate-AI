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


class GitHubAgent:
    """Higher-level helper that manages workflow issues on GitHub."""

    def __init__(self, repo_owner: str | None = None, repo_name: str | None = None, token: str | None = None) -> None:
        owner = repo_owner or os.getenv("GITHUB_REPO_OWNER")
        repo = repo_name or os.getenv("GITHUB_REPO_NAME")
        github_token = token or os.getenv("GITHUB_TOKEN")

        if not owner or not repo or not github_token:
            raise RuntimeError("Missing GitHub configuration. Set GITHUB_REPO_OWNER, GITHUB_REPO_NAME, and GITHUB_TOKEN.")

        self.integration = GitHubIntegration(owner, repo, github_token)

    def sync_workflow(self, workflow_id: str, name: str, status: str, summary: str, steps: list[dict[str, str]] | None = None) -> None:
        """Create or update an issue describing the workflow lifecycle."""

        label = f"workflow:{workflow_id}"
        existing = self.integration.get_issues(state="all", labels=[label])
        body = self._compose_body(workflow_id, name, status, summary, steps)
        labels = ['automation', 'workflow', label]

        if existing:
            issue = existing[0]
            logger.debug("Updating existing workflow issue %s", issue.get('number'))
            self.integration.update_issue(
                issue_number=issue.get('number'),
                title=f"[Workflow] {name} ({status})",
                body=body,
                state='closed' if status == 'completed' else 'open',
                labels=labels,
            )
            self.integration.add_comment_to_issue(
                issue_number=issue.get('number'),
                body=f"Workflow **{workflow_id}** moved to **{status.upper()}**\n\n{summary}",
            )
        else:
            logger.debug("Creating new workflow issue for %s", workflow_id)
            self.integration.create_issue(
                title=f"[Workflow] {name} ({status})",
                body=body,
                labels=labels,
            )

    def _compose_body(
        self,
        workflow_id: str,
        name: str,
        status: str,
        summary: str,
        steps: list[dict[str, str]] | None = None,
    ) -> str:
        step_lines = []
        for step in steps or []:
            step_id = step.get('id')
            agent = step.get('agentName') or step.get('agent_name')
            task = step.get('taskType') or step.get('task_type')
            step_lines.append(f"- {step_id} — agent `{agent}` task `{task}`")
        if not step_lines:
            step_lines.append('- No steps registered')
        return (
            f"**Workflow:** {name}\n"
            f"**ID:** {workflow_id}\n"
            f"**Status:** {status}\n\n"
            f"{summary}\n\n"
            "**Steps**\n" + "\n".join(step_lines)
        )

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
