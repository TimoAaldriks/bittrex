import sys
import random

from PySide.QtGui import *
from PySide.QtCore import *


class Graph(QGraphicsView):
	def __init__(self, parent=None):
		super(Graph, self).__init__(parent)
		self.resize(700, 300)

		self._textSize = 12
		self._contentMarginLeft = 12
		self._contentMarginTop = 12
		self._contentMarginRight = 12
		self._contentMarginBottom = 12

		self._graphBoundX = 20
		self._graphBoundY = 20

		self._graphOffsetX = 0
		self._graphOffsetY = 10

		self._dividerLength = 5

		self.xDividers = []
		self.yDividers = []

		self.values = [(x, i) for x, i in enumerate(random.sample(xrange(100), 10))]
		self.x_values = [i[0] for i in self.values]
		self.y_values = [i[1] for i in self.values]

		# self.layout = QVBoxLayout(self)

		# self.view = QGraphicsView(self)
		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.scene = QGraphicsScene(self)
		self.scene.setBackgroundBrush(QBrush(QColor('#3F3F3F')))
		self.scene.setSceneRect(self.rect())

		# self.line1 = Line(self, 0.0, 0.0, self.width(), self.height())
		# self.scene.addItem(self.line1)

		self.rect_item = QGraphicsRectItem(	self._contentMarginLeft,
										self._contentMarginTop,
										self.width() - (self._contentMarginRight + self._contentMarginLeft),
										self.height() - (self._contentMarginBottom + self._contentMarginTop))

		# self.scene.addItem(self.rect_item)

		self.yLine = Line(self, self._contentMarginLeft + self._graphBoundX,
								self._contentMarginTop,
								self._contentMarginLeft + self._graphBoundX,
								self.height() - (self._contentMarginBottom + self._graphBoundY))

		self.xLine = Line(self, self._contentMarginLeft + self._graphBoundX,
								self.height() - (self._contentMarginBottom + self._graphBoundY),
								self.width() - self._contentMarginRight,
								self.height() - (self._contentMarginBottom + self._graphBoundY))

		self.scene.addItem(self.yLine)
		self.scene.addItem(self.xLine)

		xStart = self._contentMarginLeft + self._graphBoundX + self._graphOffsetX
		xEnd = self.width() - self._contentMarginRight
		xLen = xEnd - xStart
		spacing = float(xLen) / float(len(self.values)-1)

		for n, i in enumerate(self.x_values):
			x = xStart + (n * spacing)
			y1 = self.height() - (self._contentMarginBottom + self._graphBoundY)
			y2 = y1 - self._dividerLength
			line = Line(self, x, y1, x, y2)
			self.scene.addItem(line)
			self.xDividers.append(line)

		self.setScene(self.scene)

	def resizeEvent(self, event):
		# self.line1.setLine(0.0, 0.0, self.width(), self.height())
		self.scene.setSceneRect(self.rect())
		self.rect_item.setRect(	self._contentMarginLeft,
							self._contentMarginTop,
							self.width() - (self._contentMarginRight + self._contentMarginLeft),
							self.height() - (self._contentMarginBottom + self._contentMarginTop))

		self.yLine.setLine(	self._contentMarginLeft + self._graphBoundX,
							self._contentMarginTop,
							self._contentMarginLeft + self._graphBoundX,
							self.height() - (self._contentMarginBottom + self._graphBoundY))

		self.xLine.setLine(	self._contentMarginLeft + self._graphBoundX,
							self.height() - (self._contentMarginBottom + self._graphBoundY),
							self.width() - self._contentMarginRight,
							self.height() - (self._contentMarginBottom + self._graphBoundY))


		xStart = self._contentMarginLeft + self._graphBoundX + self._graphOffsetX
		xEnd = self.width() - self._contentMarginRight
		xLen = xEnd - xStart
		spacing = float(xLen) / float(len(self.values)-1)

		for n, i in enumerate(self.x_values):
			x = xStart + (n * spacing)
			y1 = self.height() - (self._contentMarginBottom + self._graphBoundY)
			y2 = y1 - self._dividerLength
			line = Line(self, x, y1, x, y2)
			# self.scene.addItem(line)
			self.xDividers[n].setLine(x, y1, x, y2)




class Line(QGraphicsLineItem):
	def __init__(self, parent, x1, y1, x2, y2):
		super(Line, self).__init__(x1, y1, x2, y2)

		self.lineWidth = 1
		color = QColor('#BFBFBF')

		pen = QPen(color)
		pen.setWidth(self.lineWidth)
		self.setPen(pen)

		glow = QGraphicsDropShadowEffect(parent)
		glow.setColor(color)
		glow.setOffset(0)
		glow.setBlurRadius(self.lineWidth * 15)

		self.setGraphicsEffect(glow)



if __name__ == '__main__':
	app = QApplication(sys.argv)
	dialog = Graph()
	dialog.show()
	dialog.activateWindow()
	dialog.raise_()
	app.exec_()