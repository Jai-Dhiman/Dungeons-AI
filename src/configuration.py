import os
from dataclasses import fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from dataclasses import dataclass

DEFAULT_BLOG_STRUCTURE = """The D&D campaign story should follow this epic adventure structure:

1. Prologue: The Gathering (1 section)
   - Mysterious opening scene or prophecy
   - Introduction to the world and initial threat
   - The call to adventure that brings heroes together
   - 200-300 words of atmospheric storytelling

2. Main Campaign Chapters (3-4 sections)
   Chapter 1: The Heroes
      * Detailed introduction of 3 characters (Wizard, Rogue, Fighter)
      * Their backgrounds, motivations, and how they meet
      * Character sheets and starting equipment
      * 400-500 words
   
   Chapter 2: The World Awakens
      * Campaign setting and starting location
      * Local NPCs and factions
      * Environmental details and atmosphere
      * 400-500 words
   
   Chapter 3: Quests and Perils
      * Main quest revelation
      * Side quests for each character
      * Encounters and combat scenarios
      * 400-500 words

3. Epilogue: Destiny Awaits (1 section)
   - Climactic battle or challenge
   - Resolution and character growth
   - Hints at future adventures
   - 200-300 words of epic conclusion"""

@dataclass(kw_only=True)
class Configuration:
    """The configurable fields for the chatbot."""
    blog_structure: str = DEFAULT_BLOG_STRUCTURE
    
    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})