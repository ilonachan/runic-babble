import runicbabble.lang
import re


class Madouji(runicbabble.lang.Language):
    def name(self):
        return 'madouji'

    def is_responsible(self, message):
        return re.match(r'^```mdj[ \n].*```$', message) is not None

    def format(self, message):
        # No formatting needs to be done
        txt = re.match(r'^```mdj[ \n].*```$', message).group(1).strip()
        return txt.replace('a\'', 'á', )

    def font_path(self):
        return 'config/res/fonts/Madouji.ttf'
