import sys
import random
import datetime

from PySide.QtGui import *
from PySide.QtCore import *


class Graph(QGraphicsView):

	TIME = 2
	NUMERIC = 4

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

		self._graphOffsetX = 10
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

		self.rect_item.setPen(QPen(QColor('#4C4C4C')))
		self.scene.addItem(self.rect_item)

		self.graphOrigin = QPointF(	self._contentMarginLeft + self._graphBoundX,
									self.height() - (self._contentMarginBottom + self._graphBoundY))

		self.xAxis = Axis(self, 0, 10)
		self.scene.addItem(self.xAxis)

		self.yAxis = Axis(self, 0, 100, direction=Axis.VERTICAL)
		self.scene.addItem(self.yAxis)

		self.setScene(self.scene)

	def resizeEvent(self, event):
		self.updateGraphSize()

	def updateGraphSize(self):
		self.scene.setSceneRect(self.rect())
		self.rect_item.setRect(	self._contentMarginLeft,
							self._contentMarginTop,
							self.width() - (self._contentMarginRight + self._contentMarginLeft),
							self.height() - (self._contentMarginBottom + self._contentMarginTop))

		self.graphOrigin.setX(self._contentMarginLeft + self._graphBoundX)
		self.graphOrigin.setY(self.height() - (self._contentMarginBottom + self._graphBoundY))

		self.xAxis.update()
		self.yAxis.update()




class Line(QGraphicsLineItem):
	def __init__(self, parent, x1, y1, x2, y2):
		super(Line, self).__init__(x1, y1, x2, y2)

		self.lineWidth = 1
		color = QColor('#BFBFBF')

		pen = QPen(color)
		pen.setWidth(self.lineWidth)
		self.setPen(pen)

		# glow = QGraphicsDropShadowEffect(parent)
		# glow.setColor(color)
		# glow.setOffset(0)
		# glow.setBlurRadius(self.lineWidth * 15)

		# self.setGraphicsEffect(glow)


class Axis(QGraphicsLineItem):
	# Direction
	HORIZONTAL = 1
	VERTICAL = 2

	# Division options
	FIXED = 1
	EVEN = 2
	ROUNDED = 4

	# Data types
	INTEGER = 1
	FLOAT = 2
	DATETIME = 4

	def __init__(self, parent, start_value, end_value, direction=HORIZONTAL):
		super(Axis, self).__init__()

		self.setPen(QPen(QColor('#BFBFBF')))

		self._direction = direction
		self._start_value = start_value
		self._end_value = end_value
		self._view = parent

		self._set_data_type()

		# Default values
		self._divisionLenght = 10
		self._divisionType = self.FIXED
		self._maxDivisions = 10
		self._minDivisionSpace = 20
		self._divisionOffset = 3

		self.showSubdivision = True
		self._subDivisionLength = 5

		if self._data_type == self.DATETIME:
			self._subdivisionAmount = 4
		else:
			self._subdivisionAmount = 10

		self._divisions = []
		self._subDivisions = []

		x1 = self._view.graphOrigin.x()
		y1 = self._view.graphOrigin.y()

		if direction == self.HORIZONTAL:
			divisionLine = QLineF(0, self._divisionOffset, 0, -self._divisionLenght + self._divisionOffset)
		else:
			divisionLine = QLineF(-self._divisionOffset, 0, self._divisionLenght - self._divisionOffset, 0)

		self.startLine = DivisionLine(divisionLine.translated(x1, y1), parent=self, scene=self.scene())
		self.startLine.setText(str(self._start_value))
		self.endLine = DivisionLine(divisionLine.translated(x1, y1), parent=self, scene=self.scene())
		self.endLine.setText(str(self._end_value))

		self.update()

	def _set_data_type(self):
		# Check if both start and end values are datetime.datetime objects
		if isinstance(self._start_value, datetime.datetime) or isinstance(self._end_value, datetime.datetime):
			if type(start_value) == type(end_value):
				self._data_type = self.DATETIME
			else:
				raise TypeError("Both start_value and end_value needs to be a datetime.datetime object.")

		# Check if either start or end value
		elif isinstance(self._start_value, float) or isinstance(self._end_value, float):
			# Ensure both start and end are float
			self._start_value = float(self._start_value)
			self._end_value = float(self._end_value)

			self._data_type = self.FLOAT

		elif isinstance(self._start_value, int) and isinstance(self._end_value, int):
			self._data_type = self.INTEGER

		else:
			raise TypeError('Start and End values must be either datetime.datetime, in or float objects')

	def update(self):
		# Calculate the line for the direction
		x1 = self._view.graphOrigin.x()
		y1 = self._view.graphOrigin.y()
		if self._direction == self.HORIZONTAL:
			length = self._view.width() - (x1 + self._view._contentMarginRight)
			x2 = x1 + (length)
			y2 = y1
			graphLength = length - self._view._graphOffsetX

		else:
			x2 = x1
			y2 = self._view._contentMarginTop
			graphLength = y1 - (y2 + self._view._graphOffsetY)

		self.setLine(x1, y1, x2, y2)

		# Calculate the divisions
		max_fittable_divisions = int(float(graphLength) / self._minDivisionSpace)

		if self._maxDivisions >= 0:
			divisions = min(max_fittable_divisions, self._maxDivisions)
		else:
			divisions = max_fittable_divisions

		division_space = graphLength / divisions

		for i in self._divisions:
			i.scene().removeItem(i)
			del i

		self._divisions = []

		# Use .setPos inplaats van setLine voor goede positionering met parenting

		# Draw the divisions
		if self._direction == self.HORIZONTAL:
			divisionLine = QLineF(0, self._divisionOffset, 0, -self._divisionLenght + self._divisionOffset)
			self.startLine.setLine(divisionLine.translated(x1 + self._view._graphOffsetX, y1))
			self.endLine.setLine(divisionLine.translated(x1 + self._view._graphOffsetX + graphLength, y1))

			for n in xrange(max(0, divisions - 1)):
				p = QPointF(x1 + self._view._graphOffsetX + ((n + 1) * division_space), y2)
				line = DivisionLine(divisionLine.translated(p), parent=self, scene=self.scene())
				self._divisions.append(line)

		else:
			divisionLine = QLineF(-self._divisionOffset, 0, self._divisionLenght - self._divisionOffset, 0)
			self.startLine.setLine(divisionLine.translated(x1, y1 - self._view._graphOffsetY))
			self.endLine.setLine(divisionLine.translated(x1, y1 - self._view._graphOffsetY))
			for n in xrange(max(0, divisions - 1)):
				p = QPointF(x1, y1 - (self._view._graphOffsetY + ((n + 1) * division_space)))
				line = DivisionLine(divisionLine.translated(p), parent=self, scene=self.scene())
				self._divisions.append(line)

class Particle(QGraphicsEllipseItem):
	def __init__(self, p, radius, parent=None, scene=None):
		super(Particle, self).__init__(0, 0, radius*2, radius*2, parent, scene)
		self.radius = radius
		self.pos = p
		self.setBrush(QBrush(QColor('#2CAFFF')))
		self.setPen(Qt.NoPen)
		self.move(p)

		drop_colour = QColor('#2CAFFF')

		drop = QGraphicsDropShadowEffect(parent.scene())
		drop.setColor(drop_colour)
		drop.setOffset(0)
		drop.setBlurRadius(radius*15)

		self.setGraphicsEffect(drop)

	def move(self, p):
		self.pos = p
		self.setPos(self.pos.x() - self.radius, self.pos.y() - self.radius)


class DivisionLine(QGraphicsLineItem):
	def __init__(self, *args, **kwargs):
		super(DivisionLine, self).__init__(*args, **kwargs)
		self.text = ''
		self.textItem = None

	def setLine(self, *args, **kwargs):
		super(DivisionLine, self).setLine(*args, **kwargs)
		self.text.setPos(self.pos())

	def setText(self, text):
		if self.textItem is not None:
			self.textItem.scene().removeItem(self.textItem)
			del self.textItem

		if text:
			self.text = QGraphicsSimpleTextItem(text, parent=self)
			self.text.setPos(self.pos())
		else:
			self.text = None
		









if __name__ == '__main__':
	app = QApplication(sys.argv)
	dialog = Graph()
	dialog.show()
	dialog.activateWindow()
	dialog.raise_()
	app.exec_()