import yaml
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from user_profile.schema import UserProfile

mcp = FastMCP("user_profile_server")
PROFILE_PATH = Path(__file__).parent.parent / "user_profile" / "user_profile.yaml"

@mcp.resource("profile://user")
def get_profile() -> UserProfile:
    """Read the user profile"""
    if not PROFILE_PATH.exists():
        # If the profile file doesn't exist, create an empty profile
        return UserProfile()

    with open(PROFILE_PATH, "r") as f:
        data = yaml.safe_load(f) or {}
        return UserProfile(**data)

@mcp.tool()
def update_profile(profile: UserProfile) -> None:
    """Write updated profile to disk."""
    with open(PROFILE_PATH, "w") as f:
        yaml.dump(profile.model_dump(), f)
        
if __name__ == "__main__":
    mcp.run(transport="stdio")


# Granular tools, but that would explode the amount of tools we have, so for now we can just update the whole profile at once and let the MCP handle the merging of the old and new profile data.

# @mcp.tool()
# def add_channel_rating(channel_id: str, rating: float) -> None: 
#     """Add or update a channel rating in the user profile."""
#     profile = get_profile()
#     if profile is None:
#         raise Exception("User profile not found. Cannot add channel rating.")

#     if profile.channel_ratings is None:
#         profile.channel_ratings = {}

#     if rating < 0 or rating > 5:
#         raise ValueError("Rating must be between 0 and 5.")

#     profile.channel_ratings[channel_id] = rating
#     update_profile(profile)

# @mcp.tool()  
# def save_channel(channel_id: str) -> None: 
#     """Add a channel ID to the user's saved channels in the profile."""
#     profile = get_profile()
#     if profile is None:
#         raise Exception("User profile not found. Cannot save channel.")

#     if profile.saved_channels_id is None:
#         profile.saved_channels_id = []

#     if channel_id not in profile.saved_channels_id:
#         profile.saved_channels_id.append(channel_id)
#         update_profile(profile)
