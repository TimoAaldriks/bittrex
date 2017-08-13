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

		# self.setCursor(Qt.CrossCursor)

		self._textSize = 12
		self._contentMarginLeft = 25
		self._contentMarginTop = 12
		self._contentMarginRight = 55
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

		self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.scene = QGraphicsScene(self)
		self.scene.setBackgroundBrush(QBrush(QColor('#3F3F3F')))
		self.scene.setSceneRect(self.rect())

		self.rect_item = QGraphicsRectItem(	self._contentMarginLeft,
										self._contentMarginTop,
										self.width() - (self._contentMarginRight + self._contentMarginLeft),
										self.height() - (self._contentMarginBottom + self._contentMarginTop))

		self.graphOrigin = QPointF(	self._contentMarginLeft + self._graphBoundX,
									self.height() - (self._contentMarginBottom + self._graphBoundY))

		start = datetime.datetime(2017, 8, 1)
		end = datetime.datetime(2017, 8, 31)

		self.xAxis = Axis(self, start, end)
		self.scene.addItem(self.xAxis)
		# self.xAxis.cursorLine.glow()

		self.yAxis = Axis(self, 0, 100, direction=Axis.VERTICAL)
		self.scene.addItem(self.yAxis)
		# self.yAxis.cursorLine.glow()

		self.setScene(self.scene)
		self.setMouseTracking(True)

	def resizeEvent(self, event):
		self.updateGraphSize()

	def updateGraphSize(self):
		self.scene.setSceneRect(self.rect())

		self.graphOrigin.setX(self._contentMarginLeft + self._graphBoundX)
		self.graphOrigin.setY(self.height() - (self._contentMarginBottom + self._graphBoundY))

		self.xAxis.update()
		self.yAxis.update()

	def mouseMoveEvent(self, event):
		x = event.pos().x()
		y = event.pos().y()

		min_x = self.graphOrigin.x() + self._graphOffsetX
		max_x = self.width() - self._contentMarginRight
		min_y = self._contentMarginTop
		max_y = self.height() - (self._contentMarginBottom + self._graphOffsetY + self._graphBoundY)
		if min_x <= x <= max_x and min_y <= y <= max_y:
			self.xAxis.setCursorPos(event.pos())
			self.yAxis.setCursorPos(event.pos())
			QApplication.setOverrideCursor(Qt.CrossCursor)
		else:
			self.xAxis.setCursorPos(None)
			self.yAxis.setCursorPos(None)
			QApplication.restoreOverrideCursor()

	def enterEvent(self, event):
		self.xAxis.setCursorPos(None)
		self.yAxis.setCursorPos(None)

	def leaveEvent(self, event):
		self.xAxis.setCursorPos(None)
		self.yAxis.setCursorPos(None)
		QApplication.restoreOverrideCursor()


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
		self._float_format = '%.02f'
		self._datetime_fmt = "%d/%m %H:%M"

		self._set_data_type()

		# Default values
		self._divisionLength = 10
		self._divisionType = self.FIXED
		self._maxDivisions = 20
		self._minDivisionSpace = 0
		self._divisionOffset = 3

		self.showSubdivision = True
		self._subDivisionLength = 5
		self._minSubDivisionSpace = 2

		if self._data_type == self.DATETIME:
			self._subdivisionAmount = 4
		else:
			self._subdivisionAmount = 5

		self._cursorLength = 15
		self._cursorOffset = self._divisionOffset

		self._divisions = []
		self._subDivisions = []

		x1 = self._view.graphOrigin.x()
		y1 = self._view.graphOrigin.y()

		if direction == self.HORIZONTAL:
			divisionLine = QLineF(0, self._divisionOffset, 0, -self._divisionLength + self._divisionOffset)
			cursorLine = QLineF(0, 0, 0, -self._cursorLength)
		else:
			divisionLine = QLineF(-self._divisionOffset, 0, self._divisionLength - self._divisionOffset, 0)
			cursorLine = QLineF(0, 0, self._cursorLength, 0)

		if self._data_type in [self.INTEGER, self.FLOAT]:
			startLineText = str(self._start_value)
			endLineText = str(self._end_value)
		else:
			startLineText = self._start_value.strftime(self._datetime_fmt)
			endLineText = self._end_value.strftime(self._datetime_fmt)

		self.startLine = DivisionLine(divisionLine, parent=self, scene=self.scene())
		self.startLine.setPos(x1, y1)
		self.startLine.setText(startLineText)
		self.startLine.setColor(self.pen().color())
		self.endLine = DivisionLine(divisionLine, parent=self, scene=self.scene())
		self.endLine.setPos(x1, y1)
		self.endLine.setText(endLineText)
		self.endLine.setColor(self.pen().color())

		self.cursorLine = DivisionLine(cursorLine, parent=self, scene=self.scene())
		self.cursorLine.setColor(QColor('#48A7FF'))
		self.cursorLine.setVisible(False)
		self.cursorLine.setZValue(1)
		self.cursorLine.setBackdrop(QColor('black'))
		self.cursorLine.setText('Test')
		self.setZValue(0)

		self.update()

	def _set_data_type(self):
		# Check if both start and end values are datetime.datetime objects
		if isinstance(self._start_value, datetime.datetime) or isinstance(self._end_value, datetime.datetime):
			if type(self._start_value) == type(self._end_value):
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
			# self.cursorLine.setLine(0, self._cursorOffset, 0, self._cursorOffset - self._cursorLength)

		else:
			x2 = x1
			y2 = self._view._contentMarginTop
			graphLength = y1 - (y2 + self._view._graphOffsetY)
			# length = self._view.width() - (x1 + self._view._contentMarginRight)
			# self.cursorLine.setLine(-self._cursorOffset, 0, (-self._cursorOffset) + self._cursorLength, 0)

		self.setLine(x1, y1, x2, y2)

		# Calculate the divisions
		# Calculate the minimal division space
		fmStart = self.startLine.fontMetrics()
		fmEnd = self.startLine.fontMetrics()

		if self._direction == self.HORIZONTAL:
			minDivisionSpace = max([fmStart.width(self.divisionText(self._start_value, None, True)) + 15,
									fmEnd.width(self.divisionText(self._end_value, None, True)) + 15,
									self._minDivisionSpace])
		else:
			minDivisionSpace = max([fmStart.height() + 15,
									fmEnd.height() + 15,
									self._minDivisionSpace])

		max_fittable_divisions = int(float(graphLength) / minDivisionSpace)

		if self._maxDivisions >= 0:
			divisions = min(max_fittable_divisions, self._maxDivisions)
		else:
			divisions = max_fittable_divisions

		division_space = graphLength / max(1, divisions)

		# Calculate the subdivisions
		max_fittable_subdivisions  = int(float(division_space) / self._minSubDivisionSpace)
		subDivisions = min(max_fittable_subdivisions, self._subdivisionAmount)

		subdivision_space = division_space / max(1, subDivisions)

		for i in self._divisions:
			i.scene().removeItem(i)
			del i

		self._divisions = []

		# Draw the divisions
		if self._direction == self.HORIZONTAL:
			divisionLine = QLineF(0, self._divisionOffset, 0, -self._divisionLength + self._divisionOffset)
			subDivisionLine = QLineF(0, 0, 0, -self._subDivisionLength)

			self.addSubdivisions(subDivisionLine, QPointF(x1 + self._view._graphOffsetX, y1), subDivisions, subdivision_space)

			self.startLine.setPos(x1 + self._view._graphOffsetX, y1)
			self.endLine.setPos(x1 + self._view._graphOffsetX + graphLength, y1)

			for n in xrange(max(0, divisions - 1)):
				p = QPointF(x1 + self._view._graphOffsetX + ((n + 1) * division_space), y2)
				self.addDivision(divisionLine, p, self.divisionText(n + 1, divisions))
				self.addSubdivisions(subDivisionLine, p, subDivisions, subdivision_space)

		else:
			divisionLine = QLineF(-self._divisionOffset, 0, self._divisionLength - self._divisionOffset, 0)
			subDivisionLine = QLineF(0, 0, self._subDivisionLength, 0)

			self.startLine.setPos(x1, y1 - self._view._graphOffsetY)
			self.endLine.setPos(x1, y1 - (self._view._graphOffsetY + graphLength))

			self.addSubdivisions(subDivisionLine, QPointF(x1, y1 - self._view._graphOffsetY), subDivisions, subdivision_space)

			for n in xrange(max(0, divisions - 1)):
				p = QPointF(x1, y1 - (self._view._graphOffsetY + ((n + 1) * division_space)))
				self.addDivision(divisionLine, p, self.divisionText(n + 1, divisions))
				self.addSubdivisions(subDivisionLine, p, subDivisions, subdivision_space)

	def addDivision(self, line, p, text=None):
		line = DivisionLine(line, parent=self, scene=self.scene())
		line.setPos(p)
		line.setColor(self.pen().color())
		line.setText(text)
		self._divisions.append(line)

	def addSubdivisions(self, line, p, subdivisions, space):
		if self._direction == self.HORIZONTAL:
			for n in xrange(max(0, subdivisions - 1)):
				self.addDivision(line, QPointF(p.x() + ((n + 1) * space), p.y()))
		else:
			for n in xrange(max(0, subdivisions - 1)):
				self.addDivision(line, QPointF(p.x(), p.y() - ((n + 1) * space)))

	def divisionText(self, n, divisions, maxlength=False):
		total = self._end_value - self._start_value
		if self._data_type in [self.INTEGER, self.FLOAT]:
			val = ((float(n) / float(divisions)) * total) + self._start_value
			if not maxlength:
				return (self._float_format % val).rstrip('0').rstrip('.')
			else:
				return self._float_format % val

		else:
			if not maxlength:
				val = datetime.timedelta(seconds=((float(n) / float(divisions)) * total.total_seconds())) + self._start_value
			else:
				val = datetime.datetime.now()

			return val.strftime(self._datetime_fmt)

	def setCursorPos(self, pos):
		x1 = self._view.graphOrigin.x()
		y1 = self._view.graphOrigin.y()
		if pos is not None:
			# QApplication.setOverrideCursor(Qt.CrossCursor)
			self.cursorLine.setVisible(True)
			if self._direction == self.HORIZONTAL:
				self.cursorLine.setPos(pos.x(), y1 + self._cursorOffset)
				# self.cursorLine.setText(str(pos.x()))
			else:
				self.cursorLine.setPos(x1 - self._cursorOffset, pos.y())
				# self.cursorLine.setText(str(pos.y()))

			self.cursorLine.setText(self.valueToText(self.getValue(pos)))
		else:
			self.cursorLine.setVisible(False)
			# QApplication.restoreOverrideCursor()

	def getValue(self, pos):
		total = self._end_value - self._start_value


		if self._direction == self.HORIZONTAL:
			start_pos = self._view.graphOrigin.x() + self._view._graphOffsetX
			end_pos = self._view.width() - self._view._contentMarginRight
			cur_pos = pos.x()
			mult = float(cur_pos - start_pos) / float(end_pos - start_pos)

		else:
			start_pos = self._view._contentMarginTop
			end_pos = self._view.graphOrigin.y() - self._view._graphOffsetY
			cur_pos = pos.y()
			mult = (1 - (float(cur_pos - start_pos) / float(end_pos - start_pos)) )

		if self._data_type in [self.INTEGER, self.FLOAT]:
			# val = (abs(float(cur_pos - start_pos) / end_pos) * total) + self._start_value
			return (mult * total) + self._start_value
		# 	((float(n) / float(divisions)) * total) + self._start_value
		else:
			return datetime.timedelta(seconds=mult * total.total_seconds()) + self._start_value

	def valueToText(self, value):
		if self._data_type in [self.INTEGER, self.FLOAT]:
			return (self._float_format % value).rstrip('0').rstrip('.')

		else:
			return value.strftime(self._datetime_fmt)


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
	# Direction
	HORIZONTAL = 1
	VERTICAL = 2

	def __init__(self, *args, **kwargs):
		super(DivisionLine, self).__init__(*args, **kwargs)
		self.text = ''
		self.textItem = None
		self.textOffset = 5
		self.backDropMargin = 3
		self._backdropItem = None
		self.detectDirection()

	def setLine(self, *args, **kwargs):
		super(DivisionLine, self).setLine(*args, **kwargs)
		self.detectDirection()

	def setColor(self, color):
		self.setPen(QPen(color))
		if self.textItem:
			self.textItem.setBrush(QBrush(color))

	def setBackdrop(self, color=None):
		if self._backdropItem is not None:
			self._backdropItem.scene().removeItem(self._backdropItem)
			del self._backdropItem

		if self.textItem:
			rect = self.marginRect(self.mapFromScene(self.textItem.sceneBoundingRect()).boundingRect())
		else:
			rect = QRectF(0, 0, 0, 0)

		self._backdropItem = QGraphicsRectItem(rect, parent=self)
		self._backdropItem.setZValue(-1)
		self._backdropItem.setPen(Qt.NoPen)
		self._backdropItem.setBrush(QBrush(color))

		if not self.textItem:
			self._backdropItem.setVisible(False)


	def setText(self, text):
		if self.textItem is not None:
			self.textItem.scene().removeItem(self.textItem)
			del self.textItem

		if text:
			self.textItem = QGraphicsSimpleTextItem(text, parent=self)
			self.textItem.setBrush(QBrush(self.pen().color()))
			self.setTextAlignment(Qt.AlignCenter)
			if self._backdropItem:
				rect = self.marginRect(self.mapFromScene(self.textItem.sceneBoundingRect()).boundingRect())
				self._backdropItem.setRect(rect)
				self._backdropItem.setVisible(True)
		else:
			if self._backdropItem:
				self._backdropItem.setVisible(False)
			self.textItem = None

		self.text = text

	def setTextAlignment(self, align):
		rect = self.textItem.sceneBoundingRect()
		if align == Qt.AlignCenter:
			if self.direction == self.HORIZONTAL:
				self.textItem.setPos(-(rect.width() + self.textOffset) + self.line().x1(), -rect.height() / 2.0)
			else:
				self.textItem.setPos(-rect.width() / 2.0, self.line().y1() + self.textOffset)

	def fontMetrics(self):
		if self.textItem:
			return QFontMetrics(self.textItem.font())

	def detectDirection(self):
		a = abs(self.line().angle())
		if a < 45:
			self.direction = self.HORIZONTAL
		else:
			self.direction = self.VERTICAL

	def glow(self):
		drop = QGraphicsDropShadowEffect(self.scene())
		drop.setColor(self.pen().color())
		drop.setOffset(0)
		drop.setBlurRadius(15)

		self.setGraphicsEffect(drop)

	def marginRect(self, rect):
		m = self.backDropMargin
		return rect.adjusted(-m, -m, m, m)








if __name__ == '__main__':
	app = QApplication(sys.argv)
	dialog = Graph()
	dialog.show()
	dialog.activateWindow()
	dialog.raise_()
	app.exec_()