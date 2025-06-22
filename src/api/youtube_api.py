import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

logger = logging.getLogger(__name__)

class YouTubeAPI:
    def __init__(self, config):
        self.config = config
        self.youtube = None
        self.credentials = None
        self.scopes = [
            'https://www.googleapis.com/auth/youtube',
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
        
        self.authenticate()
        
    def authenticate(self):
        """Authenticate with YouTube API"""
        creds = None
        token_file = 'config/token.pickle'
        
        # Load existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                creds = pickle.load(token)
                
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config['client_secrets_file'], self.scopes
                )
                creds = flow.run_local_server(port=0)
                
            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(creds, token)
                
        self.credentials = creds
        self.youtube = build('youtube', 'v3', credentials=creds)
        logger.info("YouTube API authenticated successfully")
        
    def get_channel_info(self, channel_id=None):
        """Get channel information"""
        try:
            if not channel_id:
                channel_id = self.config['channel_id']
                
            request = self.youtube.channels().list(
                part='snippet,statistics,status',
                id=channel_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting channel info: {e}")
            return None
            
    def get_live_streams(self, channel_id=None):
        """Get live streams for channel"""
        try:
            if not channel_id:
                channel_id = self.config['channel_id']
                
            request = self.youtube.search().list(
                part='snippet',
                channelId=channel_id,
                eventType='live',
                type='video',
                maxResults=10
            )
            response = request.execute()
            
            return response['items']
            
        except Exception as e:
            logger.error(f"Error getting live streams: {e}")
            return []
            
    def get_stream_details(self, video_id):
        """Get detailed information about a stream"""
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics,liveStreamingDetails',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                return response['items'][0]
            return None
            
        except Exception as e:
            logger.error(f"Error getting stream details: {e}")
            return None
            
    def get_live_chat_id(self, video_id):
        """Get live chat ID for a video"""
        try:
            video_details = self.get_stream_details(video_id)
            if video_details and 'liveStreamingDetails' in video_details:
                return video_details['liveStreamingDetails'].get('activeLiveChatId')
            return None
            
        except Exception as e:
            logger.error(f"Error getting live chat ID: {e}")
            return None
            
    def get_chat_messages(self, live_chat_id, page_token=None):
        """Get live chat messages"""
        try:
            request = self.youtube.liveChatMessages().list(
                liveChatId=live_chat_id,
                part='snippet,authorDetails',
                pageToken=page_token
            )
            response = request.execute()
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting chat messages: {e}")
            return None
            
    def post_chat_message(self, live_chat_id, message):
        """Post message to live chat"""
        try:
            request = self.youtube.liveChatMessages().insert(
                part='snippet',
                body={
                    'snippet': {
                        'liveChatId': live_chat_id,
                        'type': 'textMessageEvent',
                        'textMessageDetails': {
                            'messageText': message
                        }
                    }
                }
            )
            response = request.execute()
            
            logger.info(f"Posted chat message: {message}")
            return response
            
        except Exception as e:
            logger.error(f"Error posting chat message: {e}")
            return None
            
    def create_live_stream(self, title, description, privacy_status='public'):
        """Create a new live stream"""
        try:
            # Create live broadcast
            broadcast_request = self.youtube.liveBroadcasts().insert(
                part='snippet,status',
                body={
                    'snippet': {
                        'title': title,
                        'description': description,
                        'scheduledStartTime': '2024-01-01T00:00:00Z'  # Will be updated
                    },
                    'status': {
                        'privacyStatus': privacy_status
                    }
                }
            )
            broadcast_response = broadcast_request.execute()
            
            # Create live stream
            stream_request = self.youtube.liveStreams().insert(
                part='snippet,cdn',
                body={
                    'snippet': {
                        'title': f"{title} - Stream"
                    },
                    'cdn': {
                        'resolution': '1080p',
                        'frameRate': '30fps',
                        'ingestionType': 'rtmp'
                    }
                }
            )
            stream_response = stream_request.execute()
            
            # Bind broadcast to stream
            bind_request = self.youtube.liveBroadcasts().bind(
                part='id,contentDetails',
                id=broadcast_response['id'],
                streamId=stream_response['id']
            )
            bind_response = bind_request.execute()
            
            return {
                'broadcast': broadcast_response,
                'stream': stream_response,
                'bind': bind_response
            }
            
        except Exception as e:
            logger.error(f"Error creating live stream: {e}")
            return None
            
    def get_stream_analytics(self, video_id):
        """Get analytics for a stream"""
        try:
            # Get basic video statistics
            video_details = self.get_stream_details(video_id)
            
            if not video_details:
                return None
                
            analytics = {
                'view_count': int(video_details['statistics'].get('viewCount', 0)),
                'like_count': int(video_details['statistics'].get('likeCount', 0)),
                'comment_count': int(video_details['statistics'].get('commentCount', 0)),
                'concurrent_viewers': 0  # This requires YouTube Analytics API
            }
            
            # Get concurrent viewers if live
            if 'liveStreamingDetails' in video_details:
                live_details = video_details['liveStreamingDetails']
                if 'concurrentViewers' in live_details:
                    analytics['concurrent_viewers'] = int(live_details['concurrentViewers'])
                    
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting stream analytics: {e}")
            return None
            
    def search_videos(self, query, max_results=10):
        """Search for videos"""
        try:
            request = self.youtube.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results
            )
            response = request.execute()
            
            return response['items']
            
        except Exception as e:
            logger.error(f"Error searching videos: {e}")
            return []
            
    def get_video_comments(self, video_id, max_results=100):
        """Get comments for a video"""
        try:
            request = self.youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=max_results,
                order='relevance'
            )
            response = request.execute()
            
            return response['items']
            
        except Exception as e:
            logger.error(f"Error getting video comments: {e}")
            return []
