"""
High Timeouts Action Handler

Handles the investigation of high timeout rates in HOLMES.
"""

from .base import BaseAction


class HighTimeoutsAction(BaseAction):
    """Handler for high timeout rates investigation"""
    
    def get_action_id(self) -> str:
        return "high_timeouts"
    
    def get_description(self) -> str:
        return "Handle high timeout rates investigation"
    
    def handle(self, ack, body, respond, client):
        """Handle high timeout rates investigation"""
        ack()
        user_id = self.get_user_id(body)
        print(f"🔍 Button clicked: high_timeouts by user {user_id}")
        
        try:
            # Get channel and thread info
            channel, message_ts, thread_ts = self.get_channel_info(body)
            
            # Update original message to show what was selected (visible to all)
            self.update_original_message(client, channel, message_ts, user_id, "*High Timeout Rates*")
            
            # Post new message in thread with investigation steps
            self.post_thread_message(
                client, channel, thread_ts, 
                self.get_investigation_blocks(user_id), 
                "High Timeout Investigation Steps"
            )
            print("✅ Successfully handled high_timeouts")
            
        except Exception as e:
            print(f"❌ Error handling high_timeouts: {e}")
            print(f"Full body keys: {list(body.keys())}")
    
    def get_investigation_blocks(self, user_id):
        """Get investigation steps for high timeout rates"""
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '⏱️ High Timeout Rates Investigation'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Investigation started by:* <@{user_id}>\n\n*PRIMARY SUSPECTS:*\n• Network connectivity issues\n• Backend service overload\n• Database connection timeouts\n\n*CHECK IMMEDIATELY:*\n• Service response times in monitoring\n• Database query performance\n• Network latency metrics\n• Load balancer configuration'
                }
            }
        ]