import webbrowser
from urllib.parse import quote

try:
    from youtubesearchpython import VideosSearch
except ImportError:
    VideosSearch = None
    print("⚠️ YouTubeSearchPython not available - using yt-dlp search only")


class YouTubeService:
    """Handles YouTube integration for JARVIS AI"""

    def __init__(self, config):
        """
        Initialize YouTube service

        Args:
            config: Configuration object
        """
        self.config = config

    def search_youtube(self, query):
        """
        Search YouTube and open results in browser

        Args:
            query (str): Search query
        """
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
        webbrowser.open(search_url)
        print(f"🔍 Searching YouTube for: {query}")

    def play_youtube_video(self, query):
        """
        Play YouTube video directly using yt-dlp

        Args:
            query (str): Video to search and play

        Returns:
            bool: True if successful, False otherwise
        """
        print(f"🎵 Searching YouTube with yt-dlp for: {query}")
        try:
            from yt_dlp import YoutubeDL

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
                'default_search': 'ytsearch1',
            }

            search_query = f"ytsearch1:{query}"
            print("🔎 Using search query:", search_query)

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)

            if not info:
                print("❌ No information returned by yt-dlp")
                raise ValueError("No info from yt-dlp")

            entries = None
            if isinstance(info, dict):
                entries = info.get('entries') or [info]

            if not entries:
                print("❌ No entries found in yt-dlp results")
                raise ValueError("No entries in results")

            first = entries[0] if entries else None
            if not first:
                print("❌ First result missing")
                raise ValueError("Missing first result")

            video_id = first.get('id')
            title = first.get('title') or query

            if not video_id:
                print("❌ Could not extract video ID")
                raise ValueError("No video id")

            video_url = f"https://www.youtube.com/watch?v={video_id}"
            print(f"✅ Found: {title}")
            print(f"🎬 Opening: {video_url}")

            webbrowser.open(video_url)
            return True

        except ImportError:
            print("❌ yt-dlp not installed. Install with: pip install yt-dlp")
            # Fallback to standard YouTube search
            self.search_youtube(query)
            return False
        except Exception as e:
            print(f"YouTube yt-dlp error: {e}")
            print("🔄 Falling back to standard YouTube search...")
            self.search_youtube(query)
            return False

    def search_youtube_api(self, query, limit=5):
        """
        Search YouTube and return video information

        Args:
            query (str): Search query
            limit (int): Maximum number of results

        Returns:
            list: List of video dictionaries
        """
        if VideosSearch is None:
            print("YouTubeSearchPython not available - no search results available")
            return []

        try:
            videos_search = VideosSearch(query, limit=limit)
            results = videos_search.result()

            videos = []
            if results and 'result' in results:
                for video in results['result']:
                    videos.append({
                        'title': video.get('title', ''),
                        'link': video.get('link', ''),
                        'duration': video.get('duration', ''),
                        'views': video.get('viewCount', {}).get('short', ''),
                        'thumbnail': video.get('thumbnails', [{}])[0].get('url', ''),
                        'channel': video.get('channel', {}).get('name', ''),
                        'upload_time': video.get('publishedTime', '')
                    })

            return videos

        except Exception as e:
            print(f"YouTube API search error: {e}")
            return []

    def get_video_info(self, video_url):
        """
        Get detailed information about a YouTube video

        Args:
            video_url (str): YouTube video URL

        Returns:
            dict: Video information
        """
        try:
            from yt_dlp import YoutubeDL

            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
            }

            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=False)

            if info:
                return {
                    'title': info.get('title', ''),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', ''),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', '')[:500],  # First 500 chars
                    'upload_date': info.get('upload_date', ''),
                    'thumbnail': info.get('thumbnail', '')
                }

        except Exception as e:
            print(f"Video info error: {e}")
            return None

    def create_playlist(self, videos):
        """
        Create a playlist from video list

        Args:
            videos (list): List of video URLs or queries

        Returns:
            list: List of processed video information
        """
        playlist = []
        for video in videos:
            if 'youtube.com' in video or 'youtu.be' in video:
                # Direct URL
                info = self.get_video_info(video)
                if info:
                    playlist.append(info)
            else:
                # Search query
                search_results = self.search_youtube_api(video, limit=1)
                if search_results:
                    playlist.append(search_results[0])

        return playlist