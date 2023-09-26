from . import screenshot_strategies
from . import supported_browsers


def get_marker_browser(node):
    value = node.iter_markers("browser")
    value = next(value, None)
    if value is not None:
        value = value.args[0]
    if value not in supported_browsers:
        value = None
    return value


def get_marker_screenshots(node):
    value = node.iter_markers("screenshots")
    value = next(value, None)
    if value is not None:
        value = value.args[0]
    if value not in screenshot_strategies:
        value = None
    return value


def get_marker_verbose(node):
    value = node.iter_markers("show_attributes")
    return next(value, None) is not None


def get_marker_pause(node):
    value = node.iter_markers("pause")
    value = next(value, None)
    if value is not None:
        try:
            value = int(value.args[0])
        except:
            value = None
    return value


def get_marker_window(node):
    opts = dict()
    for m in node.iter_markers("window"):
        opts.update(m.kwargs)
    window = dict()
    for key in ('headless', 'maximize', 'minimize', 'fullscreen'):
        if key in opts:
            window[key] = opts[key]
            del opts[key]
    if 'x' in opts and 'y' in opts and 'width' in opts and 'height' in opts:
        window['rect'] = opts
    if 'x' in opts and 'y' in opts and 'width' not in opts and 'height' not in opts:
        window['position'] = opts
    if 'x' not in opts and 'y' not in opts and 'width' in opts and 'height' in opts:
        window['size'] = opts
    return window


'''
def get_marker_settings(node):
    opts = dict()
    for m in node.iter_markers("settings"):
        opts.extend(m.args)
    return opts


def get_marker_options(node):
    opts = dict()
    for m in node.iter_markers("options"):
        opts.extend(m.args)
    return opts


def get_marker_capabilities(node):
    opts = dict()
    for m in node.iter_markers("capabilities"):
        opts.extend(m.args)
    return opts
'''
