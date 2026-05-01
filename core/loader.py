# =============================================================================
#  Ether Userbot System
#
#  Project Name:  Ether
#  Author:        LearningBotsOfficial
#
#  Repository:    https://github.com/LearningBotsOfficial/Ether
#
#  Support:       https://t.me/Ether_Support
#  Channel:       https://t.me/Ether_Update
#
#  License:       Open Source (Keep Credits)
#
#  IMPORTANT:
#    - If you copy, fork, or reuse this project or any part of it,
#      you MUST retain original credits.
#    - Proper attribution to Ether project is required.
#
#  Thank you for respecting open-source development.
# =============================================================================

import importlib
import os
from pathlib import Path
from typing import List, Optional

from telethon import TelegramClient
from utils.logger import get_logger

logger = get_logger("EtherLoader")


class PluginLoader:
    
    PLUGINS_DIR = "plugins"
    
    def __init__(self, client: TelegramClient, db=None, owner_id: Optional[int] = None):
        self.client = client
        self.db = db
        self.owner_id = owner_id
        self.loaded: List[str] = []
    
    def load_all(self, client: Optional[TelegramClient] = None) -> None:
        """Load all plugins for the given client or the default client."""
        target_client = client or self.client
        plugins_path = Path(self.PLUGINS_DIR)
        
        if not plugins_path.exists():
            logger.warning(f"Plugins directory not found: {self.PLUGINS_DIR}")
            return
        
        # Find all .py files
        plugin_files = [
            f for f in plugins_path.glob("*.py")
            if f.is_file() and not f.name.startswith("__")
        ]
        
        for file_path in sorted(plugin_files):
            self._load_plugin(file_path, target_client)
        
        if not client:
            logger.info(f"Loaded {len(self.loaded)} plugins: {', '.join(self.loaded)}")
        else:
            logger.info(f"Loaded {len(plugin_files)} plugins for additional client")
    
    def _load_plugin(self, file_path: Path, client: TelegramClient) -> None:
        """Load a single plugin file for a specific client."""
        module_name = file_path.stem
        full_module = f"{self.PLUGINS_DIR}.{module_name}"
        
        try:
            # Import the module (or get from sys.modules if already loaded)
            module = importlib.import_module(full_module)
            # Re-import doesn't happen if it's already in sys.modules,
            # but we want to call setup() again with the new client.
            
            # Check for setup function
            if hasattr(module, "setup"):
                setup_func = getattr(module, "setup")
                setup_func(
                    ether=client,
                    db=self.db,
                    owner_id=self.owner_id
                )
                
                if module_name not in self.loaded:
                    self.loaded.append(module_name)
                logger.info(f" Loaded plugin {module_name} for client")
            else:
                logger.warning(f" Plugin {module_name} has no setup() function")
                
        except Exception as e:
            logger.error(f" Failed to load {module_name}: {e}")
    
    def get_stats(self) -> dict:
        return {
            "total": len(self.loaded),
            "plugins": self.loaded
        }
