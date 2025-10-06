import json
from typing import Dict, Any

class UserPreferences:
    def __init__(self, user_id: str, storage_path: str = 'data/user_preferences'):
        self.user_id = user_id
        self.storage_path = storage_path
        self.preferences = {
            "theme": "light",                # Options: light, dark
            "font_size": 14,                  # Integer font size
            "notifications_enabled": True,    # Enable/disable notifications
            "auto_save_interval": 5,          # Minutes
            "language": "en",                # Language code
            "show_line_numbers": True,        # Code editor setting
            "spell_check": True,               # Enable/disable spell check
            "custom_shortcuts": {},            # Dict of shortcut_name: key_combination
            "text_alignment": "left",        # left, center, right
            "autosuggest_enabled": True        # Enable/disable autosuggest
        }

        self.load_preferences()

    def get_preferences(self) -> Dict[str, Any]:
        return self.preferences

    def update_preferences(self, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if key in self.preferences:
                self.preferences[key] = value
            else:
                raise KeyError(f"Invalid preference key: {key}")

        self.save_preferences()

    def reset_preferences(self) -> None:
        self.preferences = {
            "theme": "light",
            "font_size": 14,
            "notifications_enabled": True,
            "auto_save_interval": 5,
            "language": "en",
            "show_line_numbers": True,
            "spell_check": True,
            "custom_shortcuts": {},
            "text_alignment": "left",
            "autosuggest_enabled": True
        }
        self.save_preferences()

    def save_preferences(self) -> None:
        import os
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)
        file_path = f"{self.storage_path}/{self.user_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.preferences, f, indent=4)

    def load_preferences(self) -> None:
        import os
        file_path = f"{self.storage_path}/{self.user_id}.json"
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                self.preferences = json.load(f)


# Example usage:
# user_prefs = UserPreferences(user_id='user123')
# print(user_prefs.get_preferences())
# user_prefs.update_preferences({'theme': 'dark', 'font_size': 16})
# user_prefs.reset_preferences()
