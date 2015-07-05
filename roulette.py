#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2015 SeukWon Kang (kasworld@gmail.com)
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import sys
import os.path
import time
import math
import wx
from time import strftime, localtime
import random

wx.InitAllImageHandlers()


class roulette(wx.PyWindow):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_BORDER, name="Roulette"):
        wx.PyWindow.__init__(self, parent, id, pos, size, style, name)

        # Set event handlers.
        self.Bind(wx.EVT_SIZE, self._OnSize)
        self.Bind(wx.EVT_PAINT, self._OnPaint)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda evt: None)
        self.Bind(wx.EVT_TIMER, self._OnTimer)
        self.Bind(wx.EVT_WINDOW_DESTROY, self._OnDestroyWindow)
        self.Bind(wx.EVT_CONTEXT_MENU, lambda evt: None)
        self.Bind(wx.EVT_KEY_UP, self._OnRoll)
        self.Bind(wx.EVT_LEFT_UP, self._OnRoll)
        self.stopdelay = [int(1.1 ** a) for a in range(60)]
        self.timer = wx.Timer(self)
        self._OnSize(None)
        self.timer.Start(10, True)

    def _OnSize(self, evt):
        size = self.GetClientSize()
        if size.x < 1 or size.y < 1:
            return
        self._recalcCoords(size)

    def _OnDestroyWindow(self, evt):
        self.timer.Stop()
        del self.timer

    def _OnTimer(self, evt):
        self.Refresh(False)
        self.Update()
        if self.cangle < 360:
            self.timer.Start(1, True)
        else:
            remaintostop = self.stopangle - self.cangle
            if remaintostop <= 0:
                return
            stoplen = len(self.stopdelay)
            delay = 1 if remaintostop > stoplen else self.stopdelay[
                stoplen - remaintostop]
            if self.cangle < self.stopangle:
                self.timer.Start(delay, True)

    def _OnRoll(self, evt):
        if self.stopangle <= self.cangle:
            self.stopangle = self.cangle + 360 + random.randint(0, 360)
            self.timer.Start(1, True)

    def incAngle(self):
        if self.cangle % 60 == 0:
            print 60 / (time.time() - self.rotstartt), "FPS"
            self.rotstartt = time.time()
        self.cangle += 1
        return self.cangle % 360

    def _recalcCoords(self, size):
        self.clientsize = self.GetClientSizeTuple()
        mc = min(self.clientsize)
        self.clientsize = (mc, mc)
        print self.clientsize
        self.adj = min(self.clientsize[0] / 15, self.clientsize[1] / 10)
        self.calfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.calfont.SetPointSize(self.adj)
        self.smallfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.smallfont.SetPointSize(self.adj / 2)
        self.mcenterx = self.clientsize[0] / 2
        self.mcentery = self.clientsize[1] / 2
        self.maxlen = min(self.mcenterx, self.mcentery)

        self.rotatedimage = {}
        self.cangle = 0
        self.rotstartt = time.time()
        self.stopangle = 360 + 180 + random.randint(0, 360)

    def _writeRotateImage(self, image, angle):
        filename = "/tmp/roulette%03d.bmp" % (angle % 90)
        image.SaveFile(filename, wx.BITMAP_TYPE_BMP)

    def _readRotateImage(self, angle):
        filename = "/tmp/roulette%03d.bmp" % (angle % 90)
        rimage = None
        if os.path.isfile(filename):
            rimage = wx.Image(filename)
        return rimage

    def _makeRotatedImage(self, image, angle):
        angle = angle % 90
        if angle == 0:
            return image
        rad = math.radians(-angle)
        xlen, ylen = image.GetWidth(), image.GetHeight()
        offset = wx.Point()
        rimage = image.Rotate(rad, (xlen / 2, ylen / 2), True, offset)
        # return rimage
        xnlen, ynlen = rimage.GetWidth(), rimage.GetHeight()
        # print angle , (xnlen , ynlen),offset, (xlen,ylen ) , ( -(
        # xnlen-xlen)/2.0 ,-( ynlen-ylen)/2.0 )

        rimage.Resize(
            (xlen, ylen), (-(xnlen - xlen) / 2.0, -(ynlen - ylen) / 2.0))
        return rimage

    def getAngledImage(self, angle):
        rimage = self._readRotateImage(angle)
        if not rimage:
            rimage = self._makeRotatedImage(self.rotatedimage[0], angle)
            self._writeRotateImage(rimage, angle)
        n = angle / 90
        for a in range(n):
            rimage = rimage.Rotate90()
        return rimage

    def _OnPaint(self, evt):
        if 0 not in self.rotatedimage:
            dc = wx.BufferedPaintDC(self)
            self.rotatedimage[0] = self._readRotateImage(0)
            if not self.rotatedimage[0]:
                # create
                bitmap0 = wx.EmptyBitmap(*self.clientsize)
                dc.SelectObject(bitmap0)
                dc.SetBackground(wx.Brush("Black", wx.SOLID))
                # dc.SetBackground(wx.TRANSPARENT_BRUSH)
                dc.Clear()
                self._drawRoulette(dc, 0)
                self.rotatedimage[0] = bitmap0.ConvertToImage()
                self._writeRotateImage(self.rotatedimage[0], 0)
        else:
            dc = wx.PaintDC(self)
        # rotate
        secangle = int(self.incAngle())
        if secangle not in self.rotatedimage:
            self.rotatedimage[secangle] = self.getAngledImage(secangle)
        rbitmap = self.rotatedimage[secangle].ConvertToBitmap()
        dc.DrawBitmap(rbitmap, 0, 0)
        #dc.DrawBitmap( rbitmap,0,0, True )

    def _drawRoulette(self, dc, startangle=0):
        dc.SetPen(wx.Pen("Black", 3))
        dc.SetBrush(wx.Brush(wx.Colour(0xff, 0xff, 0xff), wx.SOLID))
        dc.DrawCircle(
            self.clientsize[0] / 2, self.clientsize[1] / 2, self.maxlen)

        dc.SetFont(self.smallfont)
        for a in range(0, 360, 10):
            if ((a) / 10) % 2 == 0:
                dc.SetPen(wx.Pen("Black", 1))
                dc.SetBrush(wx.Brush("Black", wx.SOLID))
            else:
                dc.SetPen(wx.Pen("Red", 1))
                dc.SetBrush(wx.Brush("Red", wx.SOLID))
            p1 = self.getpoint(startangle + a, 0.95)
            p2 = self.getpoint(startangle + a, 0.70)
            p3 = self.getpoint(startangle + a + 10, 0.70)
            p4 = self.getpoint(startangle + a + 10, 0.95)
            p5 = self.getpoint(startangle + a + 5, 0.95)

            dc.DrawPolygon((p1, p2, p3, p4, p5))
            p6 = self.getpoint(startangle + a + 5, 0.82)
            self._printText(dc, str(
                (a / 10) * 25 % 36), p6[0], p6[1], True, True, True, 5, startangle + a + 5)

        dc.SetPen(wx.Pen("White", 10))
        dc.SetBrush(wx.Brush(wx.Colour(0x00, 0x7f, 0x00), wx.SOLID))
        dc.DrawCircle(
            self.clientsize[0] / 2, self.clientsize[1] / 2, self.maxlen * 0.70)

        for a in range(0, 360, 10):
            p1 = self.getpoint(startangle + a, 0.95)
            dc.SetPen(wx.Pen("White", 2))
            p2 = self.getpoint(startangle + a, 0.50)
            dc.DrawLine(p1[0], p1[1], p2[0], p2[1])

        dc.SetPen(wx.Pen("White", 10))
        dc.SetBrush(wx.Brush(wx.Colour(0x7f, 0x7f, 0x7f), wx.SOLID))
        dc.DrawCircle(
            self.clientsize[0] / 2, self.clientsize[1] / 2, self.maxlen * 0.50)

        dc.SetFont(self.calfont)
        self._printText(dc, "Roulette", self.clientsize[
                        0] / 2, self.clientsize[1] / 2, True, True, True, 5, startangle)

    def getpoint(self, angle, length):
        rad = math.radians(angle + 270)
        l = self.maxlen * length
        return (self.mcenterx + l * math.cos(rad), self.mcentery + l * math.sin(rad))

    def _printText(self, dc, pstr, x, y, r=True, g=True, b=True, depth=5, angle=0):
        rad = math.radians(-angle)
        w, h = dc.GetTextExtent(pstr)
        x = x - math.cos(rad) * w / 2. - math.sin(rad) * h / 2.
        y = y - math.cos(rad) * h / 2. + math.sin(rad) * w / 2.
        for i in range(0, depth):
            cr = int(i * 255. / (depth - 1)) if depth > 1 else 255
            dc.SetTextForeground(
                wx.Colour(
                    cr if r else cr / 2, cr if g else cr / 2, cr if b else cr / 2, 0x7f)
            )
            dc.DrawRotatedText(
                str(pstr), int(max(0, x + depth - i)), int(max(0, y + depth - i)), -angle)


class AcDemoApp(wx.App):

    def OnInit(self):
        self.frame = wx.Frame(
            None, -1, "roulette", size=(1000, 1000), style=wx.DEFAULT_FRAME_STYLE)

        self.clock = roulette(self.frame, style=wx.STATIC_BORDER)
        self.frame.CentreOnScreen()
        self.frame.Show()
        return True

if __name__ == "__main__":
    print wx.VERSION_STRING
    acApp = AcDemoApp(0)
    acApp.MainLoop()
