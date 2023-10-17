from .wrappers import CustomSelect as Select

__all__ = ["Select"]

supported_browsers = ("firefox", "chrome", "chromium", "edge", "safari")

screenshot_strategies = ('all', 'failed', 'last', 'manual', 'none')

action_keywords = {
    '$select': ("Select", "Deselect"),
    '$check': ("Check", "Uncheck"),
    '$set': ("Set", "Unset"),
    '$add': ("Add", "Remove"),
}

value_keywords = [
    '$text',
    '$value',
    '$name',
    '$id',
    '$index',
]
