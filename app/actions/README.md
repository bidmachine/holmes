# HOLMES Actions Directory

This directory contains all the action handlers for the HOLMES Slack bot, organized for easy maintenance and extension.

## Directory Structure

```
actions/
├── __init__.py           # Package initialization
├── base.py              # Base action class with common utilities
├── registry.py          # Action registration system
├── README.md           # This documentation
├── revenue_action.py   # Revenue issue selection handler
├── traffic_action.py   # Traffic issue selection + all traffic sub-investigations  
├── high_timeouts_action.py  # High timeouts investigation handler
└── [other action files]    # Additional action handlers
```

## Consolidated Action Structure

Each action class can handle multiple related Slack action IDs. For example:
- **TrafficAction** handles `select_traffic`, `ad_requests_drop`, `bid_requests_drop`, and `sharp_bid_drop`
- This keeps all traffic-related logic in one place for easier maintenance

## How to Add a New Action

### 1. Create a New Action File

Create a new file following the naming pattern `[action_name]_action.py`:

```python
"""
[Action Name] Action Handler

Description of what this action does.
"""

from .base import BaseAction


class YourActionNameAction(BaseAction):
    """Handler for your specific action and related sub-actions"""
    
    def get_action_id(self) -> str:
        return "your_primary_action_id"  # The main Slack action ID
    
    def get_description(self) -> str:
        return "Description of what this action does"
    
    def get_handled_actions(self) -> list:
        """Return all action IDs this handler processes"""
        return [
            "your_primary_action_id",
            "your_sub_action_1", 
            "your_sub_action_2"
        ]
    
    def handle(self, ack, body, respond, client):
        """Handle the action when triggered - routes to specific handlers"""
        ack()
        
        # Get the action that was triggered
        action_id = body.get('actions', [{}])[0].get('action_id', 'your_primary_action_id')
        user_id = self.get_user_id(body)
        print(f"🔍 Button clicked: {action_id} by user {user_id}")
        
        # Route to appropriate handler
        if action_id == "your_primary_action_id":
            self._handle_primary_action(body, client, user_id)
        elif action_id == "your_sub_action_1":
            self._handle_sub_action_1(body, client, user_id)
        elif action_id == "your_sub_action_2":
            self._handle_sub_action_2(body, client, user_id)
        else:
            print(f"❌ Unknown action_id: {action_id}")
    
    def _handle_primary_action(self, body, client, user_id):
        """Handle the primary action"""
        try:
            channel, message_ts, thread_ts = self.get_channel_info(body)
            self.update_original_message(client, channel, message_ts, user_id, "*Your Selection Text*")
            self.post_thread_message(
                client, channel, thread_ts, 
                self.get_your_options_blocks(), 
                "Your Action Options"
            )
            print("✅ Successfully handled primary action")
        except Exception as e:
            print(f"❌ Error handling primary action: {e}")
    
    def _handle_sub_action_1(self, body, client, user_id):
        """Handle sub-action 1"""
        try:
            channel, message_ts, thread_ts = self.get_channel_info(body)
            self.update_original_message(client, channel, message_ts, user_id, "*Sub Action 1*")
            self.post_thread_message(
                client, channel, thread_ts, 
                self._get_sub_action_1_blocks(user_id), 
                "Sub Action 1 Investigation"
            )
            print("✅ Successfully handled sub_action_1")
        except Exception as e:
            print(f"❌ Error handling sub_action_1: {e}")
    
    def get_your_blocks(self):
        """Get the blocks for your action response"""
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '🎯 Your Action Title'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': '*Your investigation steps or next options here*'
                }
            }
            # Add more blocks as needed
        ]
```

### 2. Register the Action

Add your new action to the `registry.py` file:

```python
# In registry.py, add the import:
from .your_action_file import YourActionNameAction

# In the register_all_actions function, add:
_registry.register(YourActionNameAction)
```

### 3. Update Investigation Steps

To update the investigation steps for an existing action:

1. Find the corresponding action file (e.g., `high_timeouts_action.py`)
2. Modify the `get_investigation_blocks()` method or equivalent
3. Update the investigation steps, suspects, or check items
4. The changes will be automatically applied when the bot restarts

## Base Action Class Features

All actions inherit from `BaseAction` which provides:

- `get_channel_info(body)` - Extract channel and thread information
- `get_user_id(body)` - Extract user ID from the request
- `update_original_message()` - Update the original message to show selection
- `post_thread_message()` - Post a new message in the thread

## Action Types

### Main Selection Actions
These handle the initial issue type selection (Revenue, Traffic, Error, etc.):
- `revenue_action.py` - Revenue/spend issues
- `traffic_action.py` - Traffic anomalies  
- `error_action.py` - Error rate issues
- `latency_action.py` - Latency problems
- `discrepancy_action.py` - Data discrepancies

### Sub-Option Actions
These handle specific investigation paths:
- `high_timeouts_action.py` - High timeout investigation
- `5xx_errors_action.py` - 5xx error investigation
- `massive_overspend_action.py` - Critical overspend handling
- etc.

### Alert Investigation Starters
These handle automatic alert response flows:
- `start_revenue_investigation_action.py` - Auto revenue investigations
- `start_traffic_investigation_action.py` - Auto traffic investigations
- etc.

## Benefits of This Structure

1. **Easy to Find**: Each action has its own file with a clear name
2. **Easy to Update**: Investigation steps are isolated in individual files
3. **Easy to Add**: Follow the template to add new actions
4. **Consistent**: All actions follow the same audit trail pattern
5. **Maintainable**: Clear separation of concerns
6. **Extensible**: New actions automatically integrate with the registry

## Example: Updating High Timeouts Investigation

To update the investigation steps for high timeouts:

1. Open `app/actions/high_timeouts_action.py`
2. Find the `get_investigation_blocks()` method
3. Modify the investigation steps:

```python
def get_investigation_blocks(self, user_id):
    return [
        {
            'type': 'header',
            'text': {'type': 'plain_text', 'text': '⏱️ High Timeout Rates Investigation'}
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Investigation started by:* <@{user_id}>\n\n*UPDATED SUSPECTS:*\n• Your new suspect 1\n• Your new suspect 2\n\n*NEW CHECKS:*\n• Your new check 1\n• Your new check 2'
            }
        }
    ]
```

4. Restart the bot to apply changes

The new structure makes HOLMES much more maintainable and easier to extend! 🎉