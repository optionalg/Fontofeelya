import re
import os
import sublime
import sublime_plugin

DICT_REGEX = re.compile(r'\s*(<dict>[\S\s]*?<key>\s*settings\s*</key>\s*<dict>[\S\s]*?</dict>\s*</dict>)\s*')
KEY_STRING_REGEX = re.compile(r'\s*<key>(?P<k>[^<]+)</key>\s*<string>(?P<v>[^<]*)</string>\s*')
COLOR_REGEX = re.compile(r'^#(?P<r>[a-f\d]{1,2})(?P<g>[a-f\d]{1,2})(?P<b>[a-f\d]{1,2})(?P<a>[a-f\d]{2})?$', re.IGNORECASE)


class ColorScheme(object):

    """Encapsulates color scheme properties/contents and provides methods for parsing,
    serializing and selecting tmTheme files."""
    def __init__(self, settings='Preferences.sublime-settings'):
        if isinstance(settings, "".__class__):
            self.settings_id, settings = settings, sublime.load_settings(settings)
        if isinstance(settings, sublime.Settings):
            self.source = settings.get('color_scheme', 'Packages/Color Scheme - Default/Monokai.tmTheme')
            self.content = sublime.load_resource(self.source)

    # There has to be a more clever way to do this, but I suck at Python
    # and this appears to get her done. By her I mean split the file into fancy
    # dict objects with key/value according to each key/string of the scheme's
    # settings. Accepts an optional map function for transforming on the fly
    def parse_content(self, mapfn=None):
        parsed = []
        dicts = DICT_REGEX.split(self.content)
        for d in dicts:
            # If the piece isn't empty
            if d != '':
                dobj = dict({'src': d})
                for k in KEY_STRING_REGEX.finditer(d):
                    if COLOR_REGEX.match(k.group(2)):
                        dobj[k.group(1)] = Color(k.group(2))
                    else:
                        dobj[k.group(1)] = k.group(2)
                if mapfn:
                    dobj = mapfn(dobj) or dobj
                parsed.append(dobj)
        self.parsed = parsed
        return self

    # Rebuilds the parsed plist data with any changes made to objects containing name
    # and scope,
    def serialize_parsed(self, data=None):
        data = data or self.parsed
        result = ''
        if data:
            doneroot = False
            for pref in data:
                name = pref.get('name', None)
                scope = pref.get('scope', None)
                if name and scope:
                    fontStyle = pref.get('fontStyle', None)
                    foreground = pref.get('foreground', None)
                    background = pref.get('background', None)
                    result += """
                        <dict>
                            <key>name</key>
                            <string>%s</string>
                            <key>scope</key>
                            <string>%s</string>
                            <key>settings</key>
                                <dict>
                        """ % (name, scope)
                    if fontStyle != None:
                        result += "<key>fontStyle</key>\n<string>%s</string>\n" % (fontStyle)
                    if background != None:
                        result += "<key>background</key>\n<string>%s</string>\n" % (background.__str__())
                    if foreground != None:
                        result += "<key>foreground</key>\n<string>%s</string>\n" % (foreground.__str__())
                    result += "</dict>\n</dict>\n"
                elif name and not doneroot:
                    comment = pref.get('comment', None)
                    result += "<dict>\n<key>name</key>\n<string>%s</string>\n" % (name)
                    if comment:
                        result += "<key>comment</key>\n<string>%s</string>\n" % (comment)
                    result += "<key>settings</key>\n<array>\n<dict><key>settings</key><dict>\n"
                    for item in pref.items():
                        if isinstance(item[1], Color):
                            result += "<key>%s</key>\n<string>%s</string>\n" % (item[0], item[1].__str__())
                        elif isinstance(item[1], "".__class__):
                            # TODO: fontStyle is the only non-color I can think of, but  I should refactor this
                            # whole method, as there are too many of these hard-coded hacks
                            if item[0] == "fontStyle":
                                result += "<key>%s</key>\n<string>%s</string>\n" % (item[0], item[1])
                    result += "</dict>\n</dict>\n"
                    doneroot = True
                else:
                    result += pref.get('src', '')
            # print(result)
            self.content = result
        return self

    # Save to fontofeelya directory
    def save_to_fontofeelya(self, filename=None):
        filename = filename or os.path.split(self.source)[1]
        fullpath = os.path.join(sublime.packages_path(), 'Fontofeelya', 'color_schemes', filename)
        open(fullpath, 'w+').write(self.content)
        self.source = os.path.join('Packages', 'Fontofeelya', 'color_schemes', filename)

    # Update color_scheme setting with self.source
    def update_settings(self, settings=None):
        settings = settings or self.settings_id or 'Preferences.sublime-settings'
        if isinstance(settings, "".__class__):
            settings = sublime.load_settings(settings)
        if isinstance(settings, sublime.Settings):
            settings.set('color_scheme', self.source)

    # Just a shortcut for executing the three methods above in succession
    def serial_save_update(self):
        self.serialize_parsed()
        self.save_to_fontofeelya()
        self.update_settings()

    # Handy Dandy method to map the fg/bg colors to a single function or split
    # them into separate functions (pass at least 2 functions for the latter)
    # Can also map any other Color objects to a third function, if desired
    def map_colors(self, fgfn, bgfn=None, miscfn=None):
        result = []
        for pref in self.parsed:
            dir(pref)
            for item in pref.items():
                if item[0] == 'foreground':
                    pref['foreground'] = fgfn(item[1]) or item[1]
                elif item[0] == 'background':
                    if bgfn:
                        pref['background'] = bgfn(item[1]) or item[1]
                    else:
                        pref['background'] = fgfn(item[1]) or item[1]
                elif isinstance(item[1], Color):
                    if miscfn:
                        pref[item[0]] = miscfn(item[1]) or item[1]
                    else:
                        pref[item[0]] = fgfn(item[1]) or item[1]
            result.append(pref)
        self.parsed = result
        return self


def color2int(c=None):
    if c is None:
        return c
    elif len(c) == 1:
        c += c
    return int(float.fromhex(c))


def int2color(i=-1):
    if i > -1:
        h = hex(i)
        if i < 16:
            return ''.join(['0', h[2]])
        return ''.join([h[2], h[3]])
    return ''


def adjust_color(mag, dif=0):
    if mag == None:
        return dif
    mag += dif
    if mag < 0:
        return 0
    elif mag > 255:
        return 255
    else:
        return mag


class Color(object):

    """Basic implementation of html color conversions and some basic
    color effects as I've come to understand them (may be flawed)"""
    def __init__(self, str=None):
        super(Color, self).__init__()
        self.src = str
        m = COLOR_REGEX.match(str)
        if m:
            self.red = color2int(m.group('r'))
            self.green = color2int(m.group('g'))
            self.blue = color2int(m.group('b'))
            self.alpha = color2int(m.group('a'))

    def __str__(self):
        s = '#' + int2color(int(self.red)) + int2color(int(self.green)) + int2color(int(self.blue))
        if self.alpha:
            s += int2color(int(self.alpha))
        self.src = s
        return self.src

    # Handles min/max and alpha for adjustments to one or more color channels
    def adjust(self, r=0, g=0, b=0, a=0):
        self.red = adjust_color(self.red, r)
        self.green = adjust_color(self.green, g)
        self.blue = adjust_color(self.blue, b)
        if self.alpha:
            self.alpha = adjust_color(self.alpha, a)
        elif a:
            self.alpha = adjust_color(255, a)
        return self

    # Totally inverts all 3 color channels
    def invert(self):
        print(self.__str__())
        self.red = 255 - self.red
        self.green = 255 - self.green
        self.blue = 255 - self.blue
        print('->' + self.__str__())

        return self

    # Brighten overall color by adding magn to each channel or adding a
    def brighten(self, magn=10):
        if 0 < abs(magn) < 1:  # Treated as ratio of color strength
            self.adjust(self.red*magn, self.green*magn, self.blue*magn)
        else:
            self.adjust(magn, magn, magn)
        return self

    # Simply negates magnitude and applies it brighten
    def darken(self, magn=10):
        brighten(-magn)
        return self


# An automated way of setting a barely opaque background color for each scope settings
# specifying a foreground color and no background or an already `glowing` bg
# magnitude lets you adjust the alpha setting of the bg layer, though 14 works well
def fgbg_glow(pref, magn=14):
    fg = pref.get('foreground', None)
    bg = pref.get('background', None)
    if fg:
        if bg and isinstance(bg, Color):
            if (bg.red == fg.red and bg.green == fg.green and bg.blue == fg.blue):
                bg.alpha = magn
        else:
            bg = Color(fg.__str__())
            bg.alpha = magn
            pref['background'] = bg
    return pref


def adjust_contrast(pref, magn=5, style='light'):
    fg = pref.get('foreground', None)
    bg = pref.get('background', None)
    if style == 'light':
        f, b = -1, 1
    else:
        f, b = 1, -1
    if fg:
        fg.adjust(f*(fg.red/magn), f*(fg.green/magn), f*(fg.blue/magn))
        pref['foreground'] = fg
    if bg:
        bg.adjust(b*(bg.red/magn), b*(bg.green/magn), b*(bg.blue/magn))
        pref['background'] = bg
    return pref


class FgbgGlowCommand(sublime_plugin.ApplicationCommand):

    def run(self):
        cs = ColorScheme().parse_content(fgbg_glow).serialize_parsed()
        cs.save_to_fontofeelya()
        cs.update_settings()


class ContrastDarkCommand(sublime_plugin.ApplicationCommand):

    def run(self, m=5):
        cs = ColorScheme().parse_content(lambda p: adjust_contrast(p, m, 'dark')).serialize_parsed()
        cs.save_to_fontofeelya()
        cs.update_settings()


class ContrastLightCommand(sublime_plugin.ApplicationCommand):

    def run(self, m=5):
        cs = ColorScheme().parse_content(lambda p: adjust_contrast(p, m, 'light')).serialize_parsed()
        cs.save_to_fontofeelya()
        cs.update_settings()


class InvertColorsCommand(sublime_plugin.ApplicationCommand):

    def run(self, m=5):
        cs = ColorScheme().parse_content().map_colors(lambda c: c.invert()).serial_save_update()