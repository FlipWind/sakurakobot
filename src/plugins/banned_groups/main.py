from ..utils import *

@event_preprocessor
async def block_banned_groups(event):
    if hasattr(event, 'group_id') and event.group_id in BANNED_GROUPS:
        raise IgnoredException(f"{event.__class__.__name__} is ignored from Group {event.group_id}")