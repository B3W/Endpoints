from tkinter.font import Font


class Fonts(object):
    ''' Class holding fonts available to UI '''
    _font_map = {}

    @staticmethod
    def init():
        ''' Initialize all fonts '''
        Fonts._font_map['MessageAuthor'] = Font(family="Courier",
                                                size=14,
                                                weight='bold')
        Fonts._font_map['MessageTimestamp'] = Font(family="Courier",
                                                   size=8,
                                                   slant='italic')
        Fonts._font_map['MessageText'] = Font(family="Courier", size=12)

    @staticmethod
    def get(font_name):
        ''' Retrieves font with given identifier '''
        font = None

        try:
            font = Fonts._font_map[font_name]
        except KeyError:
            pass

        return font
