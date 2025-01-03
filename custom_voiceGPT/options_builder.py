from collections import defaultdict


class OptionsBuilder:
    def __init__(self):
        self.__text_options: defaultdict = defaultdict(dict)
        self.sideBar: dict = dict()

    @staticmethod
    def create():
        gb: OptionsBuilder = OptionsBuilder()
        return gb

    def configure_background_color(self, background_color):
        self.configure_options(background_color=background_color)

    def configure_text_color(self, text_color):
        self.configure_options(text_color=text_color)

    def configure_font_style(self, font_style):
        self.configure_options(font_style=font_style)

    def configure_options(self, **props):
        """Merges props to gridOptions

        Args:
            props (dict): props dicts will be merged to gridOptions root.
        """
        self.__text_options.update(props)

    def build(self):
        return self.__text_options
