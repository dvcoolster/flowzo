# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for FlowZo integrations with mocked APIs."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from flowzo_integrations.github import GitHubIntegration, GitHubIssue
from flowzo_integrations.linear import LinearIntegration, LinearIssue


class TestGitHubIntegration:
    """Test GitHub integration."""
    
    def test_token_storage(self):
        """Test token storage and retrieval."""
        github = GitHubIntegration()
        
        with patch("keyring.set_password") as mock_set, \
             patch("keyring.get_password") as mock_get:
            
            # Store token
            github.store_token("test_token", "test_user")
            mock_set.assert_called_once_with("flowzo-github", "test_user", "test_token")
            
            # Retrieve token
            mock_get.return_value = "test_token"
            token = github.get_token("test_user")
            assert token == "test_token"
    
    @pytest.mark.asyncio
    async def test_get_assigned_issues(self):
        """Test fetching assigned issues."""
        github = GitHubIntegration("test_user")
        github._token = "test_token"
        
        mock_response = [
            {
                "number": 123,
                "title": "Test Issue",
                "body": "Test description",
                "state": "open",
                "assignee": {"login": "test_user"},
                "labels": [{"name": "bug"}, {"name": "priority:high"}],
                "html_url": "https://github.com/owner/repo/issues/123",
                "repository_url": "https://api.github.com/repos/owner/repo",
            }
        ]
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response_obj
            
            issues = await github.get_assigned_issues()
            
            assert len(issues) == 1
            issue = issues[0]
            assert issue.number == 123
            assert issue.title == "Test Issue"
            assert issue.repository == "owner/repo"
            assert "bug" in issue.labels
    
    @pytest.mark.asyncio
    async def test_get_next_issue(self):
        """Test getting next issue."""
        github = GitHubIntegration("test_user")
        github._token = "test_token"
        
        mock_response = [
            {
                "number": 456,
                "title": "Next Task",
                "body": None,
                "state": "open",
                "assignee": {"login": "test_user"},
                "labels": [],
                "html_url": "https://github.com/owner/repo/issues/456",
                "repository_url": "https://api.github.com/repos/owner/repo",
            }
        ]
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response_obj
            
            issue = await github.get_next_issue()
            
            assert issue is not None
            assert issue.number == 456
            assert issue.title == "Next Task"
    
    @pytest.mark.asyncio
    async def test_no_token_error(self):
        """Test error when no token is available."""
        github = GitHubIntegration()
        
        with pytest.raises(ValueError, match="No GitHub token available"):
            await github.get_next_issue()


class TestLinearIntegration:
    """Test Linear integration."""
    
    def test_api_key_storage(self):
        """Test API key storage and retrieval."""
        linear = LinearIntegration()
        
        with patch("keyring.set_password") as mock_set, \
             patch("keyring.get_password") as mock_get:
            
            # Store API key
            linear.store_api_key("test_api_key")
            mock_set.assert_called_once_with("flowzo-linear", "default", "test_api_key")
            
            # Retrieve API key
            mock_get.return_value = "test_api_key"
            api_key = linear.get_api_key()
            assert api_key == "test_api_key"
    
    @pytest.mark.asyncio
    async def test_get_assigned_issues(self):
        """Test fetching assigned issues from Linear."""
        linear = LinearIntegration()
        linear._api_key = "test_api_key"
        
        mock_response = {
            "data": {
                "viewer": {
                    "assignedIssues": {
                        "nodes": [
                            {
                                "id": "issue_123",
                                "identifier": "ENG-123",
                                "title": "Linear Test Issue",
                                "description": "Test description",
                                "state": {"name": "In Progress"},
                                "assignee": {"name": "Test User"},
                                "labels": {"nodes": [{"name": "frontend"}]},
                                "url": "https://linear.app/team/issue/ENG-123",
                                "team": {"name": "Engineering"},
                            }
                        ]
                    }
                }
            }
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response_obj
            
            issues = await linear.get_assigned_issues()
            
            assert len(issues) == 1
            issue = issues[0]
            assert issue.identifier == "ENG-123"
            assert issue.title == "Linear Test Issue"
            assert issue.team == "Engineering"
            assert "frontend" in issue.labels
    
    @pytest.mark.asyncio
    async def test_graphql_error_handling(self):
        """Test GraphQL error handling."""
        linear = LinearIntegration()
        linear._api_key = "test_api_key"
        
        mock_response = {
            "errors": [{"message": "Authentication failed"}]
        }
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_response_obj = MagicMock()
            mock_response_obj.json.return_value = mock_response
            mock_response_obj.raise_for_status.return_value = None
            
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response_obj
            
            with pytest.raises(ValueError, match="Linear API error"):
                await linear.get_assigned_issues()
    
    @pytest.mark.asyncio
    async def test_no_api_key_error(self):
        """Test error when no API key is available."""
        linear = LinearIntegration()
        
        with pytest.raises(ValueError, match="No Linear API key available"):
            await linear.get_next_issue() 