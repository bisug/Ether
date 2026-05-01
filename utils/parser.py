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

import re
from typing import Optional

# ============================================
# Parser Utilities
# ============================================

def parse_links(text: Optional[str]) -> str:
    if not text:
        return ""
    
    lines = text.split("\n")
    new_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Support -> https://link format
        if "->" in line:
            parts = line.split("->", 1)
            if len(parts) == 2:
                name = parts[0].strip()
                url = parts[1].strip()
                
                if url.startswith("http"):
                    line = f'<a href="{url}">{escape_html(name)}</a>'
        
        new_lines.append(line)
    
    return "\n".join(new_lines)


def escape_html(text: str) -> str:
    """Escape HTML special characters."""
    return (text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def format_command_list(commands: dict) -> str:
    lines = ["<b>Available Commands:</b>\n"]
    
    for cmd, desc in commands.items():
        lines.append(f"<code>{cmd}</code> - {escape_html(desc)}")
    
    return "\n".join(lines)


def truncate_text(text: str, max_length: int = 4000) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def extract_urls(text: str) -> list:
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'
    return re.findall(url_pattern, text)
