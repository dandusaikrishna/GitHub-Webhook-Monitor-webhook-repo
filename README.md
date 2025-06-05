# GitHub Webhook Monitor

A Flask-based application that receives GitHub webhooks, stores them in MongoDB, and displays real-time repository activity through a clean web interface.

## 🚀 Features

- **Real-time monitoring** of GitHub repository activities
- **Webhook processing** for PUSH, PULL_REQUEST, and MERGE actions
- **MongoDB storage** with optimized schema
- **Responsive UI** with live polling every 15 seconds
- **Clean, modern interface** with activity categorization

## 📋 Requirements

- Python 3.8+
- MongoDB 4.0+
- GitHub repository with webhook access

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone <your-webhook-repo-url>
cd webhook-repo
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MongoDB

**Option A: Local MongoDB**
```bash
# Install MongoDB locally
# Start MongoDB service
mongod --dbpath /path/to/your/db
```

**Option B: MongoDB Atlas (Cloud)**
1. Create a free MongoDB Atlas account
2. Create a new cluster
3. Get your connection string
4. Set the `MONGO_URI` environment variable

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
MONGO_URI=mongodb://localhost:27017/github_webhooks
FLASK_ENV=development
FLASK_DEBUG=True
```

For MongoDB Atlas:
```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/github_webhooks?retryWrites=true&w=majority
```

## 🏃‍♂️ Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at:
- **Main UI**: http://localhost:5000
- **Webhook Endpoint**: http://localhost:5000/webhook
- **API Endpoint**: http://localhost:5000/api/events
- **Health Check**: http://localhost:5000/health

### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔗 GitHub Webhook Setup

### 1. Create Action Repository

1. Create a new repository called `action-repo`
2. Add some initial files and commit them

### 2. Configure Webhook

1. Go to your `action-repo` → Settings → Webhooks
2. Click "Add webhook"
3. Configure the webhook:
   - **Payload URL**: `http://your-domain.com:5000/webhook` (or use ngrok for local testing)
   - **Content type**: `application/json`
   - **Secret**: (optional, but recommended for security)
   - **SSL verification**: Enable if using HTTPS
   - **Events**: Select individual events:
     - ✅ Pushes
     - ✅ Pull requests
     - ✅ Branch or tag creation
     - ✅ Branch or tag deletion

### 3. Test the Webhook

1. Make a push to your `action-repo`
2. Create a pull request
3. Merge a pull request
4. Check the webhook monitor UI for real-time updates

## 🧪 Testing Locally with ngrok

For local development, use ngrok to expose your local server:

```bash
# Install ngrok
npm install -g ngrok

# Expose local port 5000
ngrok http 5000
```

Use the ngrok URL as your webhook payload URL in GitHub settings.

## 📊 API Endpoints

### Webhook Receiver
- **POST** `/webhook` - Receives GitHub webhook events
- **Headers**: `X-GitHub-Event` (required)
- **Body**: GitHub webhook payload (JSON)

### Events API
- **GET** `/api/events` - Returns latest events (max 50)
- **Response**: Array of event objects

### Health Check
- **GET** `/health` - Application health status
- **Response**: MongoDB connection status

## 🗄️ MongoDB Schema

```javascript
{
  "_id": ObjectId,
  "id": String,           // GitHub event ID
  "author": String,       // Author/pusher name
  "action": String,       // "PUSH", "PULL_REQUEST", or "MERGE"
  "from_branch": String,  // Source branch (for PR/merge)
  "to_branch": String,    // Target branch
  "timestamp": String,    // Formatted timestamp
  "request_id": String,   // GitHub request ID
  "created_at": ISODate   // Document creation time
}
```

## 🎨 Display Formats

The UI displays events in the following formats:

### PUSH Action
```
{author} pushed to {to_branch} on {timestamp}
Example: "Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC
```

### PULL_REQUEST Action
```
{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}
Example: "Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC
```

### MERGE Action
```
{author} merged branch {from_branch} to {to_branch} on {timestamp}
Example: "Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC
```

## 🔍 Monitoring

The UI automatically:
- Polls for new events every 15 seconds
- Shows connection status
- Displays event count
- Shows last update time
- Handles errors gracefully

## 🛠️ Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Check if MongoDB is running
   - Verify connection string in `.env`
   - Check network connectivity for Atlas

2. **Webhook Not Receiving Events**
   - Verify webhook URL is accessible from GitHub
   - Check GitHub webhook delivery logs
   - Ensure correct event types are selected

3. **UI Not Updating**
   - Check browser console for errors
   - Verify API endpoint is accessible
   - Check if events are being stored in MongoDB

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 Project Structure

```
webhook-repo/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── .env              # Environment variables (create this)
├── templates/
│   └── index.html    # UI template
└── static/           # Static files (if needed)
```

## 🚀 Deployment

### Using Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```

2. Set environment variables in Heroku dashboard
3. Deploy using Git or GitHub integration

### Using Docker

1. Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

2. Build and run:
```bash
docker build -t webhook-monitor .
docker run -p 5000:5000 webhook-monitor
```

## 🔐 Security Considerations

1. **Webhook Secret**: Use GitHub webhook secrets to verify payload authenticity
2. **HTTPS**: Always use HTTPS in production
3. **Rate Limiting**: Implement rate limiting for webhook endpoint
4. **Input Validation**: Validate all incoming webhook data
5. **MongoDB Security**: Use authentication and encryption for MongoDB

## 📈 Performance Optimization

1. **Database Indexing**: Indexes are automatically created on `created_at` and `request_id`
2. **Connection Pooling**: PyMongo handles connection pooling automatically
3. **Caching**: Consider implementing Redis caching for high-traffic scenarios
4. **Pagination**: API returns latest 50 events to prevent large responses

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is part of a developer assessment and is for educational purposes.

---

**Next Steps:**
1. Create the `action-repo` repository
2. Set up webhooks pointing to this application
3. Test with real GitHub activities
4. Monitor the live dashboard!