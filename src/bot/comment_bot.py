import random
import time
import json
import logging
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class CommentBot:
    def __init__(self, config):
        self.config = config
        self._is_running = False
        self.thread = None
        self.accounts = []
        self.comments = []
        self.drivers = []
        self.stats = {
            'comments_posted': 0,
            'accounts_used': 0,
            'errors': 0,
            'start_time': None
        }
        
        self.load_accounts()
        self.load_comments()
        
    def load_accounts(self):
        """Load accounts from JSON file"""
        try:
            with open(self.config['accounts_file'], 'r', encoding='utf-8') as file:
                self.accounts = json.load(file)
            logger.info(f"Loaded {len(self.accounts)} accounts")
        except FileNotFoundError:
            logger.warning("Accounts file not found, creating template")
            self.create_accounts_template()
        except Exception as e:
            logger.error(f"Error loading accounts: {e}")
            
    def load_comments(self):
        """Load comments from JSON file"""
        try:
            with open(self.config['comments_file'], 'r', encoding='utf-8') as file:
                self.comments = json.load(file)
            logger.info(f"Loaded {len(self.comments)} comments")
        except FileNotFoundError:
            logger.warning("Comments file not found, creating template")
            self.create_comments_template()
        except Exception as e:
            logger.error(f"Error loading comments: {e}")
            
    def create_accounts_template(self):
        """Create template accounts file"""
        template = [
            {
                "email": "account1@gmail.com",
                "password": "password123",
                "name": "User One",
                "enabled": True
            },
            {
                "email": "account2@gmail.com", 
                "password": "password456",
                "name": "User Two",
                "enabled": True
            }
        ]
        
        with open(self.config['accounts_file'], 'w', encoding='utf-8') as file:
            json.dump(template, file, indent=2)
            
    def create_comments_template(self):
        """Create template comments file"""
        template = [
            "Great stream! Keep it up!",
            "Amazing content as always!",
            "Love watching your streams!",
            "Thanks for the entertainment!",
            "You're doing great!",
            "Keep up the good work!",
            "This is so interesting!",
            "Really enjoying this!",
            "Awesome stream quality!",
            "Can't wait for the next stream!",
            "Your content is the best!",
            "Love the energy!",
            "This made my day!",
            "Such good vibes!",
            "You're amazing!"
        ]
        
        with open(self.config['comments_file'], 'w', encoding='utf-8') as file:
            json.dump(template, file, indent=2)
            
    def create_driver(self, account=None):
        """Create Chrome driver instance"""
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Add user agent randomization
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        options.add_argument(f'--user-agent={random.choice(user_agents)}')
        
        # Use different profiles for each account
        if account:
            profile_dir = f"/tmp/chrome_profile_{account['email'].replace('@', '_').replace('.', '_')}"
            options.add_argument(f'--user-data-dir={profile_dir}')
            
        try:
            driver = webdriver.Chrome(options=options)
            return driver
        except Exception as e:
            logger.error(f"Error creating Chrome driver: {e}")
            return None
            
    def login_to_youtube(self, driver, account):
        """Login to YouTube with account"""
        try:
            driver.get('https://accounts.google.com/signin')
            
            # Enter email
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_input.send_keys(account['email'])
            
            # Click next
            next_button = driver.find_element(By.ID, "identifierNext")
            next_button.click()
            
            # Enter password
            password_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            password_input.send_keys(account['password'])
            
            # Click next
            password_next = driver.find_element(By.ID, "passwordNext")
            password_next.click()
            
            # Wait for login to complete
            WebDriverWait(driver, 15).until(
                EC.url_contains("myaccount.google.com")
            )
            
            logger.info(f"Successfully logged in with {account['email']}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging in with {account['email']}: {e}")
            return False
            
    def navigate_to_stream(self, driver, channel_url):
        """Navigate to live stream"""
        try:
            # Go to channel
            driver.get(channel_url)
            
            # Look for live stream
            live_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/live')]"))
            )
            live_button.click()
            
            # Wait for chat to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "chat"))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error navigating to stream: {e}")
            return False
            
    def post_comment(self, driver, comment):
        """Post a comment to the live chat"""
        try:
            # Find chat input
            chat_input = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "input"))
            )
            
            # Clear and type comment
            chat_input.clear()
            chat_input.send_keys(comment)
            
            # Send comment
            send_button = driver.find_element(By.ID, "send-button")
            send_button.click()
            
            self.stats['comments_posted'] += 1
            logger.info(f"Posted comment: {comment[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            self.stats['errors'] += 1
            return False
            
    def run_comment_cycle(self):
        """Main comment bot cycle"""
        while self._is_running:
            try:
                if not self.accounts or not self.comments:
                    logger.warning("No accounts or comments available")
                    time.sleep(60)
                    continue
                    
                # Select random account and comment
                account = random.choice([acc for acc in self.accounts if acc.get('enabled', True)])
                comment = random.choice(self.comments)
                
                # Create driver
                driver = self.create_driver(account)
                if not driver:
                    continue
                    
                try:
                    # Login and navigate to stream
                    if self.login_to_youtube(driver, account):
                        # You'll need to set the actual channel URL
                        channel_url = "https://youtube.com/@yourchannel/live"
                        
                        if self.navigate_to_stream(driver, channel_url):
                            self.post_comment(driver, comment)
                            
                except Exception as e:
                    logger.error(f"Error in comment cycle: {e}")
                    self.stats['errors'] += 1
                finally:
                    driver.quit()
                    
                # Random delay between comments
                min_delay = self.config.get('min_delay', 30)
                max_delay = self.config.get('max_delay', 180)
                delay = random.randint(min_delay, max_delay)
                logger.info(f"Waiting {delay} seconds before next comment")
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error in comment bot cycle: {e}")
                time.sleep(30)
                
    def start(self):
        """Start the comment bot"""
        if self._is_running:
            return False
            
        self._is_running = True
        self.stats['start_time'] = time.time()
        self.thread = threading.Thread(target=self.run_comment_cycle, daemon=True)
        self.thread.start()
        
        logger.info("Comment bot started")
        return True
        
    def stop(self):
        """Stop the comment bot"""
        self._is_running = False
        
        # Close all drivers
        for driver in self.drivers:
            try:
                driver.quit()
            except:
                pass
        self.drivers.clear()
        
        logger.info("Comment bot stopped")
        
    def is_running(self):
        """Check if bot is running"""
        return self._is_running
        
    def get_stats(self):
        """Get bot statistics"""
        stats = self.stats.copy()
        if stats['start_time']:
            stats['runtime'] = time.time() - stats['start_time']
        return stats
