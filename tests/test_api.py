"""
Integration tests for Flask API endpoints.
"""
import pytest
import json
from research_bot import app


class TestFlaskRoutes:
    """Test Flask route handlers."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint responds."""
        response = client.get('/')
        assert response.status_code == 200
        assert b"running" in response.data.lower()
    
    def test_whatsapp_webhook_post(self, client, mock_gemini_response, mock_search_results):
        """Test WhatsApp webhook endpoint with POST."""
        response = client.post(
            '/whatsapp',
            data={
                'From': 'whatsapp:+1234567890',
                'Body': 'transformer attention'
            }
        )
        assert response.status_code == 200
        assert b"<?xml" in response.data  # TwiML response
    
    def test_whatsapp_webhook_help_command(self, client):
        """Test help command through webhook."""
        response = client.post(
            '/whatsapp',
            data={
                'From': 'whatsapp:+1234567890',
                'Body': 'help'
            }
        )
        assert response.status_code == 200
        assert b"command" in response.data.lower()
    
    def test_whatsapp_webhook_status_command(self, client):
        """Test status command through webhook."""
        response = client.post(
            '/whatsapp',
            data={
                'From': 'whatsapp:+1234567890',
                'Body': 'status'
            }
        )
        assert response.status_code == 200
        assert b"browsing" in response.data.lower()


class TestSessionManagement:
    """Test session management functionality."""
    
    def test_session_creation(self, client):
        """Test that sessions are created for new users."""
        user_id = 'whatsapp:+1111111111'
        response = client.post(
            '/whatsapp',
            data={
                'From': user_id,
                'Body': 'help'
            }
        )
        assert response.status_code == 200
    
    def test_session_persistence(self, client, mock_search_results):
        """Test that session data persists across requests."""
        user_id = 'whatsapp:+2222222222'
        
        # First request - search
        client.post(
            '/whatsapp',
            data={
                'From': user_id,
                'Body': 'transformer'
            }
        )
        
        # Second request - select
        response = client.post(
            '/whatsapp',
            data={
                'From': user_id,
                'Body': 'select 1'
            }
        )
        
        assert response.status_code == 200
        # Should have paper title in response
        assert b"test" in response.data.lower() or b"paper" in response.data.lower()
