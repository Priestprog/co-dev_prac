import gettext
import os
import locale

_podir = os.path.join(os.path.dirname(__file__), "po")
translation = gettext.translation("messages", _podir, fallback=True)
_, ngettext = translation.gettext, translation.ngettext

LOCALES = {
    ("ru_RU", "UTF-8"): gettext.translation("messages", "po", ["ru"]),
    ("en_US", "UTF-8"): gettext.NullTranslations(),
}

def _(text):
    return LOCALES[locale.getlocale()].gettext(text)

while True:
        try:
            line = input()
            for loc in LOCALES:
                locale.setlocale(locale.LC_ALL, loc)
                words = line.split()
                count = len(words)
                print(_("Entered"), ngettext("{} word", "{} words", count).format(count))
        except KeyboardInterrupt:
            print("\nEXIT")
            break
