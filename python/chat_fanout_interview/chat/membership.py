"""Room membership management."""

from typing import Set, Dict


class RoomMembershipStore:
    """Manages which users are in which rooms.
    
    Naive dictionary-based implementation.
    """
    
    def __init__(self):
        """Initialize membership store."""
        self._memberships: Dict[str, Set[str]] = {}
        
    def add_user(self, room_id: str, user_id: str):
        """Add a user to a room.
        
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        if room_id not in self._memberships:
            self._memberships[room_id] = set()
        self._memberships[room_id].add(user_id)
        
    def remove_user(self, room_id: str, user_id: str):
        """Remove a user from a room.
        
        Args:
            room_id: Room identifier
            user_id: User identifier
        """
        if room_id in self._memberships:
            self._memberships[room_id].discard(user_id)
            
    def list_users(self, room_id: str) -> Set[str]:
        """List all users in a room.
        
        Args:
            room_id: Room identifier
            
        Returns:
            Set of user identifiers in the room
        """
        return self._memberships.get(room_id, set()).copy()
