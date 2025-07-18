from ..utils import *

@event_preprocessor
async def block_banned_groups(event):
    if hasattr(event, 'group_id') and event.group_id in BANNED_GROUPS:
        raise IgnoredException(f"{event.__class__.__name__} is ignored from Group {event.group_id}")
    if hasattr(event, 'user_id') and event.user_id in BANNED_PEOPLE:
        raise IgnoredException(f"{event.__class__.__name__} is ignored from User {event.user_id}")