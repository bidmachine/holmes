"""
Revenue Issue Action Handler

Handles the selection of revenue/spend issues in HOLMES investigations.
"""

from .base import BaseAction


class RevenueAction(BaseAction):
    """Handler for revenue issue selection"""
    
    def get_action_id(self) -> str:
        return "select_revenue"
    
    def get_description(self) -> str:
        return "Handle revenue/spend issue selection"
    
    def handle(self, ack, body, respond, client):
        """Handle revenue issue selection"""
        ack()
        user_id = self.get_user_id(body)
        print(f"🔍 Button clicked: select_revenue by user {user_id}")
        
        try:
            # Get channel and thread info
            channel, message_ts, thread_ts = self.get_channel_info(body)
            
            # Update original message to show what was selected (visible to all)
            self.update_original_message(client, channel, message_ts, user_id, "*Revenue/Spend Issue*")
            
            # Post new message in thread with revenue options
            self.post_thread_message(
                client, channel, thread_ts, 
                self.get_revenue_options_blocks(), 
                "Revenue Issue Investigation Options"
            )
            print("✅ Posted new message with revenue options")
            
        except Exception as e:
            print(f"❌ Error handling revenue selection: {e}")
            print(f"Full body keys: {list(body.keys())}")
    
    def get_revenue_options_blocks(self):
        """Revenue issue option blocks"""
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '💰 Revenue Issue Analysis'}
            },
            {
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': '*What kind of revenue behavior detected?*'}
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '🔥 MASSIVE overspend (>$100K)'},
                        'value': 'massive_overspend',
                        'action_id': 'massive_overspend',
                        'style': 'danger'
                    },
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '📉 Gradual revenue drop (10-30%)'},
                        'value': 'gradual_drop',
                        'action_id': 'gradual_drop'
                    }
                ]
            }
        ]