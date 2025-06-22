import logging
import threading
import time
import schedule
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class StreamScheduler:
    def __init__(self, stream_manager, comment_bot, viewer_bot, config):
        self.stream_manager = stream_manager
        self.comment_bot = comment_bot
        self.viewer_bot = viewer_bot
        self.config = config
        self.scheduled_jobs = []
        self.running = False
        self.scheduler_thread = None
        
    def load_schedule_config(self):
        """Load streaming schedule from configuration"""
        schedule_file = 'config/schedule.json'
        if os.path.exists(schedule_file):
            with open(schedule_file, 'r') as f:
                return json.load(f)
        else:
            # Create default schedule
            default_schedule = {
                "timezone": "Asia/Jakarta",
                "streams": [
                    {
                        "id": "morning_stream",
                        "name": "Morning Stream",
                        "time": "08:00",
                        "duration": 120,
                        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
                        "enabled": True,
                        "input_source": "testsrc",
                        "title": "Good Morning Live Stream",
                        "description": "Daily morning stream with educational content"
                    },
                    {
                        "id": "evening_stream", 
                        "name": "Evening Stream",
                        "time": "19:00",
                        "duration": 180,
                        "days": ["tuesday", "thursday", "saturday"],
                        "enabled": True,
                        "input_source": "testsrc",
                        "title": "Evening Entertainment Stream",
                        "description": "Evening stream with entertainment content"
                    }
                ]
            }
            
            with open(schedule_file, 'w') as f:
                json.dump(default_schedule, f, indent=2)
            
            return default_schedule
            
    def setup_scheduled_streams(self):
        """Set up scheduled streaming based on configuration"""
        schedule_config = self.load_schedule_config()
        
        # Clear existing jobs
        schedule.clear()
        self.scheduled_jobs.clear()
        
        for stream_config in schedule_config.get('streams', []):
            if not stream_config.get('enabled', True):
                continue
                
            stream_time = stream_config['time']
            days = stream_config['days']
            
            for day in days:
                job = getattr(schedule.every(), day).at(stream_time).do(
                    self.execute_scheduled_stream, stream_config
                )
                self.scheduled_jobs.append({
                    'job': job,
                    'config': stream_config,
                    'day': day,
                    'time': stream_time
                })
                
        logger.info(f"Scheduled {len(self.scheduled_jobs)} streaming sessions")
        
    def execute_scheduled_stream(self, stream_config):
        """Execute a scheduled stream"""
        try:
            logger.info(f"Starting scheduled stream: {stream_config['name']}")
            
            # Start stream
            result = self.stream_manager.start_stream(
                input_source=stream_config.get('input_source', 'testsrc')
            )
            
            if not result['success']:
                logger.error(f"Failed to start scheduled stream: {result['error']}")
                return
                
            # Start bots if enabled
            if self.config['bot']['comments']['enabled']:
                self.comment_bot.start()
                
            if self.config['bot']['viewers']['enabled']:
                self.viewer_bot.start()
                
            # Schedule stream stop
            duration_minutes = stream_config['duration']
            stop_timer = threading.Timer(
                duration_minutes * 60,
                self.stop_scheduled_stream,
                args=[stream_config]
            )
            stop_timer.start()
            
            logger.info(f"Scheduled stream will run for {duration_minutes} minutes")
            
        except Exception as e:
            logger.error(f"Error executing scheduled stream: {e}")
            
    def stop_scheduled_stream(self, stream_config):
        """Stop a scheduled stream"""
        try:
            logger.info(f"Stopping scheduled stream: {stream_config['name']}")
            
            # Stop bots
            self.comment_bot.stop()
            self.viewer_bot.stop()
            
            # Stop stream
            self.stream_manager.stop_stream()
            
            logger.info("Scheduled stream stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping scheduled stream: {e}")
            
    def start_scheduler(self):
        """Start the scheduler thread"""
        if self.running:
            return False
            
        self.setup_scheduled_streams()
        self.running = True
        
        self.scheduler_thread = threading.Thread(
            target=self._run_scheduler,
            daemon=True
        )
        self.scheduler_thread.start()
        
        logger.info("Stream scheduler started")
        return True
        
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        logger.info("Stream scheduler stopped")
        
    def _run_scheduler(self):
        """Main scheduler loop"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                time.sleep(60)
                
    def get_next_streams(self, limit=5):
        """Get next scheduled streams"""
        next_streams = []
        
        for job_info in self.scheduled_jobs:
            job = job_info['job']
            config = job_info['config']
            
            try:
                # Calculate next run time
                next_run = job.next_run
                if next_run:
                    next_streams.append({
                        'name': config['name'],
                        'time': next_run.strftime('%Y-%m-%d %H:%M:%S'),
                        'duration': config['duration'],
                        'day': job_info['day']
                    })
            except:
                continue
                
        # Sort by time and return limited results
        next_streams.sort(key=lambda x: x['time'])
        return next_streams[:limit]
        
    def add_stream_schedule(self, stream_config):
        """Add a new stream to schedule"""
        schedule_config = self.load_schedule_config()
        schedule_config['streams'].append(stream_config)
        
        with open('config/schedule.json', 'w') as f:
            json.dump(schedule_config, f, indent=2)
            
        # Refresh scheduler
        if self.running:
            self.setup_scheduled_streams()
            
        logger.info(f"Added new stream schedule: {stream_config['name']}")
        
    def remove_stream_schedule(self, stream_id):
        """Remove a stream from schedule"""
        schedule_config = self.load_schedule_config()
        schedule_config['streams'] = [
            s for s in schedule_config['streams']
            if s.get('id') != stream_id
        ]
        
        with open('config/schedule.json', 'w') as f:
            json.dump(schedule_config, f, indent=2)
            
        # Refresh scheduler
        if self.running:
            self.setup_scheduled_streams()
            
        logger.info(f"Removed stream schedule: {stream_id}")
        
    def update_stream_schedule(self, stream_id, updates):
        """Update an existing stream schedule"""
        schedule_config = self.load_schedule_config()
        
        for stream in schedule_config['streams']:
            if stream.get('id') == stream_id:
                stream.update(updates)
                break
                
        with open('config/schedule.json', 'w') as f:
            json.dump(schedule_config, f, indent=2)
            
        # Refresh scheduler
        if self.running:
            self.setup_scheduled_streams()
            
        logger.info(f"Updated stream schedule: {stream_id}")
        
    def get_schedule_status(self):
        """Get current scheduler status"""
        return {
            'running': self.running,
            'total_jobs': len(self.scheduled_jobs),
            'next_streams': self.get_next_streams(),
            'current_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
