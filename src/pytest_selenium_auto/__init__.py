from .wrappers import CustomSelect as Select

supported_browsers = ("firefox", "chrome", "chromium", "edge", "safari")
screenshot_strategies = ('all', 'failed', 'last', 'manual', 'none')

__all__ = ["Select"]
