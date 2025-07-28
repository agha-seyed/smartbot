from .cmd_start import handlers as start_handlers
from .profile_handler import handlers as profile_handlers
from .file_handler import handlers as file_handlers
from .question_handler import handlers as question_handlers
from .weather_handler import handlers as weather_handlers
from .consult_handler import handlers as consult_handlers
from .isee_handler import handlers as isee_handlers
from .gamification_handler import handlers as gamification_handlers
from .live_chat_handler import handlers as live_chat_handlers
from .location_handler import handlers as location_handlers
from .feedback_handler import handlers as feedback_handlers
from .apps_guide_handler import handlers as apps_guide_handlers
from .admin_handler import handlers as admin_handlers
from .search_handler import handlers as search_handlers
from .menu_handler import handlers as menu_handlers
from .submenu_handler import handlers as submenu_handlers
from .static_info_handler import handlers as static_info_handlers
from .audio_handler import handlers as audio_handlers

__all__ = [
    "start_handlers",
    "profile_handlers",
    "file_handlers",
    "question_handlers",
    "weather_handlers",
    "consult_handlers",
    "isee_handlers",
    "gamification_handlers",
    "live_chat_handlers",
    "location_handlers",
    "feedback_handlers",
    "apps_guide_handlers",
    "admin_handlers",
    "search_handlers",
    "menu_handlers",
    "submenu_handlers",
    "static_info_handlers",
    "audio_handlers",
]
