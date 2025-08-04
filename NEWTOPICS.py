# -*- coding: utf-8 -*-
import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyBu1zf8TICLclqaYW8S5HzYgvPawzTQ4E8"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

# App Title
st.title("YouTube Viral Topic Finder (Business + English Only)")

# Input
niche = st.text_input("Enter Your Business Niche (e.g. AI, Startup, Tech Collapse):")
days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

# Generate smart business-related keywords
def generate_keywords(niche):
    base_phrases = [
        "business news", "startup collapse", "company drama", "tech layoffs",
        "business strategy", "founder scandal", "AI business", "corporate downfall",
        "CEO controversy", "Silicon Valley news", "tech company collapse",
        "business takeover", "AI startup", "big tech monopoly", "VC failure"
    ]
    return [f"{niche} {phrase}" for phrase in base_phrases]

if st.button("Find Trending Business Videos"):
    if not niche:
        st.warning("Please enter a business niche to continue.")
    else:
        try:
            keywords = generate_keywords(niche)
            start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
            all_results = []

            for keyword in keywords:
                st.write(f"Searching: {keyword}")

                search_params = {
                    "part": "snippet",
                    "q": keyword,
                    "type": "video",
                    "order": "viewCount",
                    "publishedAfter": start_date,
                    "maxResults": 5,
                    "relevanceLanguage": "en",
                    "key": API_KEY,
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
                st.success(f"Found {len(all_results)} trending videos for: {niche}")
                for result in all_results:
                    st.markdown(
                        f"**Title:** {result['Title']}  \n"
                        f"**Description:** {result['Description']}  \n"
                        f"**URL:** [Watch Video]({result['URL']})  \n"
                        f"Views: {result['Views']} | Subscribers: {result['Subscribers']:,}"
                    )
                    st.write("---")
            else:
                st.warning("No business-related viral videos found for this niche.")

        except Exception as e:
            st.error(f"Error: {e}")
