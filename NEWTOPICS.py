import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyBu1zf8TICLclqaYW8S5HzYgvPawzTQ4E8"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# App Title
st.title("\ud83d\udcca YouTube Viral Topic Finder (Business + English Only)")

# Inputs
niche = st.text_input("\ud83c\udfaf Enter Your Business Niche (e.g. 'AI Business', 'Startup Collapse'):")
days = st.number_input("\ud83d\uddd3\ufe0f Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# Keyword Generator
def generate_keywords(niche):
    business_phrases = [
        "business war", "company drama", "tech collapse", "startup fail", 
        "AI impact", "leadership change", "controversy explained", 
        "big tech scandal", "power shift", "corporate news", "industry insights",
        "executive drama", "market takeover", "business rivalry"
    ]
    return [f"{niche} {phrase}" for phrase in business_phrases]

# Main Function
if st.button("\ud83d\ude80 Find Trending Topics"):
    if not niche:
        st.warning("Please enter a niche to continue.")
    else:
        try:
            keywords = generate_keywords(niche)
            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            all_results = []

            for keyword in keywords:
                st.write(f"\ud83d\udd0d Searching: {keyword}")

                search_params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "order": "viewCount",
                    "publishedAfter": start_date,
                    "maxResults": 5,
                    "key": API_KEY,
                    "relevanceLanguage": "en",     # \ud83d\udd11 Only English
                    "safeSearch": "strict"         # Optional: avoids unrelated content
                }

                response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
                data = response.json()

                if "items" not in data or not data["items"]:
                    continue

                videos = data["items"]
                video_ids = [v["id"]["videoId"] for v in videos if "id" in v and "videoId" in v["id"]]
                channel_ids = [v["snippet"]["channelId"] for v in videos if "snippet" in v and "channelId" in v["snippet"]]

                if not video_ids or not channel_ids:
                    continue

                stats_data = requests.get(
                    YOUTUBE_VIDEO_URL,
                    params={"part": "statistics", "id": ",".join(video_ids), "key": API_KEY}
                ).json()

                channel_data = requests.get(
                    YOUTUBE_CHANNEL_URL,
                    params={"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY}
                ).json()

                stats = stats_data.get("items", [])
                channels = {item["id"]: item for item in channel_data.get("items", [])}

                for video, stat in zip(videos, stats):
                    vid = video["id"]["videoId"]
                    channel_id = video["snippet"]["channelId"]
                    channel_info = channels.get(channel_id, {})
                    title = video["snippet"].get("title", "N/A")
                    description = video["snippet"].get("description", "")[:200]
                    video_url = f"https://www.youtube.com/watch?v={vid}"
                    views = int(stat["statistics"].get("viewCount", 0))
                    subs = int(channel_info.get("statistics", {}).get("subscriberCount", 0))

                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs,
                        "Channel ID": channel_id
                    })

            if all_results:
                st.success(f"\u2705 Found {len(all_results)} trending business videos!")
                for result in all_results:
                    st.markdown(
                        f"**\ud83c\udfac Title:** {result['Title']}  \n"
                        f"**\ud83d\udcdd Description:** {result['Description']}  \n"
                        f"**\ud83d\udd17 URL:** [Watch Video]({result['URL']})  \n"
                        f"\ud83d\udc41\ufe0f Views:** {result['Views']} &nbsp;&nbsp; \ud83d\udc65 **Subscribers:** {result['Subscribers']:,}"
                    )
                    st.write("---")
            else:
                st.warning("\ud83d\udeab No trending business videos found for this niche. Try a broader topic!")

        except Exception as e:
            st.error(f"\u274c Error: {e}")
