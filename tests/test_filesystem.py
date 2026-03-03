from mcp_servers.filesystem_server import get_profile, update_profile
from user_profile.schema import UserProfile

def test_read_write_profile():
    original = get_profile()
    original.interests = ["AI", "Python"]
    update_profile(original)
    
    reloaded = get_profile()
    assert reloaded.interests == ["AI", "Python"]
    update_profile(UserProfile()) # Reset profile to empty after test