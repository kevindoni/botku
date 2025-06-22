import psutil
import logging
import time
import threading
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class SystemMonitor:
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.metrics_history = []
        self.max_history = 1000  # Keep last 1000 measurements
        
    def start_monitoring(self, interval=30):
        """Start system monitoring"""
        if self.monitoring:
            return False
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        
        logger.info(f"System monitoring started (interval: {interval}s)")
        return True
        
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.monitoring = False
        logger.info("System monitoring stopped")
        
    def _monitor_loop(self, interval):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only recent metrics
                if len(self.metrics_history) > self.max_history:
                    self.metrics_history.pop(0)
                    
                # Check for alerts
                self.check_alerts(metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(interval)
                
    def collect_metrics(self):
        """Collect system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            # Network metrics
            network = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'load_avg': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'used': memory.used,
                    'free': memory.free
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': disk.percent
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': process_count
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return None
            
    def check_alerts(self, metrics):
        """Check for system alerts"""
        if not metrics:
            return
            
        alerts = []
        
        # CPU alert
        if metrics['cpu']['percent'] > 90:
            alerts.append({
                'type': 'critical',
                'component': 'cpu',
                'message': f"High CPU usage: {metrics['cpu']['percent']:.1f}%",
                'value': metrics['cpu']['percent']
            })
        elif metrics['cpu']['percent'] > 80:
            alerts.append({
                'type': 'warning',
                'component': 'cpu',
                'message': f"CPU usage high: {metrics['cpu']['percent']:.1f}%",
                'value': metrics['cpu']['percent']
            })
            
        # Memory alert
        if metrics['memory']['percent'] > 90:
            alerts.append({
                'type': 'critical',
                'component': 'memory',
                'message': f"High memory usage: {metrics['memory']['percent']:.1f}%",
                'value': metrics['memory']['percent']
            })
        elif metrics['memory']['percent'] > 80:
            alerts.append({
                'type': 'warning',
                'component': 'memory',
                'message': f"Memory usage high: {metrics['memory']['percent']:.1f}%",
                'value': metrics['memory']['percent']
            })
            
        # Disk alert
        if metrics['disk']['percent'] > 95:
            alerts.append({
                'type': 'critical',
                'component': 'disk',
                'message': f"Disk space critical: {metrics['disk']['percent']:.1f}%",
                'value': metrics['disk']['percent']
            })
        elif metrics['disk']['percent'] > 85:
            alerts.append({
                'type': 'warning',
                'component': 'disk',
                'message': f"Disk space low: {metrics['disk']['percent']:.1f}%",
                'value': metrics['disk']['percent']
            })
            
        # Log alerts
        for alert in alerts:
            if alert['type'] == 'critical':
                logger.critical(alert['message'])
            else:
                logger.warning(alert['message'])
                
        return alerts
        
    def get_current_metrics(self):
        """Get current system metrics"""
        return self.collect_metrics()
        
    def get_metrics_history(self, minutes=60):
        """Get metrics history for specified minutes"""
        if not self.metrics_history:
            return []
            
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        recent_metrics = []
        
        for metric in self.metrics_history:
            metric_time = datetime.fromisoformat(metric['timestamp']).timestamp()
            if metric_time >= cutoff_time:
                recent_metrics.append(metric)
                
        return recent_metrics
        
    def get_system_summary(self):
        """Get system summary"""
        current = self.collect_metrics()
        if not current:
            return None
            
        return {
            'hostname': psutil.os.uname().nodename if hasattr(psutil.os, 'uname') else 'unknown',
            'uptime': time.time() - psutil.boot_time(),
            'cpu_percent': current['cpu']['percent'],
            'memory_percent': current['memory']['percent'],
            'disk_percent': current['disk']['percent'],
            'process_count': current['processes'],
            'status': self.get_system_status(current)
        }
        
    def get_system_status(self, metrics):
        """Determine overall system status"""
        if not metrics:
            return 'unknown'
            
        cpu_ok = metrics['cpu']['percent'] < 80
        memory_ok = metrics['memory']['percent'] < 80
        disk_ok = metrics['disk']['percent'] < 85
        
        if cpu_ok and memory_ok and disk_ok:
            return 'healthy'
        elif metrics['cpu']['percent'] > 90 or metrics['memory']['percent'] > 90 or metrics['disk']['percent'] > 95:
            return 'critical'
        else:
            return 'warning'
            
    def export_metrics(self, filename=None):
        """Export metrics to JSON file"""
        if not filename:
            filename = f"system_metrics_{int(time.time())}.json"
            
        try:
            with open(filename, 'w') as f:
                json.dump(self.metrics_history, f, indent=2)
                
            logger.info(f"Metrics exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return None
