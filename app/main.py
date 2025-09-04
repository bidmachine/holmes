import os
import sys
import time
from datetime import datetime
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from flask import Flask

# Add the current directory to Python path so we can import actions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Slack app
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Configuration
MONITORING_URLS = {
    'main_dashboard': 'https://pivot.bidmachine.io/pivot/c/9585/-Exchange-_Daily_performance_monitoring',
    'health_dashboard': 'https://grafana.appodeal.com/d/cde3ebce-204e-4f1d-967f-1a915e3ba429/health-checklist',
    'rollouts_audit': 'https://rollouts-ui.bidmachine.io/audit',
    'temporal_dashboard': 'https://temporal.bidmachine.io/namespaces/default/workflows/',
    'sro_updates': 'https://appodeal.slack.com/archives/C08T3SYMHCM/',
    'obd_dashboard': 'https://dbc-4cdcc63c-7af8.cloud.databricks.com/dashboardsv3/01f03580ca8d1556b8e4f0e36ca3a37b/published'
}

TEAM_CONTACTS = {
    'exchange_revenue_ops': 't',  # Replace with actual Slack user IDs
    'baptiste_poirier': 't',
    'nika_kozhukh': 't',
    'sergei_smirnov': 't',
    'celine_tran': 't', #U5678901234
}

CHANNELS = {
    'incidents': 'C09EB37M4HE',  # #bidmachine_incidents
    'okr': 'C09EB37M4HE',  # #bidmachine_okr
    'devops': 'C09EB37M4HE',  # #bidmachine_devops
    'experiments': 'C09EB37M4HE',  # #bidmachine_experiments
}

# Alert monitoring configuration
MONITORED_CHANNELS = [
    'C08T82KB0M7',  # Main incidents channel
    'C09EB37M4HE',  # Updated channel ID
    # Add other channels where alerts are posted
]

# Alert detection patterns
ALERT_PATTERNS = {
    'revenue': [
        'overspend', 'budget exceeded', 'cost spike', 'spend alert', 
        'revenue drop', 'massive spend', 'budget breach', '$100k'
    ],
    'traffic': [
        'traffic drop', 'request drop', 'bid drop', 'impression drop',
        'ad requests', 'bid requests', 'fill rate', 'ctr drop'
    ],
    'errors': [
        '5xx', '500 error', '503 error', 'error rate', 'timeout',
        'service unavailable', 'gateway timeout', 'internal server error'
    ],
    'latency': [
        'latency', 'slow response', 'response time', 'timeout',
        'degradation', 'p95', 'p99', 'milliseconds'
    ],
    'data': [
        'data discrepancy', 'reporting mismatch', 'analytics', 
        'data inconsistency', 'sync error'
    ]
}


def classify_alert(text):
    """Classify alert based on text content"""
    text_lower = text.lower()
    
    scores = {}
    for category, patterns in ALERT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            if pattern.lower() in text_lower:
                score += 1
        scores[category] = score
    
    # Return the category with highest score, or None if no patterns match
    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return None


def get_alert_response_blocks(alert_type, original_message, user_id):
    """Get response blocks for detected alert"""
    timestamp = int(time.time())
    
    if alert_type == 'revenue':
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '🚨 HOLMES: Revenue Alert Detected'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Alert detected by:* <@{user_id}>\n*Time:* <!date^{timestamp}^{{date_pretty}} at {{time}}|{timestamp}>\n\n*🎯 INVESTIGATION RECOMMENDED:*\n• Check <{MONITORING_URLS["main_dashboard"]}|Performance Dashboard>\n• Review <{MONITORING_URLS["temporal_dashboard"]}|Temporal workflows>\n• Verify bidder capping system status'
                }
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '🔍 Start Investigation'},
                        'value': 'start_revenue_investigation',
                        'action_id': 'start_revenue_investigation',
                        'style': 'primary'
                    }
                ]
            }
        ]
    elif alert_type == 'traffic':
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '📊 HOLMES: Traffic Alert Detected'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Alert detected by:* <@{user_id}>\n*Time:* <!date^{timestamp}^{{date_pretty}} at {{time}}|{timestamp}>\n\n*🎯 INVESTIGATION RECOMMENDED:*\n• Check <{MONITORING_URLS["rollouts_audit"]}|Rollouts audit>\n• Review <{MONITORING_URLS["sro_updates"]}|SRO updates>\n• Monitor bid request patterns'
                }
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '🔍 Start Investigation'},
                        'value': 'start_traffic_investigation',
                        'action_id': 'start_traffic_investigation',
                        'style': 'primary'
                    }
                ]
            }
        ]
    elif alert_type == 'errors':
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '⚠️ HOLMES: Error Rate Alert Detected'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Alert detected by:* <@{user_id}>\n*Time:* <!date^{timestamp}^{{date_pretty}} at {{time}}|{timestamp}>\n\n*🎯 INVESTIGATION RECOMMENDED:*\n• Check infrastructure status\n• Review recent deployments\n• Monitor service health'
                }
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '🔍 Start Investigation'},
                        'value': 'start_error_investigation',
                        'action_id': 'start_error_investigation',
                        'style': 'primary'
                    }
                ]
            }
        ]
    else:
        return [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '🕵️ HOLMES: Alert Detected'}
            },
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Alert detected by:* <@{user_id}>\n*Time:* <!date^{timestamp}^{{date_pretty}} at {{time}}|{timestamp}>\n\n*🎯 INVESTIGATION AVAILABLE:*\nHOLMES can help investigate this alert.'
                }
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '🔍 Start Investigation'},
                        'value': 'start_investigation',
                        'action_id': 'start_investigation',
                        'style': 'primary'
                    }
                ]
            }
        ]


def get_initial_decision_blocks():
    """Initial decision tree blocks"""
    return [
        {
            'type': 'header',
            'text': {
                'type': 'plain_text',
                'text': '🕵️ HOLMES: Health Operations & Live Monitoring Expert System'
            }
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': '*First, verify in monitoring dashboards:*\n• <{}|Performance Monitoring Dashboard>\n• <{}|Health Dashboard>\n\n*What type of anomaly detected?*'.format(
                    MONITORING_URLS["main_dashboard"],
                    MONITORING_URLS["health_dashboard"]
                )
            }
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '💰 Revenue/Spend Issue'},
                    'value': 'revenue_issue',
                    'action_id': 'select_revenue'
                },
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '📊 Traffic Issue'},
                    'value': 'traffic_issue',
                    'action_id': 'select_traffic'
                }
            ]
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '⚠️ Error Rate Issue'},
                    'value': 'error_issue',
                    'action_id': 'select_error'
                },
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '🐌 Latency Issue'},
                    'value': 'latency_issue',
                    'action_id': 'select_latency'
                }
            ]
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '📋 Data Discrepancy'},
                    'value': 'data_discrepancy',
                    'action_id': 'select_discrepancy'
                }
            ]
        }
    ]





def get_latency_options_blocks():
    """Latency issue option blocks"""
    return [
        {
            'type': 'header',
            'text': {'type': 'plain_text', 'text': '🐌 Latency Issue Analysis'}
        },
        {
            'type': 'section',
            'text': {'type': 'mrkdwn', 'text': '*What kind of latency pattern detected?*'}
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '📈 35-50% degradation in specific DC'},
                    'value': 'latency_degradation_dc',
                    'action_id': 'latency_degradation_dc'
                },
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '🌍 Cross-DC routing issues'},
                    'value': 'cross_dc_routing',
                    'action_id': 'cross_dc_routing'
                }
            ]
        }
    ]


def get_critical_overspend_blocks(user_id, timestamp):
    """Critical overspend incident blocks"""
    exchange_ops_id = TEAM_CONTACTS.get('exchange_revenue_ops', 'exchange_revenue_ops')

    return [
        {
            'type': 'header',
            'text': {'type': 'plain_text', 'text': '🔥 CRITICAL: Massive Overspend (>$100K)'}
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*Reported by:* <@{user_id}>\n*Time:* <!date^{timestamp}^{{date_pretty}} at {{time}}|{timestamp}>\n*Investigation:* HOLMES System'
            }
        },
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'*🎯 PRIMARY SUSPECT:* Bidder Capping System Failure\n*🔧 LIKELY CAUSE:* Druid Database unavailability\n\n*⚡ CHECK IMMEDIATELY:*\n• <{MONITORING_URLS["temporal_dashboard"]}|Temporal workflows>\n• Bidder settings in BM Dashboard\n• Druid database status\n\n*👥 ESCALATION:* <@{exchange_ops_id}>'
            }
        },
        {
            'type': 'actions',
            'elements': [
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '✅ Druid is Available'},
                    'value': 'druid_available',
                    'action_id': 'druid_check_yes',
                    'style': 'primary'
                },
                {
                    'type': 'button',
                    'text': {'type': 'plain_text', 'text': '❌ Druid is Down/Unavailable'},
                    'value': 'druid_unavailable',
                    'action_id': 'druid_check_no',
                    'style': 'danger'
                }
            ]
        }
    ]





# Slash command handler
@app.command("/holmes")
def handle_holmes_command(ack, body, client, respond):
    """Handle /holmes slash command"""
    ack()
    
    print(f"Received /holmes command from channel: {body.get('channel_id', 'unknown')}")
    print(f"User: {body.get('user_id', 'unknown')}")

    try:
        # Post message publicly in the channel instead of ephemeral response
        client.chat_postMessage(
            channel=body.get('channel_id'),
            blocks=get_initial_decision_blocks(),
            text="🕵️ HOLMES: Platform Investigation System"
        )
        print("Successfully sent public message")
    except Exception as e:
        print(f"Error sending initial message: {e}")
        # Fallback to direct message if channel fails
        try:
            client.chat_postMessage(
                channel=body.get('user_id'),  # Send DM to user
                blocks=get_initial_decision_blocks(),
                text="🕵️ HOLMES: Platform Investigation System"
            )
            print(f"Sent as DM to user {body.get('user_id')}")
        except Exception as e2:
            print(f"Error sending DM: {e2}")


# Alert detection message handler
@app.event("message")
def handle_alert_messages(message, say, client):
    """Detect alerts in monitored channels and respond with investigation help"""
    
    print(f"📨 Received message event: channel={message.get('channel')}, user={message.get('user')}, subtype={message.get('subtype')}")
    
    # Skip bot messages
    if message.get('bot_id') or message.get('subtype') == 'bot_message':
        print(f"⏭️ Skipping bot message")
        return
    
    channel = message.get('channel')
    text = message.get('text', '')
    user = message.get('user', '')
    ts = message.get('ts', '')
    
    print(f"📍 Channel: {channel}, Monitored: {MONITORED_CHANNELS}")
    
    # Check if channel is monitored OR if it's a DM for testing
    if not channel or (channel not in MONITORED_CHANNELS and not channel.startswith('D')):
        print(f"⏭️ Channel {channel} not monitored")
        return
    
    print(f"🔍 Checking message: {text[:100]}...")
    
    # Classify the alert
    alert_type = classify_alert(text)
    
    if alert_type:
        print(f"🚨 Alert detected! Type: {alert_type}, User: {user}")
        
        try:
            # Respond in a thread to the original message
            client.chat_postMessage(
                channel=channel,
                thread_ts=ts,  # This makes it a thread reply
                blocks=get_alert_response_blocks(alert_type, text, user),
                text=f"🕵️ HOLMES: {alert_type.title()} alert detected - Investigation assistance available"
            )
            print(f"✅ Posted HOLMES alert response in thread for {alert_type} alert")
            
        except Exception as e:
            print(f"❌ Error posting alert response: {e}")
    else:
        print(f"ℹ️ No alert patterns detected in message")


# Button action handlers


@app.action("select_discrepancy")
def handle_discrepancy_selection(ack, body, respond, client):
    """Handle data discrepancy selection"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Button clicked: select_discrepancy by user {user_id}")
    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show what was selected (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="✅ User selected: *Data Discrepancy*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'✅ <@{user_id}> selected: *Data Discrepancy*'
                    }
                }
            ]
        )
        
        # Post new message in thread with discrepancy analysis
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=[
                {
                    'type': 'header',
                    'text': {'type': 'plain_text', 'text': '📋 Data Discrepancy Analysis'}
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': 'Data discrepancy investigation started. Please check:\n• Revenue reporting differences\n• Analytics data consistency\n• Database synchronization issues'
                    }
                }
            ],
            text="Data Discrepancy Analysis"
        )
        print("✅ Posted new message with discrepancy analysis")
    except Exception as e:
        print(f"❌ Error handling discrepancy selection: {e}")
        print(f"Full body keys: {list(body.keys())}")






# Traffic sub-option handlers









# Latency sub-option handlers  
@app.action("latency_degradation_dc")
def handle_latency_degradation_dc(ack, body, respond, client):
    """Handle latency degradation in specific DC"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Button clicked: latency_degradation_dc by user {user_id}")

    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show what was selected (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="✅ User selected: *Latency Degradation in DC*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'✅ <@{user_id}> selected: *Latency Degradation in DC*'
                    }
                }
            ]
        )
        
        # Post new message in thread with investigation steps
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=[
                {
                    'type': 'header',
                    'text': {'type': 'plain_text', 'text': '📈 Latency Degradation Investigation'}
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*Investigation started by:* <@{user_id}>\n\n*INVESTIGATION STEPS:*\n• Check CPU and memory usage in affected DC\n• Verify network routing configuration\n• Review recent deployment changes\n• Monitor database connection pool status'
                    }
                }
            ],
            text="Latency Degradation Investigation Steps"
        )
        print("✅ Successfully handled latency_degradation_dc")
    except Exception as e:
        print(f"❌ Error handling latency_degradation_dc: {e}")


@app.action("cross_dc_routing")
def handle_cross_dc_routing(ack, body, respond, client):
    """Handle cross-DC routing issues"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Button clicked: cross_dc_routing by user {user_id}")

    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show what was selected (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="✅ User selected: *Cross-DC Routing Issues*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'✅ <@{user_id}> selected: *Cross-DC Routing Issues*'
                    }
                }
            ]
        )
        
        # Post new message in thread with investigation steps
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=[
                {
                    'type': 'header',
                    'text': {'type': 'plain_text', 'text': '🌍 Cross-DC Routing Issues Investigation'}
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*Investigation started by:* <@{user_id}>\n\n*INVESTIGATION STEPS:*\n• Check inter-DC network connectivity\n• Verify load balancer routing rules\n• Review DNS resolution times\n• Monitor cross-region latency metrics'
                    }
                }
            ],
            text="Cross-DC Routing Investigation Steps"
        )
        print("✅ Successfully handled cross_dc_routing")
    except Exception as e:
        print(f"❌ Error handling cross_dc_routing: {e}")


# Alert investigation starters
@app.action("start_revenue_investigation")
def handle_start_revenue_investigation(ack, body, respond, client):
    """Start revenue investigation from alert"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Starting revenue investigation from alert by user {user_id}")
    
    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show investigation started (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="🔍 Investigation Started: *Revenue Issue*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'🔍 <@{user_id}> started: *Revenue Issue Investigation*'
                    }
                }
            ]
        )
        
        # Post new message in thread with revenue options
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=get_revenue_options_blocks(),
            text="Revenue Issue Investigation Options"
        )
        print("✅ Started revenue investigation")
    except Exception as e:
        print(f"❌ Error starting revenue investigation: {e}")
        print(f"Full body keys: {list(body.keys())}")


@app.action("start_traffic_investigation")
def handle_start_traffic_investigation(ack, body, respond, client):
    """Start traffic investigation from alert"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Starting traffic investigation from alert by user {user_id}")
    
    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show investigation started (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="🔍 Investigation Started: *Traffic Issue*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'🔍 <@{user_id}> started: *Traffic Issue Investigation*'
                    }
                }
            ]
        )
        
        # Post new message in thread with traffic options
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=get_traffic_options_blocks(),
            text="Traffic Issue Investigation Options"
        )
        print("✅ Started traffic investigation")
    except Exception as e:
        print(f"❌ Error starting traffic investigation: {e}")
        print(f"Full body keys: {list(body.keys())}")


@app.action("start_error_investigation")
def handle_start_error_investigation(ack, body, respond, client):
    """Start error investigation from alert"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Starting error investigation from alert by user {user_id}")
    
    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show investigation started (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="🔍 Investigation Started: *Error Rate Issue*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'🔍 <@{user_id}> started: *Error Rate Issue Investigation*'
                    }
                }
            ]
        )
        
        # Post new message in thread with error options
        error_blocks = [
            {
                'type': 'header',
                'text': {'type': 'plain_text', 'text': '⚠️ Error Rate Issue Analysis'}
            },
            {
                'type': 'section',
                'text': {'type': 'mrkdwn', 'text': '*What kind of error pattern detected?*'}
            },
            {
                'type': 'actions',
                'elements': [
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '🏗️ 5xx errors in specific DC'},
                        'value': '5xx_errors_dc',
                        'action_id': '5xx_errors_dc'
                    },
                    {
                        'type': 'button',
                        'text': {'type': 'plain_text', 'text': '⏱️ High timeout rates'},
                        'value': 'high_timeouts',
                        'action_id': 'high_timeouts'
                    }
                ]
            }
        ]
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=error_blocks,
            text="Error Rate Issue Investigation Options"
        )
        print("✅ Started error investigation")
    except Exception as e:
        print(f"❌ Error starting error investigation: {e}")
        print(f"Full body keys: {list(body.keys())}")


@app.action("start_investigation")
def handle_start_general_investigation(ack, body, respond, client):
    """Start general investigation from alert"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Starting general investigation from alert by user {user_id}")
    
    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show investigation started (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="🔍 Investigation Started: *General Analysis*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'🔍 <@{user_id}> started: *HOLMES Investigation*'
                    }
                }
            ]
        )
        
        # Post new message in thread with investigation options
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=get_initial_decision_blocks(),
            text="HOLMES Investigation Options"
        )
        print("✅ Started general investigation")
    except Exception as e:
        print(f"❌ Error starting general investigation: {e}")
        print(f"Full body keys: {list(body.keys())}")


@app.action("select_latency")
def handle_latency_selection(ack, body, respond, client):
    """Handle latency issue selection"""
    ack()
    user_id = body.get('user', {}).get('id', 'unknown')
    print(f"🔍 Button clicked: select_latency by user {user_id}")
    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show what was selected (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="✅ User selected: *Latency Issue*",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'✅ <@{user_id}> selected: *Latency Issue*'
                    }
                }
            ]
        )
        
        # Post new message in thread with latency options
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=get_latency_options_blocks(),
            text="Latency Issue Analysis Options"
        )
        print("✅ Posted new message with latency options")
    except Exception as e:
        print(f"❌ Error handling latency selection: {e}")
        print(f"Full body keys: {list(body.keys())}")


@app.action("massive_overspend")
def handle_massive_overspend(ack, body, respond, client):
    """Handle massive overspend critical incident"""
    ack()

    user_id = body.get('user', {}).get('id', 'unknown')
    timestamp = int(time.time())
    print(f"🔍 Button clicked: massive_overspend by user {user_id}")

    try:
        # Get channel and thread info
        channel = body.get('channel', {}).get('id') or body.get('container', {}).get('channel_id')
        message_ts = body.get('message', {}).get('ts') or body.get('container', {}).get('message_ts')
        thread_ts = body.get('message', {}).get('thread_ts') or message_ts
        
        # Update original message to show what was selected (visible to all)
        client.chat_update(
            channel=channel,
            ts=message_ts,
            text="⚠️ MASSIVE OVERSPEND Selected",
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'🚨 <@{user_id}> selected: *MASSIVE OVERSPEND (>$100K)*'
                    }
                }
            ]
        )
        
        # Post critical alert in thread
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            blocks=[
                {
                    'type': 'header',
                    'text': {'type': 'plain_text', 'text': '🔥 CRITICAL: Massive Overspend Investigation'}
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*Investigator:* <@{user_id}>\n*Time:* <!date^{timestamp}^{{date_pretty}} at {{time}}|{timestamp}>\n\n*🎯 PRIMARY SUSPECT:* Bidder Capping System Failure\n*🔧 LIKELY CAUSE:* Druid Database unavailability\n\n*⚡ IMMEDIATE ACTIONS:*\n\n1️⃣ Check <{MONITORING_URLS["temporal_dashboard"]}|Temporal workflows>\n2️⃣ Verify Bidder settings in BM Dashboard\n3️⃣ Check Druid database status\n4️⃣ Monitor real-time spend\n\n*👥 ESCALATION REQUIRED:* Notify Exchange Revenue Ops team immediately!'
                    }
                }
            ],
            text="🔥 CRITICAL: Massive Overspend Investigation"
        )
        
        # Also post to incidents channel if configured
        if CHANNELS.get('incidents'):
            client.chat_postMessage(
                channel=CHANNELS['incidents'],
                text=f"🚨 CRITICAL INCIDENT: Massive Overspend Detected by <@{user_id}>",
                blocks=[
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'🚨 *CRITICAL INCIDENT ALERT*\n\n*Reported by:* <@{user_id}>\n*Type:* Massive Overspend (>$100K)\n*Investigation:* In progress\n\n*See thread for details:* <#{channel}>'
                        }
                    }
                ]
            )

        print("✅ Successfully handled massive_overspend")
    except Exception as e:
        print(f"❌ Error handling massive overspend: {e}")






@app.action("druid_check_no")
def handle_druid_unavailable(ack, body, client):
    """Handle Druid unavailable scenario"""
    ack()

    try:
        client.chat_update(
            channel=body['channel']['id'],
            ts=body['message']['ts'],
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '🔥 *CRITICAL ACTION REQUIRED*\n\n*ROOT CAUSE CONFIRMED:* Druid Database Unavailable\n*BIDDER CAPPING SYSTEM OFFLINE*'
                    },
                    'accessory': {
                        'type': 'image',
                        'image_url': 'https://via.placeholder.com/50x50/e53e3e/ffffff?text=!',
                        'alt_text': 'Critical'
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '*⚡ IMMEDIATE ACTIONS:*\n1. 🛑 *Manually disable affected bidder in BM Dashboard*\n2. 📞 *Contact DevOps team to restore Druid*\n3. 📊 *Monitor spend in real-time*\n4. 📝 *Document total overspend amount*\n\n*📋 FOLLOW-UP:*\n• Implement real-time billing events pipeline\n• Review Druid SLA and backup procedures'
                    }
                }
            ]
        )
    except Exception as e:
        print(f"Error handling Druid unavailable: {e}")


@app.action("sro_deploy_found")
def handle_sro_deployment_issue(ack, body, client):
    """Handle SRO deployment issue"""
    ack()

    baptiste_id = TEAM_CONTACTS.get('baptiste_poirier', 'baptiste.poirier')
    nika_id = TEAM_CONTACTS.get('nika_kozhukh', 'nika.kozhukh')

    try:
        client.chat_update(
            channel=body['channel']['id'],
            ts=body['message']['ts'],
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '📉 *SRO DEPLOYMENT ISSUE CONFIRMED*\n\n*ROOT CAUSE:* Recent SRO model file deployment'
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*⚡ IMMEDIATE ACTIONS:*\n1. 🔄 *Rollback SRO file to previous version*\n2. 📊 *Monitor bid request recovery*\n3. 🔍 *Check notebook file naming for errors*\n\n*👥 NOTIFY:* <@{baptiste_id}> <@{nika_id}>\n*📍 CHECK:* <{MONITORING_URLS["sro_updates"]}|SRO Updates Channel>'
                    }
                }
            ]
        )
    except Exception as e:
        print(f"Error handling SRO deployment issue: {e}")


@app.action("sdk_activation_found")
def handle_sdk_issue(ack, body, client):
    """Handle SDK activation issue"""
    ack()

    sergei_id = TEAM_CONTACTS.get('sergei_smirnov', 'sergei.smirnov')
    celine_id = TEAM_CONTACTS.get('celine_tran', 'celine.tran')

    try:
        client.chat_update(
            channel=body['channel']['id'],
            ts=body['message']['ts'],
            blocks=[
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': '🏗️ *SDK FEATURE ISSUE CONFIRMED*\n\n*ROOT CAUSE:* Recent SDK feature activation without proper infrastructure'
                    }
                },
                {
                    'type': 'section',
                    'text': {
                        'type': 'mrkdwn',
                        'text': f'*⚡ IMMEDIATE ACTIONS:*\n1. 🛑 *Disable new SDK features immediately*\n2. 🔍 *Check Analytics V2 status in affected region*\n3. 📊 *Monitor error rate recovery*\n\n*👥 CONTACTS:* <@{sergei_id}> <@{celine_id}>\n*📍 VERIFY:* Infrastructure availability in affected DC'
                    }
                }
            ]
        )
    except Exception as e:
        print(f"Error handling SDK issue: {e}")


# Flask integration for existing backend
def create_flask_app():

    flask_app = Flask(__name__)
    handler = SlackRequestHandler(app)

    @flask_app.route("/slack/events", methods=["POST"])
    def slack_events():
        from flask import request, jsonify
        print(f"Received request to /slack/events")
        print(f"Headers: {dict(request.headers)}")
        print(f"Content-Type: {request.content_type}")
        
        # Log the raw body for debugging
        body = request.get_data(as_text=True)
        print(f"Body: {body[:500]}")  # First 500 chars
        
        # Handle URL verification challenge
        if request.content_type == 'application/json':
            data = request.get_json()
            if data and data.get('type') == 'url_verification':
                print(f"Handling URL verification challenge")
                return jsonify({"challenge": data.get('challenge')})
        
        # Handle normal Slack requests
        return handler.handle(request)
    
    # Add a specific slash command route as fallback
    @flask_app.route("/slack/slash", methods=["POST"])
    def slack_slash():
        from flask import request
        print(f"Received SLASH command to /slack/slash")
        print(f"Form data: {dict(request.form)}")
        return handler.handle(request)

    # Health check endpoint
    @flask_app.route("/health")
    def health_check():
        return {"status": "HOLMES system operational", "timestamp": datetime.now().isoformat()}

    return flask_app


# Main function
def main():
    """Main function to run HOLMES bot"""
    print("🕵️ Starting HOLMES: Health Operations & Live Monitoring Expert System")
    print("Available commands: /holmes")
    print(f"Monitoring channels: {list(CHANNELS.values())}")
    
    # Register all actions
    print("📋 Registering HOLMES actions...")
    from actions import register_all_actions
    register_all_actions(app)

    # Check if Socket Mode is enabled
    if os.environ.get("SLACK_APP_TOKEN"):
        print("Starting in Socket Mode...")
        print(f"App token: {os.environ['SLACK_APP_TOKEN'][:20]}...")
        try:
            from slack_bolt.adapter.socket_mode import SocketModeHandler
            handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
            handler.start()
        except Exception as e:
            print(f"Socket Mode failed to start: {e}")
            print("Falling back to HTTP mode...")
            flask_app = create_flask_app()
            flask_app.run(host="0.0.0.0", port=3000)
    else:
        # Use Flask for webhook mode
        flask_app = create_flask_app()
        # Use port 3000 inside container (mapped to 4241 outside)
        port = 3000
        
        if os.environ.get("FLASK_ENV") == "development":
            flask_app.run(debug=True, host="0.0.0.0", port=port)
        else:
            flask_app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()