from server.core import AbstractAeneaPlatformRpcs

class DummyPlatformRpc(AbstractAeneaPlatformRpcs):
    def __init__(self, xdo_delay=0, display=None, **kwargs):
        """
        :param int xdo_delay: Default pause between keystrokes.
        :param str display: reserved for future use.
        :param kwargs:
        """
        super(DummyPlatformRpc, self).__init__(**kwargs)

    def server_info(self):
        return {
            'window_manager': 'idk',
            'operating_system': 'linux',
            'platform': 'linux',
            'display': 'X11',
            'server': 'x11_libxdo',
            'server_version': 1
        }
    def get_context(self):
        pass
    def key_press(self, key=None, modifiers=(), direction='press', count=1,
                  count_delay=None):
        pass
    def write_text(self, text):
        pass
    def click_mouse(self, button, direction='click', count=1, count_delay=None):
        pass
    def move_mouse(self, x, y, reference='absolute', proportional=False,
                   phantom=None):
        pass
    def notify(self, message):
        pass
