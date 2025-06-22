import logging
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict
import os

logger = logging.getLogger(__name__)

class StreamAnalytics:
    def __init__(self):
        self.analytics_file = 'logs/analytics.json'
        self.session_data = {
            'streams': [],
            'bot_performance': {
                'comments': [],
                'viewers': []
            },
            'system_metrics': [],
            'errors': []
        }
        self.current_session = None
        
    def start_session(self, stream_config):
        """Start a new analytics session"""
        self.current_session = {
            'session_id': f"session_{int(time.time())}",
            'start_time': datetime.now().isoformat(),
            'end_time': None,
            'stream_config': stream_config,
            'duration': 0,
            'metrics': {
                'peak_viewers': 0,
                'total_comments': 0,
                'avg_bitrate': 0,
                'dropped_frames': 0,
                'cpu_usage_avg': 0,
                'memory_usage_avg': 0
            },
            'events': []
        }
        
        logger.info(f"Started analytics session: {self.current_session['session_id']}")
        
    def end_session(self):
        """End current analytics session"""
        if not self.current_session:
            return
            
        self.current_session['end_time'] = datetime.now().isoformat()
        
        # Calculate duration
        start_time = datetime.fromisoformat(self.current_session['start_time'])
        end_time = datetime.fromisoformat(self.current_session['end_time'])
        self.current_session['duration'] = int((end_time - start_time).total_seconds())
        
        # Save session data
        self.session_data['streams'].append(self.current_session)
        self.save_analytics_data()
        
        logger.info(f"Ended analytics session: {self.current_session['session_id']}")
        self.current_session = None
        
    def record_event(self, event_type, data):
        """Record an event during streaming"""
        if not self.current_session:
            return
            
        event = {
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'data': data
        }
        
        self.current_session['events'].append(event)
        
    def update_stream_metrics(self, metrics):
        """Update stream metrics"""
        if not self.current_session:
            return
            
        session_metrics = self.current_session['metrics']
        
        # Update peak viewers
        current_viewers = metrics.get('active_viewers', 0)
        if current_viewers > session_metrics['peak_viewers']:
            session_metrics['peak_viewers'] = current_viewers
            
        # Update average values
        if 'bitrate' in metrics:
            session_metrics['avg_bitrate'] = self._update_average(
                session_metrics['avg_bitrate'], metrics['bitrate']
            )
            
        if 'cpu_usage' in metrics:
            session_metrics['cpu_usage_avg'] = self._update_average(
                session_metrics['cpu_usage_avg'], metrics['cpu_usage']
            )
            
        if 'memory_usage' in metrics:
            session_metrics['memory_usage_avg'] = self._update_average(
                session_metrics['memory_usage_avg'], metrics['memory_usage']
            )
            
        # Update counters
        if 'comments_posted' in metrics:
            session_metrics['total_comments'] = metrics['comments_posted']
            
        if 'dropped_frames' in metrics:
            session_metrics['dropped_frames'] = metrics['dropped_frames']
            
    def _update_average(self, current_avg, new_value, weight=0.1):
        """Update running average"""
        if current_avg == 0:
            return new_value
        return current_avg * (1 - weight) + new_value * weight
        
    def record_bot_performance(self, bot_type, metrics):
        """Record bot performance metrics"""
        performance_data = {
            'timestamp': datetime.now().isoformat(),
            'bot_type': bot_type,
            'metrics': metrics
        }
        
        self.session_data['bot_performance'][bot_type].append(performance_data)
        
    def record_system_metrics(self, metrics):
        """Record system performance metrics"""
        system_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': metrics
        }
        
        self.session_data['system_metrics'].append(system_data)
        
    def record_error(self, error_type, error_message, context=None):
        """Record error for analysis"""
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': error_message,
            'context': context or {}
        }
        
        self.session_data['errors'].append(error_data)
        
    def get_session_summary(self):
        """Get current session summary"""
        if not self.current_session:
            return None
            
        return {
            'session_id': self.current_session['session_id'],
            'duration': self._get_current_duration(),
            'metrics': self.current_session['metrics'],
            'events_count': len(self.current_session['events'])
        }
        
    def _get_current_duration(self):
        """Get current session duration in seconds"""
        if not self.current_session:
            return 0
            
        start_time = datetime.fromisoformat(self.current_session['start_time'])
        return int((datetime.now() - start_time).total_seconds())
        
    def get_historical_data(self, days=7):
        """Get historical analytics data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_streams = []
        for stream in self.session_data['streams']:
            stream_date = datetime.fromisoformat(stream['start_time'])
            if stream_date >= cutoff_date:
                recent_streams.append(stream)
                
        return {
            'streams': recent_streams,
            'total_streams': len(recent_streams),
            'total_duration': sum(s['duration'] for s in recent_streams),
            'avg_duration': self._calculate_average_duration(recent_streams),
            'peak_viewers': max((s['metrics']['peak_viewers'] for s in recent_streams), default=0),
            'total_comments': sum(s['metrics']['total_comments'] for s in recent_streams)
        }
        
    def _calculate_average_duration(self, streams):
        """Calculate average stream duration"""
        if not streams:
            return 0
        return sum(s['duration'] for s in streams) / len(streams)
        
    def get_performance_insights(self):
        """Get performance insights and recommendations"""
        insights = []
        
        if not self.session_data['streams']:
            return insights
            
        recent_streams = self.get_historical_data(7)['streams']
        
        # Analyze stream stability
        if recent_streams:
            avg_dropped_frames = sum(s['metrics']['dropped_frames'] for s in recent_streams) / len(recent_streams)
            if avg_dropped_frames > 100:
                insights.append({
                    'type': 'warning',
                    'message': 'High number of dropped frames detected',
                    'recommendation': 'Consider reducing bitrate or resolution'
                })
                
        # Analyze CPU usage
        cpu_metrics = [m for m in self.session_data['system_metrics'] if 'cpu_usage' in m['metrics']]
        if cpu_metrics:
            avg_cpu = sum(m['metrics']['cpu_usage'] for m in cpu_metrics) / len(cpu_metrics)
            if avg_cpu > 80:
                insights.append({
                    'type': 'warning',
                    'message': 'High CPU usage detected',
                    'recommendation': 'Consider reducing stream quality or bot activity'
                })
                
        # Analyze error frequency
        recent_errors = [e for e in self.session_data['errors'] 
                        if datetime.fromisoformat(e['timestamp']) >= datetime.now() - timedelta(hours=24)]
        if len(recent_errors) > 10:
            insights.append({
                'type': 'error',
                'message': 'High error frequency in last 24 hours',
                'recommendation': 'Check logs and system configuration'
            })
            
        return insights
        
    def generate_report(self, days=7):
        """Generate comprehensive analytics report"""
        historical_data = self.get_historical_data(days)
        insights = self.get_performance_insights()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': days,
            'summary': historical_data,
            'insights': insights,
            'current_session': self.get_session_summary()
        }
        
        return report
        
    def save_analytics_data(self):
        """Save analytics data to file"""
        try:
            os.makedirs(os.path.dirname(self.analytics_file), exist_ok=True)
            
            with open(self.analytics_file, 'w') as f:
                json.dump(self.session_data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving analytics data: {e}")
            
    def load_analytics_data(self):
        """Load analytics data from file"""
        try:
            if os.path.exists(self.analytics_file):
                with open(self.analytics_file, 'r') as f:
                    self.session_data = json.load(f)
                    
        except Exception as e:
            logger.error(f"Error loading analytics data: {e}")
            
    def export_csv(self, filename=None):
        """Export analytics data to CSV"""
        if not filename:
            filename = f"analytics_export_{int(time.time())}.csv"
            
        try:
            import csv
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                writer.writerow([
                    'Session ID', 'Start Time', 'Duration', 'Peak Viewers',
                    'Total Comments', 'Avg Bitrate', 'Dropped Frames', 'CPU Usage', 'Memory Usage'
                ])
                
                # Write data
                for stream in self.session_data['streams']:
                    metrics = stream['metrics']
                    writer.writerow([
                        stream['session_id'],
                        stream['start_time'],
                        stream['duration'],
                        metrics['peak_viewers'],
                        metrics['total_comments'],
                        metrics['avg_bitrate'],
                        metrics['dropped_frames'],
                        metrics['cpu_usage_avg'],
                        metrics['memory_usage_avg']
                    ])
                    
            logger.info(f"Analytics data exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            return None
