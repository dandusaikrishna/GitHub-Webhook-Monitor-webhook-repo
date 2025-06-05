// MongoDB initialization script
db = db.getSiblingDB('github_webhooks');

// Create the events collection
db.createCollection('events');

// Create indexes for better performance
db.events.createIndex({ "created_at": -1 });
db.events.createIndex({ "request_id": 1 });
db.events.createIndex({ "action": 1 });
db.events.createIndex({ "author": 1 });

// Insert a sample document to verify setup
db.events.insertOne({
    "id": "sample_event_001",
    "author": "System",
    "action": "SETUP",
    "from_branch": "",
    "to_branch": "main",
    "timestamp": "1st June 2025 - 12:00 PM UTC",
    "request_id": "setup_001",
    "created_at": new Date()
});

print("MongoDB initialization completed successfully!");
