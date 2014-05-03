# -*- coding: utf-8 -*-

from qwt.qt.QtGui import QPainterPath, QPaintEngine


class PixmapData(object):
    def __init__(self):
        self.rect = None
        self.pixmap = None
        self.subRect = None

class ImageData(object):
    def __init__(self):
        self.rect = None
        self.image = None
        self.subRect = None
        self.flags = None

class StateData(object):
    def __init__(self):
        self.flags = None
        self.pen = None
        self.brush = None
        self.brushOrigin = None
        self.backgroundBrush = None
        self.backgroundMode = None
        self.font = None
        self.matrix = None
        self.transform = None
        self.clipOperation = None
        self.clipRegion = None
        self.clipPath = None
        self.isClipEnabled = None
        self.renderHints = None
        self.compositionMode = None
        self.opacity = None

class QwtPainterCommand(object):
    
    # enum Type
    Invalid = -1
    Path, Pixmap, Image, State = range(4)
    
    def __init__(self, *args):
        if len(args) == 0:
            self.d_type = self.Invalid
        elif len(args) == 1:
            arg, = args
            if isinstance(arg, QPainterPath):
                path = arg
                self.d_type = self.Path
                self.d_path = QPainterPath(path)
            elif isinstance(arg, QwtPainterCommand):
                other = arg
                self.copy(other)
            else:
                state = arg
                self.d_type = self.State
                self.d_stateData = StateData()
                self.d_stateData.flags = state.state()
                if self.d_stateData.flags & QPaintEngine.DirtyPen:
                    self.d_stateData.pen = state.pen()
                if self.d_stateData.flags & QPaintEngine.DirtyBrush:
                    self.d_stateData.brush = state.brush()
                if self.d_stateData.flags & QPaintEngine.DirtyBrushOrigin:
                    self.d_stateData.brushOrigin = state.brushOrigin()
                if self.d_stateData.flags & QPaintEngine.DirtyFont:
                    self.d_stateData.font = state.font()
                if self.d_stateData.flags & QPaintEngine.DirtyBackground:
                    self.d_stateData.backgroundMode = state.backgroundMode()
                    self.d_stateData.backgroundBrush = state.backgroundBrush()
                if self.d_stateData.flags & QPaintEngine.DirtyTransform:
                    self.d_stateData.transform = state.transform()
                if self.d_stateData.flags & QPaintEngine.DirtyClipEnabled:
                    self.d_stateData.isClipEnabled = state.isClipEnabled()
                if self.d_stateData.flags & QPaintEngine.DirtyClipRegion:
                    self.d_stateData.clipRegion = state.clipRegion()
                    self.d_stateData.clipOperation = state.clipOperation()
                if self.d_stateData.flags & QPaintEngine.DirtyClipPath:
                    self.d_stateData.clipPath = state.clipPath()
                    self.d_stateData.clipOperation = state.clipOperation()
                if self.d_stateData.flags & QPaintEngine.DirtyHints:
                    self.d_stateData.renderHints = state.renderHints()
                if self.d_stateData.flags & QPaintEngine.DirtyCompositionMode:
                    self.d_stateData.compositionMode = state.compositionMode()
                if self.d_stateData.flags & QPaintEngine.DirtyOpacity:
                    self.d_stateData.opacity = state.opacity()
        elif len(args) == 3:
            rect, pixmap, subRect = args
            self.d_type = self.Pixmap
            self.d_pixmapData = PixmapData()
            self.d_pixmapData.rect = rect
            self.d_pixmapData.pixmap = pixmap
            self.d_pixmapData.subRect = subRect
        elif len(args) == 4:
            rect, image, subRect, flags = args
            self.d_type = self.Image
            self.d_imageData = ImageData()
            self.d_imageData.rect = rect
            self.d_imageData.image = image
            self.d_imageData.subRect = subRect
            self.d_imageData.flags = flags
        else:
            raise TypeError("%s() takes 0, 1, 3 or 4 argument(s) (%s given)"\
                            % (self.__class__.__name__, len(args)))
    
    def copy(self, other):
        self.d_type = other.d_type
        if other.d_type == self.Path:
            self.d_path = QPainterPath(other.d_path)
        elif other.d_type == self.Pixmap:
            self.d_pixmapData = PixmapData(other.d_pixmapData)
        elif other.d_type == self.Image:
            self.d_imageData = ImageData(other.d_imageData)
        elif other.d_type == self.State:
            self.d_stateData == StateData(other.d_stateData)
    
    def reset(self):
        self.d_type = self.Invalid
    
    def path(self):
        return self.d_path
    
    def pixmapData(self):
        return self.d_pixmapData
    
    def imageData(self):
        return self.d_imageData
    
    def stateData(self):
        return self.d_stateData
