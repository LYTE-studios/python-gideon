import requests
from bot.logger import setup_logger

logger = setup_logger("GitHub")

class GitHubClient:
    def __init__(self, token: str, repo: str):
        self.token = token
        self.repo = repo
        self.base_url = f"https://api.github.com/repos/{repo}"

    def create_pr(self, branch: str, title: str, body: str, base: str = "main"):
        """Creates a Pull Request on GitHub (assumes branch already pushed to remote)."""
        url = f"{self.base_url}/pulls"
        headers = {"Authorization": f"token {self.token}", "Accept": "application/vnd.github+json"}
        data = {
            "title": title,
            "head": branch,
            "base": base,
            "body": body
        }
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            pr_data = response.json()
            logger.info(f"Created PR: {pr_data.get('html_url')}")
            return pr_data
        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return None
    def list_repos(self, org_or_user: str):
        """List repos for an organization or user."""
        url = f"https://api.github.com/users/{org_or_user}/repos"
        headers = {"Authorization": f"token {self.token}"}
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            return [repo['full_name'] for repo in data]
        except Exception as e:
            logger.error(f"Error listing repos for {org_or_user}: {e}")
            return []

    def list_pull_requests(self, repo: str, state="open"):
        """List PRs for the given repo."""
        url = f"https://api.github.com/repos/{repo}/pulls?state={state}"
        headers = {"Authorization": f"token {self.token}"}
        try:
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            return [
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "url": pr["html_url"],
                    "user": pr["user"]["login"],
                }
                for pr in data
            ]
        except Exception as e:
            logger.error(f"Error listing PRs for {repo}: {e}")
            return []
        
    def get_pull_request(self, repo: str, pr_number: int):
            """Fetch PR details from GitHub."""
            url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
            headers = {"Authorization": f"token {self.token}"}
            try:
                response = requests.get(url, headers=headers, timeout=20)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error fetching PR {pr_number} from {repo}: {e}")
                return None