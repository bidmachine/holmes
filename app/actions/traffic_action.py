"""
Traffic Issue Action Handler

Handles the selection of traffic issues and all related sub-investigations in HOLMES.
"""

import time
from .base import BaseAction


class TrafficAction(BaseAction):
    """Handler for traffic issue selection and all traffic sub-actions"""
    
    def get_action_id(self) -> str:
        return "select_traffic"
    
    def get_description(self) -> str:
        return "Handle traffic issue selection and investigations"
    
    def get_handled_actions(self) -> list:
        """Return all action IDs this handler processes"""
        return [
            "select_traffic",
            "ad_requests_drop", 
            "bid_requests_drop",
            "sharp_bid_drop"
        ]
    
    def handle(self, ack, body, respond, client):
        """Handle traffic issue selection and all traffic sub-actions"""
        ack()
        
        # Get the action that was triggered
        action_id = body.get('actions', [{}])[0].get('action_id', 'select_traffic')
        user_id = self.get_user_id(body)
        print(f"🔍 Button clicked: {action_id} by user {user_id}")
        
        # Route to appropriate handler
        if action_id == "select_traffic":
            self._handle_traffic_selection(body, client, user_id)
        elif action_id == "ad_requests_drop":
            self._handle_ad_requests_drop(body, client, user_id)
        elif action_id == "bid_requests_drop":
            self._handle_bid_requests_drop(body, client, user_id)
        elif action_id == "sharp_bid_drop":
            self._handle_sharp_bid_drop(body, client, user_id)
        else:
            print(f"❌ Unknown action_id: {action_id}")
    
    def _handle_traffic_selection(self, body, client, user_id):
        """Handle main traffic issue selection"""
        try:
            # Get channel and thread info
            channel, message_ts, thread_ts = self.get_channel_info(body)
            
            # Update original message to show what was selected (visible to all)
            self.update_original_message(client, channel, message_ts, user_id, "*Traffic Issue*")
            
            # Post new message in thread with traffic options
            self.post_thread_message(
                client, channel, thread_ts, 
                self.get_traffic_options_blocks(), 
                "Traffic Issue Investigation Options"
            )
            print("✅ Posted new message with traffic options")
            
        except Exception as e:
            print(f"❌ Error handling traffic selection: {e}")
            print(f"Full body keys: {list(body.keys())}")
    
    def _handle_ad_requests_drop(self, body, client, user_id):
        """Handle ad requests dropping investigation"""
        try:
            channel, message_ts, thread_ts = self.get_channel_info(body)
            self.update_original_message(client, channel, message_ts, user_id, "*Ad Requests Dropping*")
            self.post_thread_message(
                client, channel, thread_ts, 
                self._get_ad_requests_blocks(user_id), 
                "Ad Requests Investigation Steps"
            )
            print("✅ Successfully handled ad_requests_drop")
        except Exception as e:
            print(f"❌ Error handling ad_requests_drop: {e}")
    
    def _handle_bid_requests_drop(self, body, client, user_id):
        """Handle bid requests dropping investigation"""
        try:
            channel, message_ts, thread_ts = self.get_channel_info(body)
            self.update_original_message(client, channel, message_ts, user_id, "*Bid Requests Dropping*")
            self.post_thread_message(
                client, channel, thread_ts, 
                self._get_bid_requests_blocks(user_id), 
                "Bid Requests Investigation Steps"
            )
            print("✅ Successfully handled bid_requests_drop")
        except Exception as e:
            print(f"❌ Error handling bid_requests_drop: {e}")
    
    def _handle_sharp_bid_drop(self, body, client, user_id):
        """Handle sharp bid drop investigation"""
        try:
            channel, message_ts, thread_ts = self.get_channel_info(body)
            timestamp = int(time.time())
            
            # Post to OKR channel (different behavior from other actions)
            okr_channel = 'C09EB37M4HE'  # OKR channel ID
            client.chat_postMessage(
                channel=okr_channel,
                blocks=self._get_sharp_bid_drop_blocks(user_id, timestamp),
                text="📉 Sharp Bid Drop Investigation"
            )
            
            # Update original message to show investigation started
            client.chat_update(
                channel=channel,
                ts=message_ts,
                blocks=[
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'📉 *INVESTIGATION STARTED*\\n\\nPosted to <#{okr_channel}> channel\\nHOLMES analysis initiated'
                        }
                    }
                ]
            )
            print("✅ Successfully handled sharp_bid_drop")
        except Exception as e:
            print(f"❌ Error handling sharp_bid_drop: {e}")
    
    def get_traffic_options_blocks(self):
        """Traffic issue option blocks"""
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '📊 Traffic Issue Analysis'}
            },
            {
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': '*What kind of traffic anomaly detected?*'}
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '📉 Ad requests dropping'},
                        'value': 'ad_requests_drop',
                        'action_id': 'ad_requests_drop'
                    },
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '🎯 Bid requests dropping'},
                        'value': 'bid_requests_drop',
                        'action_id': 'bid_requests_drop'
                    }
                ]
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '⚡ Sharp bid drop (10-15%)'},
                        'value': 'sharp_bid_drop',
                        'action_id': 'sharp_bid_drop'
                    }
                ]
            }
        ]
    
    def _get_ad_requests_blocks(self, user_id):
        """Get investigation blocks for ad requests dropping"""
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '📥 Ad Requests Dropping Investigation'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Investigation started by:* <@{user_id}>\\n\\n*📋 INVESTIGATION STEPS:*\\n\\n1️⃣ Check SDK integration status\\n2️⃣ Verify app inventory settings\\n3️⃣ Review mediation configuration\\n4️⃣ Monitor partner response rates\\n\\n*🔗 Relevant Dashboards:*\\n• Performance Dashboard\\n• Health Dashboard'
                }
            }
        ]
    
    def _get_bid_requests_blocks(self, user_id):
        """Get investigation blocks for bid requests dropping"""
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '🎯 Bid Requests Dropping Investigation'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Investigation started by:* <@{user_id}>\\n\\n*INVESTIGATION STEPS:*\\n• Check bid request filtering rules\\n• Verify targeting parameters\\n• Review exchange connectivity\\n• Monitor bid response rates'
                }
            }
        ]
    
    def _get_sharp_bid_drop_blocks(self, user_id, timestamp):
        """Get investigation blocks for sharp bid drop"""
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '📉 Sharp Bid Drop Investigation'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Reported by:* <@{user_id}>\\n*Time:* <!date^{timestamp}^{{date_pretty}} at {{time}}|{timestamp}>\\n*Investigation:* HOLMES System'
                }
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*🎯 PRIMARY SUSPECT:* SRO Model File Deployment Issues\\n*🔍 COMMON CAUSES:* Naming errors in notebook files, incorrect model versions\\n\\n*⚡ INVESTIGATION STEPS:*\\n• Check Rollouts audit\\n• Review SRO updates channel\\n• Verify notebook file versions\\n\\n*👥 NOTIFY:* Baptiste Poirier & Nika Kozhukh'
                }
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '✅ Found recent SRO deployment'},
                        'value': 'sro_deploy_found',
                        'action_id': 'sro_deploy_found',
                        'style': 'danger'
                    },
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '❓ No obvious SRO changes'},
                        'value': 'no_sro_changes',
                        'action_id': 'no_sro_changes'
                    }
                ]
            }
        ]