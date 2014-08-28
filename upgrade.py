#!/usr/bin/env python

import re
import sys
import os


# missing:
# - navbar

class Element(object):

    def __init__(self, data, start, refpos, startTag="<", endTag=">"):
        self.data = data    
        if self.data[start:start+len(startTag)] != startTag:
            raise Error("Invalid element in data")

        self.tagStart = start
        self.tagEnd = refpos + 1 + data[refpos:].find(endTag)
        
        self.dataPre = self.data[:start]
        self.dataPost = self.data[self.tagEnd:]
        
        self.innerTag = data[start:self.tagEnd]
        m = re.search('^(' + startTag + '\s*)([a-zA-z\-_]+)', self.innerTag, re.DOTALL)
        startTag = m.groups()[0]
        self.tagName = m.groups()[1]
        
        classRe = re.compile('\s+class="(.*?)"', re.DOTALL)
        m = classRe.search(data, start)

        if m is None or m.start() > self.tagEnd:
            self.tplExpr = ""
            self.classes = None
        else:
            origClass = m.groups()[0]
            m = re.search('({%.*%})', origClass, re.DOTALL)
            if m:
                self.tplExpr = m.groups()[0]
                classes = origClass.replace(self.tplExpr, "")
                self.tplExpr = " " + self.tplExpr
            else:
                self.tplExpr = ""
                classes = origClass.strip()
            self.classes = [x for x in re.split("[ ]+", classes) if x != '']

        if self.classes is None:
            self.template = startTag.replace("%", "%%")+"%(tagName)s%(classes)s" + self.innerTag[len(startTag)+len(self.tagName):].replace("%", "%%")
            self.classes = []
            self.spaceAdd = " "
        else:
            self.template = startTag.replace("%", "%%")+"%(tagName)s" + self.innerTag[len(startTag)+len(self.tagName):].replace("%", "%%")
            m = re.search('.*(\s+)class="', self.template)
            self.spaceAdd = m and m.groups()[0] or " "
            self.template = re.sub('\s+class="' + origClass + '"', "%(classes)s", self.template)
        #print "__"+self.tagName, startTag, self.template
        
    def replaceClass(self, a, b):
        self.classes = [b if x == a else x for x in self.classes]
        return self
        
    def removeClass(self, a):
        self.classes = [x for x in self.classes if x != a]
        return self
        
    def addClassAfter(self, a, b):
        if b in self.classes:
            return self
        n = self.classes.index(a)+1
        self.classes = self.classes[0:n] + [b] + self.classes[n:]
        return self

    def addClass(self, a):
        if a in self.classes:
            return self
        self.classes.append(a)
        return self

    def tag(self, t):
        self.tagName = t
        return self
        
    @classmethod
    def fromString(x, orig, pattern, offset=0):
        data = orig[offset:]
        m = re.search(pattern, data, re.DOTALL)
        if not m:
            return None
        startPos = m.start(1)
        # now search left until start of tag    
        tagStart = data[:startPos].rfind("<")
        tplTagStart = data[:startPos].rfind("{%")
        if tagStart == -1 and tplTagStart == -1:
            return None
        if tagStart == -1 or tagStart < tplTagStart:
            tagStart = tplTagStart
            startTag = "{%"
            endTag = "%}"
        else:
            startTag = "<"
            endTag = ">"
        e = Element(orig, offset+tagStart, offset+startPos, startTag, endTag)
        e.patternGroups = m.groups()    
        return e

    def output(self):
        if self.classes is None or not(len(self.classes)):
            classes=""
        else:
            classes=self.spaceAdd + "class=\"%s\"" % (" ".join(self.classes) + self.tplExpr)
        d = {'tagName': self.tagName, 'classes': classes}
        elem = (self.template % d)
        return self.tagStart, self.tagStart + len(elem), self.dataPre + elem + self.dataPost
        
def transformGrid(e):
    e.replaceClass("container-fluid", "container")
    e.replaceClass("row-fluid", "row")

    prefix = None
    for c in e.classes:
        if c[:4] == "span":
            prefix = c[4:]
    if prefix:
        e.removeClass("span"+prefix)
        e.classes += ["col-lg-" + prefix, "col-md-" + prefix]

def transformForms(e):
    e.replaceClass("form-search", "form-inline")
    e.removeClass("input-block-level")
    e.replaceClass("help-inline", "help-block")
    e.replaceClass("control-group", "form-group")
    e.removeClass("controls")
    if "inline" in e.classes and "radio" in e.classes:
        e.removeClass("radio")
        e.removeClass("inline")
        e.classes.append("radio-inline")
    if "inline" in e.classes and "checkbox" in e.classes:
        e.removeClass("checkbox")
        e.removeClass("inline")
        e.classes.append("checkbox-inline")
        
    sizes = {'mini': '2', 'small': '4', 'medium': '6', 'large': '8'}
    for old, new in sizes.iteritems():
        cls = "input-" + old
        if cls in e.classes:
            e.removeClass(cls).addClass("col-md-" + new)
        

def transformNavbar(e):
    orig = e.classes[:]
    # Replace .navbar-search with .navbar-form
    e.replaceClass("navbar-search", "navbar-form")
    # Replace .navbar-inner with .container
    e.replaceClass("navbar-inner", "container")

    if "nav-header" in orig and e.tagName == "li":
        e.classes = ["dropdown-header"]
        
    if "dropdown-menu" in orig:
        e.classes = ["dropdown-menu"]

    # Replace .navbar .nav with .navbar-nav
    if "nav" in orig and Element.fromString(e.dataPre, ".*(navbar)[^<]*") is not None:
        e.removeClass("navbar")
        e.addClass("navbar-nav")

    # .brand is now .navbar-brand
    e.replaceClass("brand", "navbar-brand")

    # .navbar. pull-left is now .navbar-left
    # if "pull-left" in orig and e.parentContainsClass(":
    #     e.removeClass("pull-left")
    #     e.removeClass("navbar")
    #     e.classes.append("navbar-left")
        
    # # .navbar.pull-right is now .navbar-right
    # if "navbar" in orig and "pull-right" in orig:
    #     e.removeClass("pull-right")
    #     e.removeClass("navbar")
    #     e.classes.append("navbar-right")

    # .nav-collapse is now .navbar-collapse
    e.replaceClass("nav-collapse", "navbar-collapse")
    e.replaceClass("nav-toggle", "navbar-toggle")
    e.replaceClass("btn-navbar", "navbar-btn")
    
    # FIXME .navbar-brand, .navbar-toggle are wrapped by .navbar-header
    # FIXME .navbar:not(.navbar-inverse) is now .navbar.navbar-default

    
def transformButtons(e):
    # Add btn-default to btn elements with no other color.
    colors = "primary,success,info,warning,danger,link".split(",")
    if "btn" in e.classes:
        hasColor = False
        for c in e.classes:
            if c[:4] == "btn-" and c[4:] in colors:
                hasColor = True
                break
        if not hasColor:
            e.addClassAfter("btn", "btn-default")
    
    # Replace btn-inverse with btn-default since inverse has been removed from Bootstrap 3.
    e.replaceClass("btn-inverse", "btn-default")

    # upgrade sizes
    types = ['btn', 'pagination', 'well'];
    sizes = {'mini': 'xs', 'small': 'sm', 'large': 'lg'}
    for t in types:
        for old,new in sizes.iteritems():
            e.replaceClass(t + "-" + old, t + "-" + new)


def transformIcons(e):
    e.removeClass("icon-white")
    icon = None
    for c in e.classes:
        if c[:5] == "icon-":
            icon = c
            break
    if icon:
        e.replaceClass(icon, "glyphicon")                
        e.addClassAfter("glyphicon", "glyph"+icon)


def transformMisc(e):
    e.replaceClass("hero-unit", "jumbotron")
    e.replaceClass("alert-error", "alert-danger")
    e.replaceClass("muted", "text-muted")
    if e.tagName == "ul":
        e.replaceClass("unstyled", "list-unstyled")
        e.replaceClass("inline", "list-inline")

    if "label" in e.classes:
        found = False
        for c in e.classes:
            if c[:6] == "label-":
                found = True
        if not(found):
            e.addClass("label-default")
    e.replaceClass("label-important", "label-danger")

    e.replaceClass("img-polariod", "img-thumbnail")
    
    e.replaceClass("accordion", "panel-group")
    e.replaceClass("accordion-group", "panel-default")
    e.replaceClass("accordion-heading", "panel-heading")
    e.replaceClass("accordion-body", "panel-collapse")
    e.replaceClass("accordion-inner", "panel-body")

    e.replaceClass("bar", "progress-bar")
    for c in e.classes:
        if c[:4] == "bar-":
            e.replaceClass(c, "progress-" + c)

    e.replaceClass("pill-content", "tab-content")
    e.replaceClass("pill-pane", "tab-pane")
    
    
transformers = [transformGrid, transformForms, transformNavbar, transformButtons, transformIcons, transformMisc]

def upgrade(data):
    cursor = 0
    while True:
        e = Element.fromString(data, ".*?(class=)", cursor)
        if e is None:
            break
        for f in transformers:
            f(e)
        (start, cursor, data) = e.output()
#    return data
    # Add form-control to every input
    cursor = 0
    while True:
        e = Element.fromString(data, ".*?<(input|textarea|select)", cursor)
        if e is None:
            break
        #  Add form-control class to inputs and selects
        if 'type="radio"' not in e.innerTag and 'type="checkbox"' not in e.innerTag and 'type="hidden"' not in e.innerTag:
            e.addClass("form-control")
        (start, cursor, data) = e.output()

    # process radio and checkboxes
    cursor = 0
    while True:
        e = Element.fromString(data, ".*?<(input)[^<>]*?type=\"(radio|checkbox)", cursor)
        if e is None:
            break

        # find first label
        labelElem = Element.fromString(e.dataPre, ".*<(label)")
        if labelElem is None or "checkbox-inline" in labelElem.classes or "radio-inline" in labelElem.classes or re.match(".*</label", labelElem.dataPost):
            cursor = e.tagEnd
            continue

        tpe = e.patternGroups[1]
        labelElem.removeClass(tpe)
        # try to find a stray <div> before the label
        divElem = Element.fromString(labelElem.dataPre, ".*<(div)>[^<]*$")

        if divElem is None:
            labelElem.dataPre += "<div class=\"%s\">" % tpe
            (_, _, e.dataPre) = labelElem.output()
            e.dataPost = e.dataPost.replace("</label>", "</label></div>", 1)
        else:
            divElem.addClass(tpe)
            (_, _, labelElem.dataPre) = divElem.output()
            (_, _, e.dataPre) = labelElem.output()
            
        (start, cursor, data) = e.output()
        
    return data
        
if __name__ == "__main__":
    print upgrade(sys.stdin.read()),
    #print upgrade('<input class="">')
    #print Element.fromString("dd <input type=\"text\" class=\"{% if foo %}dd{% endif %} y\"> foo bar class=\"d\"", ".*?(type=)").addClass("bar").output()
    #print Element.fromString("dd <input type=\"text\"> foo bar class=\"d\"", ".*?(type=)").tag("foo").addClass("foo").output()
