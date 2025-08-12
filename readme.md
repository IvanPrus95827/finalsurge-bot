# Final Surge Bot

A Python application that automatically monitors athletes' training plans and results on Final Surge, sending personalized messages every Saturday at 6 PM (Ireland time) based on their weekly performance. The bot also includes an inbox listener feature to automatically respond to athlete messages.

## Features

- **Automated Monitoring**: Scrapes athlete training data from Final Surge weekly
- **Smart Messaging**: Sends personalized messages based on training completion status
- **Scheduled Execution**: Runs automatically every Saturday at 6 PM (Ireland timezone)
- **Team Support**: Handles multiple teams and athletes
- **Personalized Communication**: Uses athlete's first name in messages
- **Inbox Listener**: Automatically monitors and responds to incoming messages from athletes
- **AI-Powered Auto-Reply**: Uses an AI engine to analyze messages and generate contextual, personalized responses
- **Real-time Message Processing**: Continuously polls inbox with configurable intervals and handles network issues gracefully
- **Smart Message Filtering**: Determines when responses are needed based on message content and context

## How It Works

The bot connects to the Final Surge API to:
1. Retrieve team and athlete information
2. Fetch weekly training plans and completion status
3. Analyze workout completion for the current week
4. Send appropriate messages:
   - **Completion messages**: For athletes who completed their training
   - **Check-in messages**: For athletes with incomplete workouts
5. Monitor inbox for new messages and respond automatically using AI
6. Process incoming messages in real-time with intelligent filtering
7. Generate contextual responses based on message content and athlete context

## Prerequisites

- Python 3.7 or higher
- Final Surge account with coach/team access
- Internet connection for API access

## Installation

1. **Clone or download the project files**
   ```bash
   git clone <repository-url>
   cd finalsurge-bot
   ```

2. **Install required Python packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**
   Create a `.env` file in the project root with your Final Surge credentials:
   ```
   USER_EMAIL=your_email@example.com
   USER_PASSWORD=your_password
   GEMINI_API_KEY=your_gemini_api_key
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USER_EMAIL` | Your Final Surge login email | - | Yes |
| `USER_PASSWORD` | Your Final Surge login password | - | Yes |
| `INBOX_LISTENER_ENABLED` | Enable/disable inbox monitoring | `true` | No |
| `INBOX_POLL_INTERVAL_SECONDS` | How often to check for new messages (seconds) | `120` | No |
| `TOKEN_TTL_SECONDS` | How long to cache authentication token (seconds) | `3300` | No |

### Message Templates

The bot uses predefined message templates that can be customized in the code:

**Complete Workout Messages:**
- "Well done on the training"
- "Nice work on Final Surge this week! 💪👏"
- "Fantastic job this week in Final Surge!"

**Incomplete Workout Messages:**
- "Check in" - For athletes with incomplete workouts

**Note**: Use `$NAME` as a placeholder for the athlete's first name in message templates.

## Usage

### Running the Bot

1. **Start the bot**:
   ```bash
   python bot.py
   ```

2. **The bot will**:
   - Display "Scheduler started. Waiting for Saturday 6 PM (Ireland time)..."
   - Automatically execute at Saturday 6 PM (Ireland timezone)
   - Process all teams and athletes
   - Send appropriate messages based on training completion
   - Monitor inbox for new messages (if enabled)
   - Respond to athlete messages using AI

### Inbox Listener & Auto-Reply

The inbox listener and auto-reply feature provides intelligent message monitoring and response:

**Message Monitoring:**
- Continuously polls the Final Surge inbox for new messages
- Configurable polling interval (default: 120 seconds)
- Tracks message timestamps to prevent duplicate processing
- Handles network timeouts and API errors gracefully

**AI-Powered Auto-Reply:**
- Analyzes incoming message content using the AI engine
- Determines if a response is needed based on message context
- Generates contextual and personalized replies
- Automatically sends responses to athletes

**Message Processing:**
- Extracts sender information, subject, and message content
- Processes messages in chronological order
- Logs all inbox activity for monitoring
- Handles various message formats and content types

**Configuration Options:**
- Enable/disable inbox monitoring via `INBOX_LISTENER_ENABLED`
- Adjust polling frequency with `INBOX_POLL_INTERVAL_SECONDS`
- Control authentication token caching with `TOKEN_TTL_SECONDS`

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify your Final Surge credentials in the `.env` file
   - Ensure your account has coach/team access permissions

2. **Network Timeouts**
   - The bot includes timeout handling for API requests
   - Check your internet connection
   - Verify Final Surge API availability

3. **Inbox Poll Delays**
   - If inbox polling takes too long, increase `INBOX_POLL_INTERVAL_SECONDS`
   - The default 120-second interval should be sufficient for most cases
   - Check network connectivity and Final Surge API status

4. **Message Processing Errors**
   - Check the console output for specific error messages
   - Verify the AI engine (`engine.py`) is properly configured
   - Ensure message format compatibility with the processing logic

5. **Auto-Reply Issues**
   - Verify AI engine is responding correctly to test messages
   - Check if messages are being filtered out unexpectedly
   - Review message content for potential processing issues

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use strong passwords for your Final Surge account
- The bot stores credentials only in memory during execution
- API tokens are cached for 55 minutes to reduce authentication overhead

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Final Surge account permissions
3. Ensure all dependencies are properly installed
4. Review console output for error messages

## File Structure

```
finalsurge-bot/
├── bot.py              # Main bot application with scheduling and inbox monitoring
├── engine.py           # AI engine for intelligent message analysis and response generation
├── requirements.txt    # Python dependencies
├── readme.md          # This file
└── .env               # Environment configuration (create this)
```
