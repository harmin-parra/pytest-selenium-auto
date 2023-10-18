from .wrappers import CustomSelect as Select

__all__ = ["Select"]

supported_browsers = ("firefox", "chrome", "chromium", "edge", "safari")

screenshot_strategies = ("all", "failed", "last", "manual", "none")

# Action keywords for select and checkbox webelements.
action_keywords = {
    '$add': ("Add", "Remove"),
    '$check': ("Check", "Uncheck"),
    "$include": ("Include", "Exclude"),
    '$select': ("Select", "Deselect"),
    '$set': ("Set", "Unset"),
}

value_keywords = [
    '$id',
    '$index',
    '$name',
    '$text',
    '$value',
    '$visible_text',
]
