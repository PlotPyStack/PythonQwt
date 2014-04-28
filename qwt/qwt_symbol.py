# -*- coding: utf-8 -*-


class QwtSymbol(object):
    
    # enum Style
    NoSymbol = -1
    (Ellipse, Rect, Diamond, Triangle, DTriangle, UTriangle, LTriangle,
     RTriangle, Cross, XCross, HLine, VLine, Star1, Star2, Hexagon, Path,
     Pixmap, Graphic, SvgDocument) = range(19)
    UserStyle = 1000
    
    # enum CachePolicy
    NoCache, Cache, AutoCache = range(3)
    