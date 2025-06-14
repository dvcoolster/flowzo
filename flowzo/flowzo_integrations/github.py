# SPDX-License-Identifier: AGPL-3.0-only
"""GitHub integration for FlowZo."""

import json
from typing import Any, Dict, List, Optional

import httpx
import keyring
from pydantic import BaseModel


class GitHubIssue(BaseModel):
    """GitHub issue model."""
    number: int
    title: str
    body: Optional[str]
    state: str
    assignee: Optional[str]
    labels: List[str]
    html_url: str
    repository: str


class GitHubIntegration:
    """GitHub API integration."""
    
    SERVICE_NAME = "flowzo-github"
    BASE_URL = "https://api.github.com"
    
    def __init__(self, username: Optional[str] = None) -> None:
        """Initialize GitHub integration."""
        self.username = username
        self._token: Optional[str] = None
    
    def store_token(self, token: str, username: str) -> None:
        """Store GitHub personal access token securely."""
        keyring.set_password(self.SERVICE_NAME, username, token)
        self.username = username
        self._token = token
    
    def get_token(self, username: Optional[str] = None) -> Optional[str]:
        """Retrieve stored GitHub token."""
        if self._token:
            return self._token
        
        user = username or self.username
        if not user:
            return None
        
        token = keyring.get_password(self.SERVICE_NAME, user)
        if token:
            self._token = token
            self.username = user
        
        return token
    
    def clear_token(self, username: Optional[str] = None) -> None:
        """Clear stored GitHub token."""
        user = username or self.username
        if user:
            keyring.delete_password(self.SERVICE_NAME, user)
        self._token = None
    
    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make authenticated request to GitHub API."""
        token = self.get_token()
        if not token:
            raise ValueError("No GitHub token available. Run 'flowzo auth github' first.")
        
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "FlowZo/0.1.0",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/{endpoint}",
                headers=headers,
                params=params or {},
            )
            response.raise_for_status()
            return response.json()
    
    async def get_assigned_issues(self, state: str = "open", limit: int = 10) -> List[GitHubIssue]:
        """Get issues assigned to the authenticated user."""
        if not self.username:
            raise ValueError("Username not set")
        
        data = await self._make_request(
            "issues",
            params={
                "assignee": self.username,
                "state": state,
                "sort": "updated",
                "direction": "desc",
                "per_page": limit,
            },
        )
        
        issues = []
        for item in data:
            # Extract repository name from URL
            repo_url = item["repository_url"]
            repo_name = repo_url.split("/")[-2] + "/" + repo_url.split("/")[-1]
            
            issue = GitHubIssue(
                number=item["number"],
                title=item["title"],
                body=item.get("body"),
                state=item["state"],
                assignee=item.get("assignee", {}).get("login") if item.get("assignee") else None,
                labels=[label["name"] for label in item.get("labels", [])],
                html_url=item["html_url"],
                repository=repo_name,
            )
            issues.append(issue)
        
        return issues
    
    async def get_next_issue(self) -> Optional[GitHubIssue]:
        """Get the next issue to work on (first assigned open issue)."""
        issues = await self.get_assigned_issues(limit=1)
        return issues[0] if issues else None
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test GitHub API connection and return user info."""
        return await self._make_request("user") 