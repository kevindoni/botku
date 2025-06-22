# Troubleshooting Guide - YouTube Streaming Bot

## Common Issues and Solutions

### 1. Installation Issues

#### FFmpeg not found
```bash
# Install FFmpeg
sudo apt update
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

#### Python dependencies fail to install
```bash
# Update pip and setuptools
pip install --upgrade pip setuptools

# Install with verbose output to see errors
pip install -v -r requirements.txt

# For OpenCV issues on Ubuntu
sudo apt install python3-opencv
```

#### ChromeDriver issues
```bash
# Install ChromeDriver manually
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
LATEST=$(cat LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

### 2. Streaming Issues

#### Stream fails to start
**Symptoms:** Error message when starting stream
**Solutions:**
1. Check YouTube stream key in config.yaml
2. Verify internet connection
3. Check FFmpeg installation
4. Review logs for detailed error messages

```bash
# Test FFmpeg manually
ffmpeg -f lavfi -i testsrc=size=1280x720:rate=30 -f lavfi -i sine=frequency=1000 -t 10 test.mp4
```

#### Poor stream quality
**Symptoms:** Low quality or choppy stream
**Solutions:**
1. Reduce bitrate in config.yaml
2. Lower resolution (e.g., 1280x720)
3. Check CPU usage during streaming
4. Ensure sufficient bandwidth

```yaml
streaming:
  bitrate: 1500  # Reduce from 2500
  resolution: "1280x720"  # Reduce from 1920x1080
  fps: 25  # Reduce from 30
```

#### Stream disconnects frequently
**Solutions:**
1. Check network stability
2. Increase buffer size in FFmpeg
3. Use lower bitrate
4. Check YouTube streaming guidelines

### 3. Bot Issues

#### Comment bot not working
**Symptoms:** No comments being posted
**Solutions:**
1. Check account credentials in config/accounts.json
2. Verify YouTube login process
3. Check if accounts are blocked/suspended
4. Review Selenium WebDriver setup

```bash
# Test Chrome/Chromium installation
chromium-browser --version
google-chrome --version
```

#### Viewer bot sessions failing
**Solutions:**
1. Check virtual display setup (Xvfb)
2. Verify Chrome headless mode
3. Check memory usage
4. Review proxy settings if used

### 4. Dashboard Issues

#### Dashboard not accessible
**Symptoms:** Cannot access http://localhost:5000
**Solutions:**
1. Check if port 5000 is available
2. Verify Flask application is running
3. Check firewall settings
4. Review application logs

```bash
# Check if port is in use
sudo netstat -tlnp | grep :5000

# Check firewall
sudo ufw status
sudo ufw allow 5000/tcp
```

#### Dashboard shows errors
**Solutions:**
1. Check browser console for JavaScript errors
2. Verify all static files are loaded
3. Check Flask logs
4. Clear browser cache

### 5. Configuration Issues

#### Config file not found
```bash
# Copy example config
cp config/config.example.yaml config/config.yaml

# Edit configuration
nano config/config.yaml
```

#### Invalid YAML syntax
**Symptoms:** YAML parsing errors
**Solutions:**
1. Check indentation (use spaces, not tabs)
2. Validate YAML syntax online
3. Check for special characters
4. Review example configuration

### 6. Permission Issues

#### File permission errors
```bash
# Fix permissions
chmod -R 755 /path/to/youtube-streaming-bot
chmod +x start.sh

# For logs directory
chmod -R 766 logs/
```

#### ChromeDriver permission denied
```bash
sudo chmod +x /usr/local/bin/chromedriver
```

### 7. System Resource Issues

#### High CPU usage
**Solutions:**
1. Reduce number of viewer bot sessions
2. Lower stream quality settings
3. Close unnecessary applications
4. Monitor with htop/top

```bash
# Monitor system resources
htop
# or
top
```

#### Memory issues
**Solutions:**
1. Increase system swap space
2. Reduce bot session count
3. Monitor memory usage
4. Restart application periodically

```bash
# Check memory usage
free -h

# Add swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 8. Network Issues

#### Connection timeouts
**Solutions:**
1. Check internet connection stability
2. Increase timeout values in config
3. Use proxy if available
4. Check DNS settings

#### Rate limiting
**Symptoms:** YouTube API errors, blocked requests
**Solutions:**
1. Increase delays between bot actions
2. Use fewer bot accounts
3. Implement better rate limiting
4. Check YouTube API quotas

### 9. Logging and Debugging

#### Enable debug logging
```yaml
logging:
  level: "DEBUG"
  file: "logs/debug.log"
```

#### Check application logs
```bash
# View real-time logs
tail -f logs/app.log

# Search for errors
grep -i error logs/app.log

# View system logs
sudo journalctl -u youtube-streaming-bot -f
```

### 10. YouTube API Issues

#### Authentication failed
**Solutions:**
1. Check client_secret.json file
2. Re-generate OAuth credentials
3. Verify API key
4. Check YouTube Data API v3 is enabled

#### Quota exceeded
**Solutions:**
1. Monitor API usage in Google Cloud Console
2. Reduce API calls frequency
3. Request quota increase
4. Optimize API usage

### Emergency Recovery

#### Reset everything
```bash
# Stop application
sudo systemctl stop youtube-streaming-bot

# Remove virtual environment
rm -rf venv/

# Reinstall
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Reset configuration
cp config/config.example.yaml config/config.yaml
```

#### Factory reset
```bash
# Backup important files first
cp config/config.yaml /tmp/
cp config/accounts.json /tmp/

# Clean installation
./install.sh

# Restore configuration
cp /tmp/config.yaml config/
cp /tmp/accounts.json config/
```

## Getting Help

1. Check the logs first: `logs/app.log`
2. Enable debug mode for more detailed logs
3. Test individual components separately
4. Review YouTube's streaming guidelines
5. Check system resources (CPU, RAM, bandwidth)

## Performance Optimization

### For low-end servers:
- Reduce stream quality
- Limit bot sessions
- Use efficient encoding settings
- Monitor resource usage

### For high-end servers:
- Increase stream quality
- Run multiple bot sessions
- Use GPU encoding if available
- Enable advanced features
