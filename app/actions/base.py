"""
Base Action Class for HOLMES Actions

This provides a common interface and utility methods for all HOLMES action handlers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseAction(ABC):
    """Base class for all HOLMES action handlers"""
    
    def __init__(self):
        self.action_id = self.get_action_id()
        self.description = self.get_description()
    
    @abstractmethod
    def get_action_id(self) -> str:
        """Return the primary Slack action ID this handler responds to"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return a human-readable description of this action"""
        pass
    
    def get_handled_actions(self) -> List[str]:
        """Return all action IDs this handler can process (including sub-actions)"""
        return [self.get_action_id()]
    
    @abstractmethod
    def handle(self, ack, body, respond, client):
        """Handle the action when triggered"""
        pass
    
    def get_channel_info(self, body: Dict[str, Any]) -> tuple:
        """Extract channel and thread information from the body"""
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        return channel, message_ts, thread_ts
    
    def get_user_id(self, body: Dict[str, Any]) -> str:
        """Extract user ID from the body"""
        return body.get('user', {}).get('id', 'unknown')
    
    def update_original_message(self, client, channel: str, message_ts: str, user_id: str, selection_text: str):
        """Update the original message to show what was selected"""
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text=f"✅ User selected: {selection_text}",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'✅ <@{user_id}> selected: {selection_text}'
                    }
                }
            ]
        )
    
    def post_thread_message(self, client, channel: str, thread_ts: str, blocks: List[Dict], text: str):
        """Post a new message in the thread"""
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=blocks,
            text=text
        )