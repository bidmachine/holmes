"""
Action Registry for HOLMES

This module handles the registration and management of all HOLMES actions.
"""

from typing import Dict, Type
from .base import BaseAction

# Import all action classes
from .revenue_action import RevenueAction
from .traffic_action import TrafficAction  
from .high_timeouts_action import HighTimeoutsAction
from .error_action import ErrorAction

# Traffic sub-actions are now consolidated into TrafficAction
# from .ad_requests_drop_action import AdRequestsDropAction
# from .bid_requests_drop_action import BidRequestsDropAction  
# from .sharp_bid_drop_action import SharpBidDropAction

# Add more imports as you create new action files
# from .error_action import ErrorAction
# from .latency_action import LatencyAction
# etc.


class ActionRegistry:
    """Registry to manage all HOLMES actions"""
    
    def __init__(self):
        self.actions: Dict[str, BaseAction] = {}
    
    def register(self, action_class: Type[BaseAction]):
        """Register a new action class"""
        action_instance = action_class()
        handled_actions = action_instance.get_handled_actions()
        
        # Register all handled action IDs to this instance
        for action_id in handled_actions:
            self.actions[action_id] = action_instance
        
        primary_action = action_instance.get_action_id()
        print(f"✅ Registered action: {primary_action} - {action_instance.get_description()}")
        if len(handled_actions) > 1:
            other_actions = [a for a in handled_actions if a != primary_action]
            print(f"    Also handles: {', '.join(other_actions)}")
    
    def get_action(self, action_id: str) -> BaseAction:
        """Get an action by its ID"""
        return self.actions.get(action_id)
    
    def list_actions(self) -> Dict[str, str]:
        """List all registered actions with their descriptions"""
        return {
            action_id: action.get_description() 
            for action_id, action in self.actions.items()
        }


# Global registry instance
_registry = ActionRegistry()


def register_all_actions(app):
    """Register all actions with the Slack app"""
    
    # Register all action classes
    _registry.register(RevenueAction)
    _registry.register(TrafficAction)  # Now handles ad_requests_drop, bid_requests_drop, sharp_bid_drop
    _registry.register(HighTimeoutsAction)
    _registry.register(ErrorAction)  # Now handles select_error, 5xx_errors_dc
    
    # Add more registrations as you create new actions:
    # _registry.register(ErrorAction)
    # _registry.register(LatencyAction)
    # etc.
    
    # Register handlers with Slack app
    for action_id, action in _registry.actions.items():
        app.action(action_id)(action.handle)
        print(f"🔗 Connected action {action_id} to Slack app")
    
    print(f"📋 Total registered actions: {len(_registry.actions)}")
    return _registry


def get_registry() -> ActionRegistry:
    """Get the global action registry"""
    return _registry