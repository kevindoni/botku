import random
import time
import threading
import logging
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)

class ViewerBot:
    def __init__(self, config):
        self.config = config
        self.is_running = False
        self.threads = []
        self.active_sessions = []
        self.stats = {
            'total_views': 0,
            'active_viewers': 0,
            'session_duration_avg': 0,
            'errors': 0,
            'start_time': None
        }
        
    def create_viewer_driver(self):
        """Create a Chrome driver for viewing"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--mute-audio')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--window-size=1280,720')
        
        # Random user agents for diversity
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Random viewport sizes
        viewports = ['1920,1080', '1366,768', '1280,720', '1024,768']
        options.add_argument(f'--window-size={random.choice(viewports)}')
        
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            logger.error(f"Error creating viewer driver: {e}")
            return None
            
    def simulate_viewer_session(self, stream_url, session_id):
        """Simulate a viewer watching the stream"""
        driver = None
        session_start = time.time()
        
        try:
            driver = self.create_viewer_driver()
            if not driver:
                return
                
            logger.info(f"Starting viewer session {session_id}")
            
            # Navigate to stream
            driver.get(stream_url)
            
            # Wait for video to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "video"))
            )
            
            # Find and click play if needed
            try:
                play_button = driver.find_element(By.CSS_SELECTOR, ".ytp-large-play-button")
                if play_button.is_displayed():
                    play_button.click()
            except:
                pass  # Video might already be playing
                
            # Simulate watching behavior
            session_duration = random.randint(
                self.config['session_duration'] // 2,
                self.config['session_duration'] * 2
            )
            
            watch_start = time.time()
            while time.time() - watch_start < session_duration and self.is_running:
                # Random interactions to appear more human
                if random.random() < 0.1:  # 10% chance
                    self.simulate_interaction(driver)
                    
                time.sleep(random.randint(5, 15))
                
            # Update stats
            actual_duration = time.time() - session_start
            self.stats['total_views'] += 1
            self.update_avg_duration(actual_duration)
            
            logger.info(f"Viewer session {session_id} completed after {actual_duration:.1f}s")
            
        except Exception as e:
            logger.error(f"Error in viewer session {session_id}: {e}")
            self.stats['errors'] += 1
        finally:
            if driver:
                driver.quit()
            self.remove_active_session(session_id)
            
    def simulate_interaction(self, driver):
        """Simulate human-like interactions"""
        try:
            actions = ['scroll', 'pause_resume', 'volume_change']
            action = random.choice(actions)
            
            if action == 'scroll':
                # Scroll page randomly
                driver.execute_script(f"window.scrollBy(0, {random.randint(-200, 200)});")
                
            elif action == 'pause_resume':
                # Pause and resume video
                video = driver.find_element(By.TAG_NAME, "video")
                if video:
                    driver.execute_script("arguments[0].pause();", video)
                    time.sleep(random.randint(1, 3))
                    driver.execute_script("arguments[0].play();", video)
                    
            elif action == 'volume_change':
                # Change volume
                volume = random.uniform(0.3, 0.8)
                driver.execute_script(f"document.querySelector('video').volume = {volume};")
                
        except Exception as e:
            logger.debug(f"Error in interaction simulation: {e}")
            
    def update_avg_duration(self, duration):
        """Update average session duration"""
        if self.stats['total_views'] == 1:
            self.stats['session_duration_avg'] = duration
        else:
            # Moving average
            self.stats['session_duration_avg'] = (
                (self.stats['session_duration_avg'] * (self.stats['total_views'] - 1) + duration) 
                / self.stats['total_views']
            )
            
    def add_active_session(self, session_id):
        """Add active session to tracking"""
        self.active_sessions.append(session_id)
        self.stats['active_viewers'] = len(self.active_sessions)
        
    def remove_active_session(self, session_id):
        """Remove active session from tracking"""
        if session_id in self.active_sessions:
            self.active_sessions.remove(session_id)
        self.stats['active_viewers'] = len(self.active_sessions)
        
    def maintain_viewer_count(self, stream_url):
        """Maintain target viewer count"""
        session_counter = 0
        
        while self.is_running:
            try:
                current_viewers = len(self.active_sessions)
                target_viewers = random.randint(
                    self.config['min_viewers'],
                    self.config['max_viewers']
                )
                
                if current_viewers < target_viewers:
                    # Start new viewer sessions
                    sessions_to_start = target_viewers - current_viewers
                    
                    for _ in range(sessions_to_start):
                        if not self.is_running:
                            break
                            
                        session_id = f"viewer_{session_counter}"
                        session_counter += 1
                        
                        self.add_active_session(session_id)
                        
                        # Start viewer session in separate thread
                        thread = threading.Thread(
                            target=self.simulate_viewer_session,
                            args=(stream_url, session_id),
                            daemon=True
                        )
                        thread.start()
                        self.threads.append(thread)
                        
                        # Stagger session starts
                        time.sleep(random.randint(2, 8))
                        
                # Wait before checking again
                time.sleep(random.randint(30, 60))
                
            except Exception as e:
                logger.error(f"Error maintaining viewer count: {e}")
                time.sleep(30)
                
    def get_stream_url(self):
        """Get the stream URL - you'll need to implement this based on your setup"""
        # This should return the actual live stream URL
        # For now, returning a placeholder
        return "https://youtube.com/@yourchannel/live"
        
    def start(self):
        """Start the viewer bot"""
        if self.is_running:
            return False
            
        self.is_running = True
        self.stats['start_time'] = time.time()
        
        # Get stream URL
        stream_url = self.get_stream_url()
        
        # Start main viewer management thread
        main_thread = threading.Thread(
            target=self.maintain_viewer_count,
            args=(stream_url,),
            daemon=True
        )
        main_thread.start()
        self.threads.append(main_thread)
        
        logger.info("Viewer bot started")
        return True
        
    def stop(self):
        """Stop the viewer bot"""
        self.is_running = False
        
        # Wait for threads to finish (with timeout)
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
                
        self.threads.clear()
        self.active_sessions.clear()
        self.stats['active_viewers'] = 0
        
        logger.info("Viewer bot stopped")
        
    def is_running_status(self):
        """Check if bot is running"""
        return self.is_running
        
    def get_stats(self):
        """Get bot statistics"""
        stats = self.stats.copy()
        if stats['start_time']:
            stats['runtime'] = time.time() - stats['start_time']
        return stats
        
    def adjust_viewer_count(self, min_viewers, max_viewers):
        """Dynamically adjust viewer count ranges"""
        self.config['min_viewers'] = min_viewers
        self.config['max_viewers'] = max_viewers
        logger.info(f"Adjusted viewer count: {min_viewers}-{max_viewers}")
        
    def get_real_viewer_count(self, stream_url):
        """Get actual viewer count from YouTube (if possible)"""
        try:
            # This would need YouTube API or web scraping
            # Placeholder implementation
            return random.randint(50, 200)
        except Exception as e:
            logger.error(f"Error getting real viewer count: {e}")
            return 0
