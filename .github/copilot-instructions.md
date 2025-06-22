<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# YouTube Streaming Bot - Copilot Instructions

## Project Overview
This is a Python-based YouTube live streaming bot application that enables automated streaming to YouTube without OBS Studio, using FFmpeg directly. The application includes comment bots, viewer bots, and a web dashboard for monitoring and control.

## Key Technologies
- **Backend**: Python Flask
- **Streaming**: FFmpeg (direct RTMP streaming)
- **Automation**: Selenium WebDriver with Chrome/Chromium
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **APIs**: YouTube Data API v3, Google OAuth2
- **Deployment**: Ubuntu Server 24.04 LTS

## Architecture Guidelines

### Streaming Component
- Use FFmpeg for direct RTMP streaming to YouTube
- No OBS Studio dependency
- Support multiple input sources (webcam, screen capture, test pattern)
- Real-time monitoring of stream health and statistics

### Bot Components
- Comment bot: Automated natural-looking comments with random delays
- Viewer bot: Simulated viewers with realistic session durations
- Use Selenium with headless Chrome for browser automation
- Implement proxy rotation for IP diversity

### Dashboard
- Real-time monitoring with WebSocket updates
- Stream control (start/stop/restart)
- Bot management and statistics
- Analytics and health monitoring

## Coding Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Implement proper error handling and logging
- Use configuration files for all settings
- Maintain separation of concerns

### Security Considerations
- Never hardcode API keys or credentials
- Use environment variables for sensitive data
- Implement rate limiting for API calls
- Validate all user inputs
- Use secure session management

### Performance Guidelines
- Implement connection pooling for database operations
- Use background threads for long-running tasks
- Implement proper resource cleanup
- Monitor memory usage for browser instances
- Use async/await for I/O operations where beneficial

## File Structure Conventions
```
src/
├── streaming/     # FFmpeg streaming management
├── bot/          # Comment and viewer bots
├── api/          # YouTube API integration
└── app.py        # Main Flask application

config/           # Configuration files
templates/        # HTML templates
static/          # CSS, JS, assets
logs/            # Application logs
```

## Bot Behavior Guidelines
- Implement human-like delays and interactions
- Avoid patterns that could be detected as automation
- Use diverse comment content and timing
- Respect YouTube's Terms of Service
- Include disclaimers about educational/development use

## Error Handling
- Implement comprehensive try-catch blocks
- Log all errors with appropriate detail levels
- Provide meaningful error messages to users
- Implement graceful degradation for non-critical failures
- Use circuit breaker patterns for external API calls

## Configuration Management
- Use YAML for main configuration
- Support environment variable overrides
- Provide example/template configurations
- Validate configuration on startup
- Support runtime configuration updates

## Deployment Considerations
- Design for Ubuntu Server 24.04 LTS
- Use systemd services for process management
- Implement proper logging and monitoring
- Support both development and production modes
- Include installation and setup scripts

## Testing Guidelines
- Write unit tests for core functionality
- Test streaming components with various inputs
- Validate bot behavior under different conditions
- Performance test with multiple concurrent operations
- Test error scenarios and recovery mechanisms
