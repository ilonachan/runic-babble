import runicbabble.lang
import re


class Madouji(runicbabble.lang.Language):
    @property
    def name(self):
        return 'madouji'

    def is_responsible(self, message):
        return re.match(r'^```mdj\s.*```$', message, re.DOTALL) is not None

    def format(self, message):
        # No formatting needs to be done
        txt = re.match(r'^```mdj\s(.*)```$', message, re.DOTALL).group(1).strip()
        return txt.replace('a\'', 'á').replace('A\'', 'á')\
            .replace('e\'', 'é').replace('E\'', 'é')\
            .replace('i\'', 'í').replace('I\'', 'í')\
            .replace('o\'', 'ó').replace('O\'', 'ó')\
            .replace('u\'', 'ú').replace('U\'', 'ú')\
            .replace('y\'', 'ý').replace('Y\'', 'ý')\
            .replace('w\'', '\xb5').replace('W\'', '\xb5')

    def font_path(self, message):
        return 'config/res/fonts/Madouji.ttf'
