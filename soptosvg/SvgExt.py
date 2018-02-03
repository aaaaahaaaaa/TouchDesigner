"""
Copyright © 2018 Guillaume Onfroy <guillaume.onfroy@gmail.com>
This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.
"""

import svgwrite
import time
import datetime
import numpy
from array import array
from TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions

class SvgExt:

  def __init__(self, ownerComp):
    self.ownerComp = ownerComp
    self.loadParameters()
    print('SvgExt initialized')


  def loadParameters(self):
    self.sop = op(self.ownerComp.par.Sop)
    self.projection = self.ownerComp.par.Projection
    self.camera = op(self.ownerComp.par.Camera)
    self.offsetX = self.ownerComp.par.Offsetx
    self.offsetY = self.ownerComp.par.Offsety
    self.polylineOnly = self.ownerComp.par.Polylineonly
    self.unit = self.ownerComp.par.Unit
    self.scaleToFit = self.ownerComp.par.Scaletofit
    self.canvaW = self.ownerComp.par.Canvaw
    self.canvaH = self.ownerComp.par.Canvah
    self.margin = self.ownerComp.par.Margin
    self.folder = self.ownerComp.par.Folder
    self.filename = self.ownerComp.par.Filename
    self.suffixe = self.ownerComp.par.Suffixe
    self.svg = op('svg')

    if self.camera:
      self.viewMatrix = self.camera.worldTransform
      self.viewMatrix.invert()
      self.projectionMatrix = self.camera.projection(1, 1)


  def SwitchProjection(self):
    self.projection = self.ownerComp.par.Projection
    self.ownerComp.par.Camera.enable = self.projection == 'Camera'
    self.ownerComp.par.Offsetx.enable = not self.projection == 'Camera'


  def formatFilepath(self):
    filepath = str()

    if self.folder:
      filepath += self.folder + '/'

    if str(self.filename).endswith('.svg'):
      self.filename = str(self.filename)[:-4]
    filepath += self.filename

    if self.suffixe == 'Timestamp':
      ts = time.time()
      st = datetime.datetime.fromtimestamp(ts).strftime('%d%m%Y_%H%M%S')
      filepath += '_' + st

    filepath += '.svg'
    self.filepath = filepath


  def getPointsFromMeshSop(self, sop):
    mesh = sop.prims[0]
    polys = [x[:] for x in [[]] * (mesh.numCols + mesh.numRows)]
    for i in range(mesh.numRows):
      for j in range(mesh.numCols):
        polys[i].append(self.parsePoint(mesh[i, j].point))
        polys[mesh.numRows+j].append(self.parsePoint(mesh[i, j].point))
    return polys


  def getPointsFromPolySop(self, sop):
    polys = []
    for prim in sop.prims:
      polys.append([self.parsePoint(vert.point) for vert in prim])
    return polys


  def parsePoint(self, point):
    if self.projection == 'Offset':
      return ((point.x + (point.z*self.offsetX)),
              (point.y + (point.z*self.offsetY)))

    elif self.projection == 'Camera':
      pos = self.projectionMatrix * self.viewMatrix * point.P
      return (pos[0], pos[1])


  def scalePolysToFit(self, polys):
    topLeft = numpy.min([numpy.min(poly, axis=0) for poly in polys], axis=(0))
    bottomRight = numpy.max([numpy.max(poly, axis=0) for poly in polys], axis=(0))
    width = bottomRight[0]-topLeft[0]
    heigth = bottomRight[1]-topLeft[1]
    scale = min((self.canvaW - self.margin*2) / width,
                (self.canvaH - self.margin*2) / heigth)

    for poly in polys:
      for i in range(len(poly)):
        poly[i] = ((poly[i][0]-topLeft[0])*scale + (self.canvaW-width*scale)/2,
                   (poly[i][1]-topLeft[1])*scale + (self.canvaH-heigth*scale)/2)

    return polys


  def drawMesh(self, sop):
    polys = self.getPointsFromMeshSop(sop)

    if self.scaleToFit:
      polys = self.scalePolysToFit(polys)

    for poly in polys:
      p = self.drawing.polyline(points=poly, stroke='black', stroke_width=1, fill='none')
      self.drawing.add(p)


  def drawPoly(self, sop):
    polys = self.getPointsFromPolySop(sop)

    if self.scaleToFit:
      polys = self.scalePolysToFit(polys)

    for poly in polys:
      if self.polylineOnly:
        p = self.drawing.polyline(points=poly, stroke='black', stroke_width=1, fill='none')
      else:
        p = self.drawing.polygon(points=poly, stroke='black', stroke_width=1, fill='none')
      self.drawing.add(p)


  def SaveSvg(self):
    print('Saving SVG...')

    self.loadParameters()
    self.formatFilepath()

    self.drawing = svgwrite.Drawing(
      self.filepath,
      size=('{}{}'.format(self.canvaW, self.unit), '{}{}'.format(self.canvaH, self.unit)),
      viewBox=('0 0 {} {}'.format(self.canvaW, self.canvaH)))

    if len(self.sop.prims) == 0:
      print('Error: no primitive to draw')
      return
    elif isinstance(self.sop.prims[0], Mesh):
      self.drawMesh(self.sop)
    elif isinstance(self.sop.prims[0], Poly):
      self.drawPoly(self.sop)
    else:
      print('Error: unsupported primitive type')
      return

    self.drawing.save()
    print(self.filepath + ' saved')

    self.svg.par.file = self.filepath
    self.svg.par.reload = 0
    self.svg.cook()
    self.svg.par.reload = 1