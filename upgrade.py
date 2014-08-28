#!/usr/bin/env python

import re
import sys
import os

class Element(object):

    def __init__(self, tag, classes):
        self.tag = tag
        self.classes = classes

    def replaceClass(self, a, b):
        self.classes = [b if x == a else x for x in self.classes]

    def removeClass(self, a):
        self.classes = [x for x in self.classes if x != a]

    def addClassAfter(self, a, b):
        n = self.classes.index(a)+1
        self.classes = self.classes[0:n] + [b] + self.classes[n:]

        
def transformGrid(e):
    e.removeClass("container-fluid")
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
        
    #  Add form-control class to inputs and selects
    if e.tag == "input":
        e.classes.append("form-control")

    # Add column widths to horizontal form labels and .controls
        

def transformNavbar(e):
    orig = e.classes[:]
    # Replace .navbar-search with .navbar-form
    e.replaceClass("navbar-search", "navbar-form")
    # Replace .navbar-inner with .container
    e.replaceClass("navbar-inner", "container")

    # Replace .navbar .nav with .navbar-nav
    if "navbar" in orig and "nav" in orig:
        e.removeClass("nav")
        e.removeClass("navbar")
        e.classes.append("navbar-nav")

    # .brand is now .navbar-brand
    e.replaceClass("brand", "navbar-brand")

    # .navbar.pull-left is now .navbar-left
    if "navbar" in orig and "pull-left" in orig:
        e.removeClass("pull-left")
        e.removeClass("navbar")
        e.classes.append("navbar-left")
        
    # .navbar.pull-right is now .navbar-right
    if "navbar" in orig and "pull-right" in orig:
        e.removeClass("pull-right")
        e.removeClass("navbar")
        e.classes.append("navbar-right")

    # .nav-collapse is now .navbar-collapse
    e.replaceClass("nav-collapse", "navbar-collapse")

    # FIXME .navbar-brand, .navbar-toggle are wrapped by .navbar-header
    # FIXME .navbar:not(.navbar-inverse) is now .navbar.navbar-default

    
def transformButtons(e):
    # Add btn-default to btn elements with no other color.
    if "btn" in e.classes:
        hasColor = False
        for c in e.classes:
            if c[:4] == "btn-":
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


def transformIcons(classes):
    e.removeClass("icon-white")
    icon = None
    for c in e.classes:
        if c[:5] == "icon-":
            icon = c
            break
    if icon:
        e.replaceClass(icon, "glyphicon")                
        e.addClassAfter("glyphicon", "glyph"+icon)

transformers = [transformGrid, transformForms, transformNavbar, transformButtons, transformIcons]

for line in sys.stdin.readlines():
    if line[-1] == "\n":
        line = line[:-1]
        
    m = re.search(' class\=\"(.*?)\"', line)
    if not m:
        print line
        continue
    origClass = m.groups()[0]
    m = re.search('({%.*%})', origClass)
    if m:
        tplExpr = m.groups()[0]
        classes = origClass.replace(tplExpr, "")
    else:
        tplExpr = ""
        classes = origClass.strip()
    classes = re.split("[ ]+", classes)
    if classes == ['']:
        print line
        continue

    part = line[:line.find("class=")]
    part = part[part.rfind("<")+1:]
    tag = part[:part.find(" ")]
    
    e = Element(tag, classes)
    for f in transformers:
        f(e)
    newClass = (" ".join(e.classes) + " " + tplExpr).strip()
    line = line.replace(origClass, newClass)
    line = line.replace(" class=\"\"", "")
    print line







