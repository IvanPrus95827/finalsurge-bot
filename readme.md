# Final Surge Bot

A Python application that automatically monitors athletes' training plans and results on Final Surge, sending personalized messages every Saturday at 6 PM (Ireland time) based on their weekly performance.

## Features

- **Automated Monitoring**: Scrapes athlete training data from Final Surge weekly
- **Smart Messaging**: Sends personalized messages based on training completion status
- **Scheduled Execution**: Runs automatically every Saturday at 6 PM (Ireland timezone)
- **Team Support**: Handles multiple teams and athletes
- **Personalized Communication**: Uses athlete's first name in messages

## How It Works

The bot connects to the Final Surge API to:
1. Retrieve team and athlete information
2. Fetch weekly training plans and completion status
3. Analyze workout completion for the current week
4. Send appropriate messages:
   - **Completion messages**: For athletes who completed their training
   - **Check-in messages**: For athletes with incomplete workouts

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
   ```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

| Variable | Description | Required |
|----------|-------------|----------|
| `USER_EMAIL` | Your Final Surge login email | Yes |
| `USER_PASSWORD` | Your Final Surge login password | Yes |


**Note**: Use `$NAME` as a placeholder for the athlete's first name.

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

## Security Notes

- Keep your `.env` file secure and never commit it to version control
- Use strong passwords for your Final Surge account
- The bot stores credentials only in memory during execution

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your Final Surge account permissions
3. Ensure all dependencies are properly installed
