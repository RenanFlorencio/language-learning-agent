PROMPT = """Reflect on the conversation and update the user profile 
based on any new information provided by the user.

Consider updating:
- interests: if user expresses interest in new topics
- dislikes: if user expresses dislike for topics
- language_levels: if user mentions their current level
- saved_channels_id: if user wants to save a channel
- channel_ratings: if user rates a channel
- video_ratings: if user rates a video

Only update fields that are explicitly mentioned or clearly implied 
by the conversation. Do not modify fields that were not mentioned.
"""