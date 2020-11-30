from tkinter.font import Font


class Fonts(object):
    ''' Class holding fonts available to UI '''
    _font_map = {}

    @staticmethod
    def init():
        ''' Initialize all fonts '''
        Fonts._font_map['MessageAuthor'] = Font(family="Ariel",
                                                size=10,
                                                weight='bold')

        Fonts._font_map['MessageTimestamp'] = Font(family="Ariel",
                                                   size=7,
                                                   slant='italic')

        Fonts._font_map['MessageText'] = Font(family="Ariel", size=12)
        Fonts._font_map['EntryText'] = Font(family="Ariel", size=12)
        Fonts._font_map['EmptyArea'] = Font(family="Ariel", size=12)
        Fonts._font_map['AboutMain'] = Font(family="Ariel", size=14)

    @staticmethod
    def get(font_name):
        ''' Retrieves font with given identifier '''
        font = None

        try:
            font = Fonts._font_map[font_name]
        except KeyError:
            pass

        return font
