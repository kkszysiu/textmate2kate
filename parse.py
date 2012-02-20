#!/usr/bin/env python
"""
Copyright (C) 2012 Krzysztof "kkszysiu" Klinikowski <kkszysiu@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import sys
import shutil
import time
import re
import subprocess
import plistlib
import xml.etree.ElementTree as ET

"""

[kate - Normal]
Color Background=255,255,255
Color Highlighted Bracket=237,249,255
Color Highlighted Line=248,247,246
Color Icon Bar=213,209,207
Color Line Number=27,25,24
Color MarkType1=0,0,255
Color MarkType2=255,0,0
Color MarkType3=255,255,0
Color MarkType4=255,0,255
Color MarkType5=160,160,164
Color MarkType6=0,255,0
Color MarkType7=255,0,0
Color Selection=67,172,232
Color Spelling Mistake Line=255,0,0
Color Tab Marker=210,210,210
Color Template Background=204,204,204
Color Template Editable Placeholder=204,255,204
Color Template Focused Editable Placeholder=102,255,102
Color Template Not Editable Placeholder=255,204,204
Color Word Wrap Marker=237,237,237
Font=Monospace,9,-1,5,50,0,0,0,0,0


[Default Item Styles - Schema darK]
Alert=ffbf0303,ff9c0e0e,1,,,,fff7e6e6,,,---
Base-N Integer=ffb08000,ffffdd00,,,,,,,,---
Character=ffff80e0,ffff80e0,,,,,,,,---
Comment=ff898887,ffa5c1e4,,1,,,,,,---
Data Type=ff0057ae,ff00316e,,,,,,,,---
Decimal/Value=ffb08000,ffffdd00,,,,,,,,---
Error=ffbf0303,ff9c0e0e,,,,,,,,---
Floating Point=ffb08000,ffffdd00,,,,,,,,---
Function=ff644a9b,ff452886,,,,,,,,---
Keyword=ff181615,ffffffff,1,,,,,,,---
Normal=ff181615,ffffffff,,,,,,,,---
Others=ff006e28,ff80ff80,,,,,,,,---
Region Marker=ff0057ae,ff00316e,,,,,ffe0e9f8,,,---
String=ffbf0303,ff9c0e0e,,,,,,,,---


{'uuid': 'D8D5E82E-3D5B-46B5-B38E-8C841C21347D', 'name': 'Monokai', 'settings': [{'settings': {'caret': '#F8F8F0', 'foreground': '#F8F8F2', 'selection': '#49483E', 'invisibles': '#49483E', 'lineHighlight': '#49483E', 'background': '#272822'}}, {'scope': 'comment', 'name': 'Comment', 'settings': {'foreground': '#75715E'}}, {'scope': 'string', 'name': 'String', 'settings': {'foreground': '#E6DB74'}}, {'scope': 'constant.numeric', 'name': 'Number', 'settings': {'foreground': '#AE81FF'}}, {'scope': 'constant.language', 'name': 'Built-in constant', 'settings': {'foreground': '#AE81FF'}}, {'scope': 'constant.character, constant.other', 'name': 'User-defined constant', 'settings': {'foreground': '#AE81FF'}}, {'scope': 'variable', 'name': 'Variable', 'settings': {'fontStyle': ''}}, {'scope': 'keyword', 'name': 'Keyword', 'settings': {'foreground': '#F92672'}}, {'scope': 'storage', 'name': 'Storage', 'settings': {'foreground': '#F92672', 'fontStyle': ''}}, {'scope': 'storage.type', 'name': 'Storage type', 'settings':
{'foreground': '#66D9EF', 'fontStyle': 'italic'}}, {'scope': 'entity.name.class', 'name': 'Class name', 'settings': {'foreground': '#A6E22E', 'fontStyle': 'underline'}}, {'scope': 'entity.other.inherited-class', 'name': 'Inherited class', 'settings': {'foreground': '#A6E22E', 'fontStyle': 'italic underline'}}, {'scope': 'entity.name.function', 'name': 'Function name', 'settings': {'foreground': '#A6E22E', 'fontStyle': ''}}, {'scope': 'variable.parameter', 'name': 'Function argument', 'settings': {'foreground': '#FD971F', 'fontStyle': 'italic'}}, {'scope': 'entity.name.tag', 'name': 'Tag name', 'settings': {'foreground': '#F92672', 'fontStyle': ''}}, {'scope': 'entity.other.attribute-name', 'name': 'Tag attribute', 'settings': {'foreground': '#A6E22E', 'fontStyle': ''}}, {'scope': 'support.function', 'name': 'Library function', 'settings': {'foreground': '#66D9EF', 'fontStyle': ''}}, {'scope': 'support.constant', 'name': 'Library constant', 'settings': {'foreground': '#66D9EF', 'fontStyle': ''}}, {'scope': '
support.type, support.class', 'name': 'Library class/type', 'settings': {'foreground': '#66D9EF', 'fontStyle': 'italic'}}, {'scope': 'support.other.variable', 'name': 'Library variable', 'settings': {'fontStyle': ''}}, {'scope': 'invalid', 'name': 'Invalid', 'settings': {'foreground': '#F8F8F0', 'fontStyle': '', 'background': '#F92672'}}, {'scope': 'invalid.deprecated', 'name': 'Invalid deprecated', 'settings': {'foreground': '#F8F8F0', 'background': '#AE81FF'}}]}

"""

useThemeBarColors = True


class TexmateToKateShemaGenerator(object):
    def __init__(self):
        self.schemaname = ""
        self.syntaxhighlightingrc = ""
        self.schemarc = ""
        self.output = ""
        self.output2 = ""

    def HTMLColorToRGB(self, colorstring):
        """ convert #RRGGBB to an (R, G, B) tuple """
        colorstring = colorstring.strip()
        if colorstring[0] == '#': colorstring = colorstring[1:]
        if len(colorstring) != 6:
            raise ValueError, "input #%s is not in #RRGGBB format" % colorstring
        r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
        r, g, b = [int(n, 16) for n in (r, g, b)]
        return (r, g, b)

    def convert(self, infile):
        data = plistlib.readPlist(infile)
        #print data
        # here we should have correct data :)
        # now we need to parse it to Kate/KDevelop sheme styles
        #print "Shema name: ", themename
        if "name" in data:
            shemaname = data["name"]
        else:
            shemaname = data["uuid"]
        print "Shema name: ", shemaname
        self.schemaname = shemaname
        self.output += "[%s]\n" % (shemaname)
        self.output2 += "[Default Item Styles - Schema %s]\n" % (shemaname)

        if "settings" in data:
            for elem in data["settings"]:
                if not "name" in elem and "settings" in elem:
                    #print elem["settings"]
                    if "foreground" in elem["settings"]:
                        bg = elem["settings"]["foreground"]
                        self.output2 += "Normal=ff%s,ffffffff,,,,,,,,---\n" % (bg.lower()[1:])
                        #self.output += "Color Background=%s,%s,%s\n" % bgcolor

                    if "background" in elem["settings"]:
                        bg = elem["settings"]["background"]
                        bgcolor = self.HTMLColorToRGB(bg)
                        self.output += "Color Background=%s,%s,%s\n" % bgcolor

                        if useThemeBarColors:
                             self.output += "Color Icon Bar=%s,%s,%s\n" % bgcolor
                    if "caret" in elem["settings"]:
                        pass
                    if "lineHighlight" in elem["settings"]:
                        lh = elem["settings"]["lineHighlight"]
                        lhcolor = self.HTMLColorToRGB(lh)
                        self.output += "Color Highlighted Line=%s,%s,%s\n" % lhcolor

                        if useThemeBarColors:
                            self.output += "Color Line Number=%s,%s,%s\n" % lhcolor
                    if "selection" in elem["settings"]:
                        cs = elem["settings"]["lineHighlight"]
                        cscolor = self.HTMLColorToRGB(cs)
                        self.output += "Color Selection=%s,%s,%s\n" % cscolor
                    #Color Highlighted Bracket=237,249,255
                else:
                    implementedScopeParsers = {
                        "string": "String",
                        "comment": "Comment",
                        "keyword": "Keyword",
                        "constant.numeric": "Decimal/Value",
                        "invalid": "Alert",
                        "constant.character": "Character",
                        "entity.name.function": "Function",
                        "storage.type": "Data Type",
                        "entity.name.class": "Others"
                    }

                    if "scope" in elem and elem["scope"] in implementedScopeParsers:
                        kdata = ""
                        scope = elem["scope"]
                        settings = elem["settings"]
                        kdata += "%s=" % (implementedScopeParsers[scope])
                        if "foreground" in settings:
                            bg = settings["foreground"]
                            katecolor = "ff%s" % (bg.lower()[1:])
                        kdata += "%s,%s,,,,,-,-,---" % (katecolor, katecolor)
                        self.output2 += kdata
                        self.output2 += "\n"
                        #String=ffff6f00,ffff0000,,,,,-,-,---
                    elif "scope" in elem:
                        print "Scope not implemented: %s, src: %s" % (elem["scope"], elem)
                    else:
                        print "What to do with? Seems unsupported at all!:", elem
        self.output += "Font=Ubuntu Mono,9,-1,5,50,0,0,0,0,0\n"
        self.output += "\n"
        self.output2 += "\n"

    def getLocalPrefix(self):
        #try:
        cmd_output = subprocess.Popen(["kde4-config", "--localprefix"], shell=False, stdout=subprocess.PIPE).communicate()
        return cmd_output[0].replace("\n", "");
        #except:
        #    pass

    def backupFiles(self, kateschemarc, katesyntaxhighlightingrc):
        shutil.copyfile(kateschemarc, "kateschemarc.backup.%i" % (time.time()))
        shutil.copyfile(katesyntaxhighlightingrc, "katesyntaxhighlightingrc.backup.%i" % (time.time()))

    def checkIsThemeExists(self, kateschemarc, katesyntaxhighlightingrc):
        """ This method check is schema added already and if it was, then remove it from files """

        ##  kateschemarc
        f = open(kateschemarc, "rb")
        fdata = f.read()
        f.close()

        # check if rules for this theme already exists in config and if yes, override it :)
        prog = re.compile(r"\[%s\]\n(.*[^[(.*)\]]+)" % (self.schemaname), re.MULTILINE)

        match = prog.search(fdata)
        if match:
            result = match.group()

            newfdata = fdata.replace(result, "")
            f = open(kateschemarc, "wb")
            f.write(newfdata)
            f.close()

        ##  katesyntaxhighlightingrc
        f = open(katesyntaxhighlightingrc, "rb")
        fdata = f.read()
        f.close()

        # check if rules for this theme already exists in config and if yes, override it :)
        prog = re.compile(r"\[Default Item Styles - Schema %s\]\n(.*[^[(.*)\]]+)" % (self.schemaname), re.MULTILINE)

        match = prog.search(fdata)
        if match:
            result = match.group()

            newfdata = fdata.replace(result, "")
            f = open(katesyntaxhighlightingrc, "wb")
            f.write(newfdata)
            f.close()

    def updateFiles(self):
        f = open(self.schemarc, "ab")
        f.write(self.output)
        f.close()

        f = open(self.syntaxhighlightingrc, "ab")
        f.write(self.output2)
        f.close()

    def installScheme(self):
        localprefix = self.getLocalPrefix()
        print localprefix
        katesyntaxhighlightingrc = "%s/share/config/katesyntaxhighlightingrc" % (localprefix)
        kateschemarc = "%s/share/config/kateschemarc" % (localprefix)
        self.syntaxhighlightingrc = katesyntaxhighlightingrc
        self.schemarc = kateschemarc
        self.backupFiles(kateschemarc, katesyntaxhighlightingrc)
        self.checkIsThemeExists(kateschemarc, katesyntaxhighlightingrc)
        self.updateFiles()

    def getOutput(self):
        print self.output
        print "\n"
        print self.output2
        print "\n"
        return self.output

def usage(msg):
    print "Script failed, message:\n%s\n\nHelp: python %s /path/to/schema.xml" % (msg, __file__)

def main(argv):
    try:
        if argv[0]:
            data = plistlib.readPlist(argv[0])
            if data == None:
                raise Exception, "Argument is not a valid schema file."
            else:
                gen = TexmateToKateShemaGenerator()
                gen.convert(argv[0])
                gen.getOutput()
                gen.installScheme()
        else:
            raise Exception, "Argument not provided."
    except Exception, e:
        usage(e)
        sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])

"""
pos1 = fdata.find(tname)
if pos1 != 0:
pos2 = fdata.find("[", pos1 + len(tname))

newbody = fdata[:pos1]+fdata[pos2:]
if pos2 != 0 and len(newbody) != 0:
print "newbody:\n", newbody
f.write(newbody)
f.close()

##  katesyntaxhighlightingrc

f = open(katesyntaxhighlightingrc, "rb")
fdata = f.read()
f.close()

f = open(katesyntaxhighlightingrc, "wb")
tname = "[Default Item Styles - Schema %s]" % (self.schemaname)

# check if rules for this theme already exists in config and if yes, override it :)
pos1 = fdata.find(tname)
if pos1 != 0:
pos2 = fdata.find("\n\n", pos1 + len(tname))

newbody = fdata[:pos1]+fdata[pos2:]
if pos2 != 0 and len(newbody) != 0:
print "newbody2:\n", newbody
f.write(newbody)
f.close()
"""
