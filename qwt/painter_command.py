# -*- coding: utf-8 -*-
#
# Licensed under the terms of the Qwt License
# Copyright (c) 2002 Uwe Rathmann, for the original C++ code
# Copyright (c) 2015 Pierre Raybaut, for the Python translation/optimization
# (see LICENSE file for more details)

"""
QwtPainterCommand
-----------------

.. autoclass:: QwtPainterCommand
   :members:
"""

import copy

from qtpy.QtGui import QPaintEngine, QPainterPath


def _flag_int(flag):
    """Return the integer value of a Qt enum/flag (PyQt5 and PyQt6).

    PyQt5 exposes Qt enums as plain ints (``int(flag)`` works). PyQt6 wraps
    them as ``enum.Flag`` instances which are not ``int`` subclasses, so
    ``int(flag)`` raises -- the value must be read from ``flag.value``.
    """
    try:
        return flag.value
    except AttributeError:
        return int(flag)


# Cache QPaintEngine.DirtyXxx flags as plain Python ints once at import time.
# On PyQt6, Qt enums are full ``enum.Flag`` instances and every ``flags &
# Member`` test goes through Python's ``enum.__and__`` machinery (~6 us each).
# In ``QwtPainterCommand.__init__`` below, the State branch performs twelve
# successive flag tests per painter command -- on PyQt6 alone this accounted
# for ~20 ms of the residual perf gap on the load test. Casting once to int
# and bitwise-testing against int constants brings each test back to ~50 ns.
_DIRTY_PEN = _flag_int(QPaintEngine.DirtyPen)
_DIRTY_BRUSH = _flag_int(QPaintEngine.DirtyBrush)
_DIRTY_BRUSH_ORIGIN = _flag_int(QPaintEngine.DirtyBrushOrigin)
_DIRTY_FONT = _flag_int(QPaintEngine.DirtyFont)
_DIRTY_BACKGROUND = _flag_int(QPaintEngine.DirtyBackground)
_DIRTY_TRANSFORM = _flag_int(QPaintEngine.DirtyTransform)
_DIRTY_CLIP_ENABLED = _flag_int(QPaintEngine.DirtyClipEnabled)
_DIRTY_CLIP_REGION = _flag_int(QPaintEngine.DirtyClipRegion)
_DIRTY_CLIP_PATH = _flag_int(QPaintEngine.DirtyClipPath)
_DIRTY_HINTS = _flag_int(QPaintEngine.DirtyHints)
_DIRTY_COMPOSITION_MODE = _flag_int(QPaintEngine.DirtyCompositionMode)
_DIRTY_OPACITY = _flag_int(QPaintEngine.DirtyOpacity)


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
    """
    `QwtPainterCommand` represents the attributes of a paint operation
    how it is used between `QPainter` and `QPaintDevice`

    It is used by :py:class:`qwt.graphic.QwtGraphic` to record and replay
    paint operations

    .. seealso::

        :py:meth:`qwt.graphic.QwtGraphic.commands()`


    .. py:class:: QwtPainterCommand()

        Construct an invalid command

    .. py:class:: QwtPainterCommand(path)
        :noindex:

        Copy constructor

        :param QPainterPath path: Source

    .. py:class:: QwtPainterCommand(rect, pixmap, subRect)
        :noindex:

        Constructor for Pixmap paint operation

        :param QRectF rect: Target rectangle
        :param QPixmap pixmap: Pixmap
        :param QRectF subRect: Rectangle inside the pixmap

    .. py:class:: QwtPainterCommand(rect, image, subRect, flags)
        :noindex:

        Constructor for Image paint operation

        :param QRectF rect: Target rectangle
        :param QImage image: Image
        :param QRectF subRect: Rectangle inside the image
        :param Qt.ImageConversionFlags flags: Conversion flags

    .. py:class:: QwtPainterCommand(state)
        :noindex:

        Constructor for State paint operation

        :param QPaintEngineState state: Paint engine state
    """

    # enum Type
    Invalid = -1
    Path, Pixmap, Image, State = list(range(4))

    def __init__(self, *args):
        if len(args) == 0:
            self.__type = self.Invalid
        elif len(args) == 1:
            (arg,) = args
            if isinstance(arg, QPainterPath):
                path = arg
                self.__type = self.Path
                self.__path = QPainterPath(path)
            elif isinstance(arg, QwtPainterCommand):
                other = arg
                self.copy(other)
            else:
                state = arg
                self.__type = self.State
                self.__stateData = StateData()
                self.__stateData.flags = state.state()
                # Cast to int once: subsequent bitwise tests are done against
                # the cached _DIRTY_* int constants (see top of module).
                flags = _flag_int(self.__stateData.flags)
                if flags & _DIRTY_PEN:
                    self.__stateData.pen = state.pen()
                if flags & _DIRTY_BRUSH:
                    self.__stateData.brush = state.brush()
                if flags & _DIRTY_BRUSH_ORIGIN:
                    self.__stateData.brushOrigin = state.brushOrigin()
                if flags & _DIRTY_FONT:
                    self.__stateData.font = state.font()
                if flags & _DIRTY_BACKGROUND:
                    self.__stateData.backgroundMode = state.backgroundMode()
                    self.__stateData.backgroundBrush = state.backgroundBrush()
                if flags & _DIRTY_TRANSFORM:
                    self.__stateData.transform = state.transform()
                if flags & _DIRTY_CLIP_ENABLED:
                    self.__stateData.isClipEnabled = state.isClipEnabled()
                if flags & _DIRTY_CLIP_REGION:
                    self.__stateData.clipRegion = state.clipRegion()
                    self.__stateData.clipOperation = state.clipOperation()
                if flags & _DIRTY_CLIP_PATH:
                    self.__stateData.clipPath = state.clipPath()
                    self.__stateData.clipOperation = state.clipOperation()
                if flags & _DIRTY_HINTS:
                    self.__stateData.renderHints = state.renderHints()
                if flags & _DIRTY_COMPOSITION_MODE:
                    self.__stateData.compositionMode = state.compositionMode()
                if flags & _DIRTY_OPACITY:
                    self.__stateData.opacity = state.opacity()
        elif len(args) == 3:
            rect, pixmap, subRect = args
            self.__type = self.Pixmap
            self.__pixmapData = PixmapData()
            self.__pixmapData.rect = rect
            self.__pixmapData.pixmap = pixmap
            self.__pixmapData.subRect = subRect
        elif len(args) == 4:
            rect, image, subRect, flags = args
            self.__type = self.Image
            self.__imageData = ImageData()
            self.__imageData.rect = rect
            self.__imageData.image = image
            self.__imageData.subRect = subRect
            self.__imageData.flags = flags
        else:
            raise TypeError(
                "%s() takes 0, 1, 3 or 4 argument(s) (%s given)"
                % (self.__class__.__name__, len(args))
            )

    def copy(self, other):
        self.__type = other.__type
        if other.__type == self.Path:
            self.__path = QPainterPath(other.__path)
        elif other.__type == self.Pixmap:
            self.__pixmapData = copy.deepcopy(other.__pixmapData)
        elif other.__type == self.Image:
            self.__imageData = copy.deepcopy(other.__imageData)
        elif other.__type == self.State:
            self.__stateData == copy.deepcopy(other.__stateData)

    def reset(self):
        self.__type = self.Invalid

    def type(self):
        return self.__type

    def path(self):
        return self.__path

    def pixmapData(self):
        return self.__pixmapData

    def imageData(self):
        return self.__imageData

    def stateData(self):
        return self.__stateData
