# SPDX-License-Identifier: AGPL-3.0-only
"""Linear integration for FlowZo."""

from typing import Any, Dict, List, Optional

import httpx
import keyring
from pydantic import BaseModel


class LinearIssue(BaseModel):
    """Linear issue model."""
    id: str
    identifier: str
    title: str
    description: Optional[str]
    state: str
    assignee: Optional[str]
    labels: List[str]
    url: str
    team: str


class LinearIntegration:
    """Linear GraphQL API integration."""
    
    SERVICE_NAME = "flowzo-linear"
    BASE_URL = "https://api.linear.app/graphql"
    
    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize Linear integration."""
        self._api_key = api_key
    
    def store_api_key(self, api_key: str, user_id: str = "default") -> None:
        """Store Linear API key securely."""
        keyring.set_password(self.SERVICE_NAME, user_id, api_key)
        self._api_key = api_key
    
    def get_api_key(self, user_id: str = "default") -> Optional[str]:
        """Retrieve stored Linear API key."""
        if self._api_key:
            return self._api_key
        
        api_key = keyring.get_password(self.SERVICE_NAME, user_id)
        if api_key:
            self._api_key = api_key
        
        return api_key
    
    def clear_api_key(self, user_id: str = "default") -> None:
        """Clear stored Linear API key."""
        keyring.delete_password(self.SERVICE_NAME, user_id)
        self._api_key = None
    
    async def _make_graphql_request(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GraphQL request to Linear API."""
        api_key = self.get_api_key()
        if not api_key:
            raise ValueError("No Linear API key available. Run 'flowzo auth linear' first.")
        
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "User-Agent": "FlowZo/0.1.0",
        }
        
        payload = {
            "query": query,
            "variables": variables or {},
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.BASE_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            
            if "errors" in data:
                raise ValueError(f"Linear API error: {data['errors']}")
            
            return data["data"]
    
    async def get_assigned_issues(self, limit: int = 10) -> List[LinearIssue]:
        """Get issues assigned to the authenticated user."""
        query = """
        query GetAssignedIssues($first: Int!) {
            viewer {
                assignedIssues(first: $first, filter: { state: { type: { nin: ["completed", "canceled"] } } }) {
                    nodes {
                        id
                        identifier
                        title
                        description
                        state {
                            name
                        }
                        assignee {
                            name
                        }
                        labels {
                            nodes {
                                name
                            }
                        }
                        url
                        team {
                            name
                        }
                    }
                }
            }
        }
        """
        
        data = await self._make_graphql_request(query, {"first": limit})
        
        issues = []
        for item in data["viewer"]["assignedIssues"]["nodes"]:
            issue = LinearIssue(
                id=item["id"],
                identifier=item["identifier"],
                title=item["title"],
                description=item.get("description"),
                state=item["state"]["name"],
                assignee=item.get("assignee", {}).get("name") if item.get("assignee") else None,
                labels=[label["name"] for label in item.get("labels", {}).get("nodes", [])],
                url=item["url"],
                team=item["team"]["name"],
            )
            issues.append(issue)
        
        return issues
    
    async def get_next_issue(self) -> Optional[LinearIssue]:
        """Get the next issue to work on (first assigned open issue)."""
        issues = await self.get_assigned_issues(limit=1)
        return issues[0] if issues else None
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test Linear API connection and return user info."""
        query = """
        query GetViewer {
            viewer {
                id
                name
                email
            }
        }
        """
        
        return await self._make_graphql_request(query) 