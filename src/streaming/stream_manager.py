import logging
import subprocess
import threading
import time
import os
import psutil
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class StreamManager:
    def __init__(self, config):
        self.config = config
        self.ffmpeg_process = None
        self.is_streaming = False
        self.stream_start_time = None
        self.connection_status = False
        self.stream_stats = {
            'bytes_sent': 0,
            'frames_encoded': 0,
            'dropped_frames': 0,
            'fps': 0,
            'bitrate': 0
        }
        
    def check_ffmpeg_available(self):
        """Check if FFmpeg is available"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.connection_status = True
                logger.info("FFmpeg is available")
                return True
            else:
                logger.error("FFmpeg not working properly")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.error(f"FFmpeg not found: {e}")
            self.connection_status = False
            return False
            
    def get_video_sources(self):
        """Get available video sources (webcam, screen, etc.)"""
        sources = []
        
        # Check for webcam devices
        for i in range(10):  # Check first 10 video devices
            if os.path.exists(f'/dev/video{i}'):
                sources.append({
                    'type': 'webcam',
                    'device': f'/dev/video{i}',
                    'name': f'Webcam {i}'
                })
        
        # Screen capture
        sources.append({
            'type': 'screen',
            'device': ':0.0',
            'name': 'Desktop Screen'
        })
        
        # Test pattern (for testing)
        sources.append({
            'type': 'test',
            'device': 'testsrc',
            'name': 'Test Pattern'
        })
        
        return sources
        
    def build_ffmpeg_command(self, input_source='testsrc'):
        """Build FFmpeg command for streaming"""
        rtmp_url = f"rtmp://a.rtmp.youtube.com/live2/{self.config['stream_key']}"
        
        # Get resolution and fps from config
        width, height = self.config['resolution'].split('x')
        fps = self.config['fps']
        bitrate = self.config['bitrate']
        
        # Base command
        cmd = ['ffmpeg', '-y']  # -y to overwrite output
        
        # Input configuration based on source type
        if input_source == 'testsrc':
            # Test pattern
            cmd.extend([
                '-f', 'lavfi',
                '-i', f'testsrc=size={width}x{height}:rate={fps}',
                '-f', 'lavfi',
                '-i', 'sine=frequency=1000:sample_rate=44100'
            ])
        elif input_source.startswith('/dev/video'):
            # Webcam input
            cmd.extend([
                '-f', 'v4l2',
                '-i', input_source,
                '-f', 'alsa',
                '-i', 'default'  # Default audio input
            ])
        elif input_source == 'screen':
            # Screen capture
            cmd.extend([
                '-f', 'x11grab',
                '-s', f'{width}x{height}',
                '-r', str(fps),
                '-i', ':0.0',
                '-f', 'pulse',
                '-i', 'default'
            ])
        
        # Video encoding settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-tune', 'zerolatency',
            '-b:v', f'{bitrate}k',
            '-maxrate', f'{int(bitrate * 1.2)}k',
            '-bufsize', f'{bitrate * 2}k',
            '-g', str(fps * 2),  # GOP size
            '-keyint_min', str(fps),
            '-sc_threshold', '0',
            '-pix_fmt', 'yuv420p'
        ])
        
        # Audio encoding settings
        cmd.extend([
            '-c:a', 'aac',
            '-b:a', '128k',
            '-ar', '44100',
            '-ac', '2'
        ])
        
        # Output settings
        cmd.extend([
            '-f', 'flv',
            '-flvflags', 'no_duration_filesize',
            rtmp_url
        ])
        
        return cmd
        
    def start_stream(self, input_source='testsrc'):
        """Start streaming with FFmpeg"""
        try:
            if not self.check_ffmpeg_available():
                return {'success': False, 'error': 'FFmpeg not available'}
                
            if self.is_streaming:
                return {'success': False, 'error': 'Stream is already running'}
                
            # Build FFmpeg command
            cmd = self.build_ffmpeg_command(input_source)
            
            logger.info(f"Starting stream with command: {' '.join(cmd)}")
            
            # Start FFmpeg process
            self.ffmpeg_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Start monitoring thread
            monitor_thread = threading.Thread(
                target=self._monitor_stream,
                daemon=True
            )
            monitor_thread.start()
            
            self.is_streaming = True
            self.stream_start_time = datetime.now()
            
            logger.info("Stream started successfully")
            return {'success': True, 'message': 'Stream started with FFmpeg'}
            
        except Exception as e:
            logger.error(f"Error starting stream: {e}")
            return {'success': False, 'error': str(e)}
            
    def stop_stream(self):
        """Stop streaming"""
        try:
            if not self.is_streaming or not self.ffmpeg_process:
                return {'success': False, 'error': 'Stream is not running'}
                
            # Terminate FFmpeg process gracefully
            self.ffmpeg_process.terminate()
            
            # Wait for process to end, force kill if needed
            try:
                self.ffmpeg_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.warning("FFmpeg didn't terminate gracefully, force killing")
                self.ffmpeg_process.kill()
                self.ffmpeg_process.wait()
                
            self.ffmpeg_process = None
            self.is_streaming = False
            
            logger.info("Stream stopped successfully")
            return {'success': True, 'message': 'Stream stopped'}
            
        except Exception as e:
            logger.error(f"Error stopping stream: {e}")
            return {'success': False, 'error': str(e)}
            
    def _monitor_stream(self):
        """Monitor FFmpeg stream output"""
        if not self.ffmpeg_process:
            return
            
        try:
            while self.ffmpeg_process.poll() is None and self.is_streaming:
                # Read stderr for FFmpeg output
                line = self.ffmpeg_process.stderr.readline()
                if line:
                    self._parse_ffmpeg_output(line.strip())
                    
        except Exception as e:
            logger.error(f"Error monitoring stream: {e}")
            
    def _parse_ffmpeg_output(self, line):
        """Parse FFmpeg output for statistics"""
        try:
            # FFmpeg outputs stats like: frame= 1234 fps= 30 q=28.0 size= 1234kB time=00:01:23.45 bitrate=1234.5kbits/s
            if 'frame=' in line and 'fps=' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part.startswith('frame='):
                        self.stream_stats['frames_encoded'] = int(part.split('=')[1])
                    elif part.startswith('fps='):
                        self.stream_stats['fps'] = float(part.split('=')[1])
                    elif part.startswith('bitrate='):
                        bitrate_str = part.split('=')[1].replace('kbits/s', '')
                        if bitrate_str != 'N/A':
                            self.stream_stats['bitrate'] = float(bitrate_str)
                            
        except (ValueError, IndexError) as e:
            logger.debug(f"Error parsing FFmpeg output: {e}")
            
    def get_status(self):
        """Get current stream status"""
        try:
            status = {
                'connected_to_ffmpeg': self.connection_status,
                'is_streaming': self.is_streaming,
                'stream_duration': self.get_stream_duration(),
                'frames_encoded': self.stream_stats['frames_encoded'],
                'fps': self.stream_stats['fps'],
                'bitrate': self.stream_stats['bitrate'],
                'input_source': 'FFmpeg Direct'
            }
            
            # Add process info if streaming
            if self.is_streaming and self.ffmpeg_process:
                try:
                    process = psutil.Process(self.ffmpeg_process.pid)
                    status['cpu_usage'] = process.cpu_percent()
                    status['memory_usage'] = process.memory_info().rss / 1024 / 1024  # MB
                except:
                    status['cpu_usage'] = 0
                    status['memory_usage'] = 0
            else:
                status['cpu_usage'] = 0
                status['memory_usage'] = 0
                
            return status
            
        except Exception as e:
            logger.error(f"Error getting stream status: {e}")
            return {'error': str(e)}
            
    def get_stream_duration(self):
        """Get stream duration in seconds"""
        if self.stream_start_time and self.is_streaming:
            duration = datetime.now() - self.stream_start_time
            return int(duration.total_seconds())
        return 0
        
    def restart_stream(self, input_source='testsrc'):
        """Restart streaming"""
        logger.info("Restarting stream...")
        stop_result = self.stop_stream()
        if stop_result['success']:
            time.sleep(3)  # Wait before restarting
            return self.start_stream(input_source)
        return stop_result
        
    def get_available_sources(self):
        """Get list of available input sources"""
        return self.get_video_sources()
        
    def update_stream_settings(self, new_config):
        """Update stream configuration"""
        self.config.update(new_config)
        logger.info("Stream settings updated")
        
    def get_stream_health(self):
        """Get stream health metrics"""
        if not self.is_streaming:
            return {'status': 'offline', 'health': 'N/A'}
            
        health_score = 100
        issues = []
        
        # Check FPS
        if self.stream_stats['fps'] < self.config['fps'] * 0.8:
            health_score -= 20
            issues.append('Low FPS')
            
        # Check if process is still running
        if self.ffmpeg_process and self.ffmpeg_process.poll() is not None:
            health_score = 0
            issues.append('Stream process died')
            
        return {
            'status': 'streaming',
            'health_score': health_score,
            'issues': issues,
            'stats': self.stream_stats
        }
        
    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.is_streaming:
            self.stop_stream()
