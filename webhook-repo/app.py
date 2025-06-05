from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from datetime import datetime
import json
import os
from bson import ObjectId

app = Flask(__name__, template_folder='templates')

# MongoDB Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/github_webhooks")
mongo = PyMongo(app)

class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)

app.json_encoder = JSONEncoder

def format_timestamp(timestamp_str):
    """Convert GitHub timestamp to readable format"""
    try:
        # Parse GitHub timestamp (ISO format)
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        # Format as required: "1st April 2021 - 9:30 PM UTC"
        day = dt.day
        if 4 <= day <= 20 or 24 <= day <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][day % 10 - 1]
        
        formatted_date = dt.strftime(f"{day}{suffix} %B %Y - %I:%M %p UTC")
        return formatted_date
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
        return timestamp_str

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events"""
    try:
        # Get the event type from headers
        event_type = request.headers.get('X-GitHub-Event')
        payload = request.json
        
        if not payload:
            return jsonify({"error": "No payload received"}), 400
        
        # Initialize document structure
        document = {
            "id": None,
            "author": "",
            "action": "",
            "from_branch": "",
            "to_branch": "",
            "timestamp": "",
            "request_id": "",
            "created_at": datetime.utcnow()
        }
        
        if event_type == 'push':
            # Handle PUSH events
            ref = payload.get('ref', '')
            branch = ref.replace('refs/heads/', '') if ref.startswith('refs/heads/') else ref
            
            document.update({
                "id": payload.get('head_commit', {}).get('id', ''),
                "author": payload.get('pusher', {}).get('name', '') or payload.get('head_commit', {}).get('author', {}).get('name', ''),
                "action": "PUSH",
                "to_branch": branch,
                "timestamp": payload.get('head_commit', {}).get('timestamp', ''),
                "request_id": payload.get('head_commit', {}).get('id', '')
            })
            
        elif event_type == 'pull_request':
            # Handle PULL REQUEST events
            pr = payload.get('pull_request', {})
            action = payload.get('action', '')
            
            # Only process opened, closed, or merged pull requests
            if action in ['opened', 'closed', 'merged']:
                if action == 'merged':
                    # This is actually a MERGE action
                    document.update({
                        "id": str(pr.get('id', '')),
                        "author": pr.get('merged_by', {}).get('login', '') or pr.get('user', {}).get('login', ''),
                        "action": "MERGE",
                        "from_branch": pr.get('head', {}).get('ref', ''),
                        "to_branch": pr.get('base', {}).get('ref', ''),
                        "timestamp": pr.get('merged_at', ''),
                        "request_id": str(pr.get('id', ''))
                    })
                else:
                    # Regular PULL_REQUEST
                    document.update({
                        "id": str(pr.get('id', '')),
                        "author": pr.get('user', {}).get('login', ''),
                        "action": "PULL_REQUEST",
                        "from_branch": pr.get('head', {}).get('ref', ''),
                        "to_branch": pr.get('base', {}).get('ref', ''),
                        "timestamp": pr.get('created_at', '') if action == 'opened' else pr.get('updated_at', ''),
                        "request_id": str(pr.get('id', ''))
                    })
            else:
                return jsonify({"message": "PR action not tracked"}), 200
        
        else:
            return jsonify({"message": f"Event type {event_type} not supported"}), 200
        
        # Format timestamp
        if document["timestamp"]:
            document["timestamp"] = format_timestamp(document["timestamp"])
        
        # Insert into MongoDB
        result = mongo.db.events.insert_one(document)
        print(f"Inserted document with ID: {result.inserted_id}")
        print(f"Document: {document}")
        
        return jsonify({"message": "Webhook processed successfully", "id": str(result.inserted_id)}), 200
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """API endpoint to get latest events for polling"""
    try:
        # Get latest 50 events, sorted by creation time (newest first)
        events = list(mongo.db.events.find().sort("created_at", -1).limit(50))
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
            
        return jsonify(events), 200
    except Exception as e:
        print(f"Error fetching events: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Serve the main UI"""
    return render_template('index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        mongo.db.events.find_one()
        return jsonify({"status": "healthy", "mongodb": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == '__main__':
    # Create indexes for better performance
    try:
        mongo.db.events.create_index([("created_at", -1)])
        mongo.db.events.create_index([("request_id", 1)])
        print("Database indexes created successfully")
    except Exception as e:
        print(f"Error creating indexes: {e}")
    
    print("Starting Flask webhook receiver...")
    print("Webhook endpoint: http://localhost:5001/webhook")
    print("UI available at: http://localhost:5001")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
