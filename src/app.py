#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Live Streaming Bot - Main Application
This application provides automated streaming to YouTube without OBS Studio,
using FFmpeg directly along with comment bots and viewer bots.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import yaml
import logging
import os
import threading
import time
from datetime import datetime
import json

# Configure logging first
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class YouTubeStreamingApp:
    def __init__(self):
        """Initialize the YouTube Streaming Bot application"""
        # Initialize Flask app
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('SECRET_KEY', 'youtube-streaming-bot-secret-key')
        
        # Initialize SocketIO for real-time updates
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Load configuration
        self.config = self.load_config()
          # Initialize components (with error handling)
        self.initialize_components()
        
        # Setup routes and WebSocket handlers
        self.setup_routes()
        self.setup_websocket_handlers()
        
        # Start background tasks for real-time updates
        self.start_background_tasks()
        
        logger.info("YouTube Streaming Bot initialized successfully")
    
    def load_config(self):
        """Load configuration from YAML file"""
        try:
            if os.path.exists('config/config.yaml'):
                with open('config/config.yaml', 'r') as file:
                    config = yaml.safe_load(file)
                    logger.info("Configuration loaded successfully")
                    return config
            else:
                # Create default configuration
                default_config = self.create_default_config()
                with open('config/config.yaml', 'w') as file:
                    yaml.dump(default_config, file, default_flow_style=False)
                logger.info("Created default configuration file")
                return default_config
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        return {
            'dashboard': {
                'host': '0.0.0.0',
                'port': 5000,
                'debug': False,
                'secret_key': 'youtube-streaming-bot-secret-key'
            },
            'streaming': {
                'rtmp_url': 'rtmp://a.rtmp.youtube.com/live2',
                'stream_key': '',
                'resolution': '1280x720',
                'fps': 30,
                'bitrate': 2500,
                'input_source': 'testsrc',
                'auto_restart': False
            },
            'bot': {
                'comments': {
                    'enabled': False,
                    'interval': 30,
                    'max_comments': 50,
                    'random_delay': 10
                },
                'viewers': {
                    'enabled': False,
                    'max_instances': 10,
                    'session_duration': 15,
                    'use_proxies': False
                }
            },            'youtube': {
                'api_key': '',
                'client_id': '',
                'client_secret': '',
                'timeout': 30
            },
            'scheduler': {
                'enabled': False
            }        }
    
    def initialize_components(self):
        """Initialize all components with error handling"""
        try:
            # Import real components
            from streaming.stream_manager import StreamManager
            from bot.comment_bot import CommentBot
            from bot.viewer_bot import ViewerBot
            from api.youtube_api import YouTubeAPI
            from streaming.scheduler import StreamScheduler as Scheduler
            from dashboard.analytics import StreamAnalytics as Analytics
            from dashboard.monitoring import SystemMonitor as Monitoring
            
            # Initialize components with proper config
            streaming_config = self.config.get('streaming', {})
            bot_config = self.config.get('bot', {})
            youtube_config = self.config.get('youtube', {})
            
            self.stream_manager = StreamManager(streaming_config)
            self.comment_bot = CommentBot({
                **bot_config.get('comments', {}),
                'accounts_file': 'config/accounts.json',
                'comments_file': 'config/comments.json'
            })
            self.viewer_bot = ViewerBot(bot_config.get('viewers', {}))
            self.youtube_api = YouTubeAPI({
                **youtube_config,
                'client_secrets_file': 'config/client_secrets.json'
            })
            # Initialize scheduler with all required components
            self.scheduler = Scheduler(
                self.stream_manager, 
                self.comment_bot, 
                self.viewer_bot, 
                self.config.get('scheduler', {})
            )
            self.analytics = Analytics()
            self.monitoring = Monitoring()
            
            logger.info("Components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            # Initialize dummy components for development fallback
            self.stream_manager = DummyStreamManager(self.config)
            self.comment_bot = DummyCommentBot(self.config)
            self.viewer_bot = DummyViewerBot(self.config)
            self.youtube_api = DummyYouTubeAPI(self.config)
            self.scheduler = DummyScheduler(self.config)
            self.analytics = DummyAnalytics(self.config)
            self.monitoring = DummyMonitoring(self.config)
    
    def setup_websocket_handlers(self):
        """Setup WebSocket event handlers for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid}")
            emit('status', {'message': 'Connected to YouTube Streaming Bot'})
            
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client disconnected: {request.sid}")
            
        @self.socketio.on('request_status')
        def handle_status_request():
            """Send current status to client"""
            status = self.get_system_status()
            emit('system_status', status)
    
    def get_system_status(self):
        """Get comprehensive system status"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'stream': {
                    'status': self.stream_manager.is_streaming(),
                    'uptime': self.stream_manager.get_uptime() if self.stream_manager.is_streaming() else 0
                },
                'bots': {
                    'comment_bot': {
                        'active': self.comment_bot.is_running(),
                        'comments_sent': self.comment_bot.get_stats().get('comments_sent', 0)
                    },
                    'viewer_bot': {
                        'active': self.viewer_bot.is_running(),
                        'active_viewers': self.viewer_bot.get_active_viewers()
                    }
                },
                'scheduler': {
                    'running': self.scheduler.is_running()
                }
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('dashboard.html', 
                                 config=self.config,
                                 stream_status=self.stream_manager.get_status())
        
        @self.app.route('/settings')
        def settings():
            """Settings page"""
            return render_template('settings.html', config=self.config)
        
        # API Routes
        @self.app.route('/api/stream/start', methods=['POST'])
        def start_stream():
            """Start streaming"""
            try:
                result = self.stream_manager.start_stream()
                if result.get('success'):
                    # Start bots if enabled
                    if self.config.get('bot', {}).get('comments', {}).get('enabled', False):
                        self.comment_bot.start()
                    if self.config.get('bot', {}).get('viewers', {}).get('enabled', False):
                        self.viewer_bot.start()
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error starting stream: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/stream/stop', methods=['POST'])
        def stop_stream():
            """Stop streaming"""
            try:
                # Stop bots first
                if self.comment_bot.is_running():
                    self.comment_bot.stop()
                if self.viewer_bot.is_running():
                    self.viewer_bot.stop()
                
                result = self.stream_manager.stop_stream()
                return jsonify(result)
            except Exception as e:
                logger.error(f"Error stopping stream: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/stream/status')
        def stream_status():
            """Get stream status"""
            try:
                return jsonify(self.stream_manager.get_status())
            except Exception as e:
                return jsonify({'error': str(e)})
        
        @self.app.route('/api/bot/comment/toggle', methods=['POST'])
        def toggle_comment_bot():
            """Toggle comment bot"""
            try:
                if self.comment_bot.is_running():
                    self.comment_bot.stop()
                    status = 'stopped'
                else:
                    self.comment_bot.start()
                    status = 'started'
                return jsonify({'success': True, 'status': status})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/bot/viewer/toggle', methods=['POST'])
        def toggle_viewer_bot():
            """Toggle viewer bot"""
            try:
                if self.viewer_bot.is_running():
                    self.viewer_bot.stop()
                    status = 'stopped'
                else:
                    self.viewer_bot.start()
                    status = 'started'
                return jsonify({'success': True, 'status': status})
            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/settings/get')
        def get_settings():
            """Get current settings (sanitized)"""
            try:
                # Return sanitized config (hide sensitive data)
                safe_config = self.config.copy()
                if 'youtube' in safe_config:
                    if 'api_key' in safe_config['youtube'] and safe_config['youtube']['api_key']:
                        safe_config['youtube']['api_key'] = '***hidden***'
                    if 'client_secret' in safe_config['youtube'] and safe_config['youtube']['client_secret']:
                        safe_config['youtube']['client_secret'] = '***hidden***'
                if 'streaming' in safe_config:
                    if 'stream_key' in safe_config['streaming'] and safe_config['streaming']['stream_key']:
                        safe_config['streaming']['stream_key'] = '***hidden***'
                
                return jsonify({'success': True, 'settings': safe_config})
            except Exception as e:
                logger.error(f"Error getting settings: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/settings/update', methods=['POST'])
        def update_settings():
            """Update settings"""
            try:
                new_settings = request.json
                logger.info(f"Updating settings: {new_settings}")
                
                # Update configuration
                self._update_config(new_settings)
                
                # Save to file
                with open('config/config.yaml', 'w') as file:
                    yaml.dump(self.config, file, default_flow_style=False)
                
                logger.info("Settings updated successfully")
                return jsonify({'success': True, 'message': 'Settings updated successfully'})
            except Exception as e:
                logger.error(f"Error updating settings: {e}")
                return jsonify({'success': False, 'error': str(e)})
        
        @self.app.route('/api/system/status')
        def system_status():
            """Get system status"""
            try:
                return jsonify(self.get_system_status())
            except Exception as e:
                return jsonify({'error': str(e)})
    
    def _update_config(self, new_settings):
        """Update configuration with new settings"""
        try:
            category = new_settings.get('category')
            settings = new_settings.get('settings', {})
            
            if category == 'streaming':
                self._update_streaming_settings(settings)
            elif category == 'bots':
                self._update_bot_settings(settings)
            elif category == 'youtube':
                self._update_youtube_settings(settings)
            elif category == 'security':
                self._update_security_settings(settings)
            else:
                # Direct config update
                for key, value in new_settings.items():
                    if key in self.config:
                        if isinstance(self.config[key], dict) and isinstance(value, dict):
                            self.config[key].update(value)
                        else:
                            self.config[key] = value
                            
            logger.info("Configuration updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            raise
    
    def _update_streaming_settings(self, settings):
        """Update streaming settings"""
        streaming_config = self.config.setdefault('streaming', {})
        
        for key, value in settings.items():
            if key == 'stream_key' and value != '***hidden***':
                streaming_config['stream_key'] = value
            elif key in ['rtmp_server', 'resolution', 'video_input', 'video_file']:
                streaming_config[key] = value
            elif key in ['bitrate', 'framerate']:
                streaming_config[key] = int(value) if value else 0
            elif key in ['auto_restart', 'record_local']:
                streaming_config[key] = bool(value)
    
    def _update_bot_settings(self, settings):
        """Update bot settings"""
        bot_config = self.config.setdefault('bot', {})
        
        # Comment bot settings
        comment_config = bot_config.setdefault('comments', {})
        if 'comment_enabled' in settings:
            comment_config['enabled'] = bool(settings['comment_enabled'])
        if 'comment_interval' in settings:
            comment_config['interval'] = int(settings['comment_interval'])
        if 'max_comments' in settings:
            comment_config['max_comments'] = int(settings['max_comments'])
        if 'random_delay' in settings:
            comment_config['random_delay'] = int(settings['random_delay'])
        
        # Viewer bot settings
        viewer_config = bot_config.setdefault('viewers', {})
        if 'viewer_enabled' in settings:
            viewer_config['enabled'] = bool(settings['viewer_enabled'])
        if 'max_viewers' in settings:
            viewer_config['max_instances'] = int(settings['max_viewers'])
        if 'session_duration' in settings:
            viewer_config['session_duration'] = int(settings['session_duration'])
        if 'use_proxies' in settings:
            viewer_config['use_proxies'] = bool(settings['use_proxies'])
    
    def _update_youtube_settings(self, settings):
        """Update YouTube API settings"""
        youtube_config = self.config.setdefault('youtube', {})
        
        for key, value in settings.items():
            if key == 'api_key' and value != '***hidden***':
                youtube_config['api_key'] = value
            elif key == 'client_secret' and value != '***hidden***':
                youtube_config['client_secret'] = value
            elif key in ['client_id', 'timeout', 'rate_limit']:
                youtube_config[key] = value
    
    def _update_security_settings(self, settings):
        """Update security settings"""
        # These would update dashboard and security configurations
        dashboard_config = self.config.setdefault('dashboard', {})
        
        for key, value in settings.items():
            if key in ['session_timeout', 'max_failed_attempts']:
                dashboard_config[key] = int(value) if value else 0
            elif key in ['enable_logging', 'enable_cors']:
                dashboard_config[key] = bool(value)
    
    def start_background_tasks(self):
        """Start background tasks for real-time updates"""
        def broadcast_status():
            """Broadcast status updates to all connected clients"""
            while True:
                try:
                    if hasattr(self, 'socketio'):
                        status = self.get_system_status()
                        self.socketio.emit('system_status', status)
                except Exception as e:
                    logger.error(f"Error broadcasting status: {e}")
                time.sleep(5)  # Update every 5 seconds
        
        # Start background thread
        status_thread = threading.Thread(target=broadcast_status, daemon=True)
        status_thread.start()
        logger.info("Background status broadcasting started")

    def run(self):
        """Run the application"""
        port = int(os.getenv('PORT', self.config.get('dashboard', {}).get('port', 5000)))
        host = os.getenv('HOST', self.config.get('dashboard', {}).get('host', '0.0.0.0'))
        debug = os.getenv('FLASK_ENV') == 'development'
        
        logger.info(f"Starting YouTube Streaming Bot on {host}:{port}")
        
        # Use SocketIO to run the app for WebSocket support
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )

# Dummy classes for development (will be replaced with real implementations)
class DummyStreamManager:
    def __init__(self, config):
        self.config = config
        self._streaming = False
        self._start_time = None
    
    def start_stream(self):
        self._streaming = True
        self._start_time = datetime.now()
        return {'success': True, 'message': 'Stream started successfully'}
    
    def stop_stream(self):
        self._streaming = False
        self._start_time = None
        return {'success': True, 'message': 'Stream stopped successfully'}
    
    def is_streaming(self):
        return self._streaming
    
    def get_status(self):
        return {
            'streaming': self._streaming,
            'uptime': self.get_uptime()
        }
    
    def get_uptime(self):
        if self._streaming and self._start_time:
            return int((datetime.now() - self._start_time).total_seconds())
        return 0

class DummyCommentBot:
    def __init__(self, config):
        self.config = config
        self._running = False
        self._stats = {'comments_sent': 0}
    
    def start(self):
        self._running = True
    
    def stop(self):
        self._running = False
    
    def is_running(self):
        return self._running
    
    def get_stats(self):
        return self._stats

class DummyViewerBot:
    def __init__(self, config):
        self.config = config
        self._running = False
        self._active_viewers = 0
    
    def start(self):
        self._running = True
        self._active_viewers = 5
    
    def stop(self):
        self._running = False
        self._active_viewers = 0
    
    def is_running(self):
        return self._running
    
    def get_active_viewers(self):
        return self._active_viewers

class DummyYouTubeAPI:
    def __init__(self, config):
        self.config = config

class DummyScheduler:
    def __init__(self, config):
        self.config = config
        self._running = False
    
    def is_running(self):
        return self._running

class DummyAnalytics:
    def __init__(self, config):
        self.config = config
    
    def get_stats(self):
        return {'sessions': 0, 'total_uptime': 0}

class DummyMonitoring:
    def __init__(self, config):
        self.config = config
    
    def get_system_metrics(self):
        return {
            'cpu_percent': 25.5,
            'memory_percent': 45.2,
            'disk_usage': 60.8,
            'network_io': {'bytes_sent': 1024, 'bytes_recv': 2048}
        }

def main():
    """Main entry point"""
    try:
        app = YouTubeStreamingApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == '__main__':
    main()
