# =============================================================================
#  Ether Userbot System
#
#  Project Name:  Ether
#  Author:        LearningBotsOfficial
#
#  Repository:    https://github.com/LearningBotsOfficial/Ether
#
#  Support:       https://t.me/Ether_Support
#  Channel:       https://t.me/EtherUserbot
#
#  License:       Open Source (Keep Credits)
#
#  IMPORTANT:
#    • If you copy, fork, or reuse this project or any part of it,
#      you MUST retain original credits.
#    • Proper attribution to Ether project is required.
#
#  Thank you for respecting open-source development.
# =============================================================================

from typing import Optional, Dict, Any, List

# ============================================
# Shortcut Service Class
# ============================================
class ShortcutService:
    
    def __init__(self, db):
        self.shortcuts = db["shortcuts"] if db is not None else None
    
    async def save_shortcut(self, owner_id: int, name: str, text: str, 
                           image: Optional[str] = None, 
                           buttons: Optional[List[Dict[str, str]]] = None) -> bool:
        """Save a shortcut with the given name."""
        if self.shortcuts is None:
            return False
        
        data = {
            "owner_id": owner_id,
            "name": name.lower(),
            "text": text
        }
        
        if image:
            data["image"] = image
        else:
            data["image"] = None
        
        if buttons:
            data["buttons"] = buttons
        else:
            data["buttons"] = None
        
        await self.shortcuts.update_one(
            {"owner_id": owner_id, "name": name.lower()},
            {"$set": data},
            upsert=True
        )
        return True
    
    async def get_shortcut(self, owner_id: int, name: str) -> Optional[Dict[str, Any]]:
        if self.shortcuts is None:
            return None
        
        result = await self.shortcuts.find_one({
            "owner_id": owner_id,
            "name": name.lower()
        })
        return result
    
    async def delete_shortcut(self, owner_id: int, name: str) -> bool:
        if self.shortcuts is None:
            return False
        
        result = await self.shortcuts.delete_one({
            "owner_id": owner_id,
            "name": name.lower()
        })
        return result.deleted_count > 0
    
    async def list_shortcuts(self, owner_id: int) -> List[str]:
        if self.shortcuts is None:
            return []
        
        cursor = self.shortcuts.find(
            {"owner_id": owner_id},
            {"name": 1, "_id": 0}
        )
        shortcuts = await cursor.to_list(length=None)
        return [s["name"] for s in shortcuts]
