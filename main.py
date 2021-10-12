# -*- coding: utf-8 -*-
import tkinter
import json
import copy
import grid
import sys

print(sys.getrecursionlimit())
sys.setrecursionlimit(2000)
print(sys.getrecursionlimit())


_W_, _H_ = 900, 800
_X_, _Y_ = 40, _H_-30

color = { 'root': '#282923',
		  'interface': '#282923',
		  'note': '#00A0E5',
		  'bottom': '#00A0E5',
		  'canvas': '#262626',
		  'lines': '#00A0E5',
		  'ovals': '#f5f5f5',
		  'ranges': '#517D8F',
		  'limits': '#517D8F',
		  'grid': '#313131',
		  'text_interface': '#f5f5f5',
		  'text_grid': '#f5f5f5' }

const = { 'end_dist': 2,
		  'length_min': 24,
		  'step_rotate': 4,
		  'step_div': 10 }


class Point:

	def __init__(self, x=0, y=0):
		self.x = x
		self.y = y
		self.id = ''

	def move(self, x, y):
		self.x = x
		self.y = y

	def draw(self, color = '#C70133', fill = color['canvas']):
		x = _X_ + self.x
		y = _Y_ - self.y
		if self.id:
			work.canvas.coords( self.id, x+5, y+5, x-5, y-5 )
		else:
			self.id = work.canvas.create_oval( x+5, y+5, x-5, y-5, width = 2, outline = color , fill = fill )

	def to_erase(self):
		if  self.id:
			work.canvas.delete(self.id)


class End(Point):

	def __init__(self, x, y):
		super().__init__(x, y)

	def __eq__(self, point):
		return ( (point.x - self.x) <= const['end_dist'] and (point.y - self.y) <= const['end_dist'] )

	def draw(self, color = '#C70133'):
		super().draw(color = color)


class GivenPoint(Point):

	def __init__(self, x, y, name = 'point', movable = True, driver = False):
		super().__init__(x, y)
		self.new_x = x
		self.new_y = y
		self.name  = name
		self.movable = movable
		self.driver  = driver
		self.id = work.canvas.create_oval( x+5, y+5, x-5, y-5, width = 2, outline = color['ovals'] )
		self.text_id = work.canvas.create_text( x, y - 15, text = name )
		self.limit = Limit()
		self.end = ''
		self.get_end = ''
		self.note  = ''
		self.range = ''

	def move(self, x, y):
		self.x = self.new_x = x
		self.y = self.new_y = y

	def bind_mouse(self):
		def motion(x, y):
			x = round( x - _X_, 2)
			y = round(_Y_ - y, 2)
			self.move(x, y)
			self.draw_point()
		self.func_id = work.canvas.tag_bind( self.id, "<B1-Motion>", lambda event: motion(event.x, event.y) )

	def draw_point(self):
		x = _X_ + self.x
		y = _Y_ - self.y
		work.canvas.coords(self.id, x+5, y+5, x-5, y-5)
		work.canvas.coords(self.text_id, x, y - 15)
		self.note.entry_x.delete(0, 100)
		self.note.entry_y.delete(0, 100)
		self.note.entry_x.insert(0, self.x)
		self.note.entry_y.insert(0, self.y)

	def unbind_mouse(self):
		work.canvas.tag_bind(self.id, "<B1-Motion>", "")        # перепривязка событий к "пустым"
		work.canvas.tag_bind(self.id, "<Double-Button-1>", "")  # функциям удаляет предыдущую привязку

	def to_erase(self):
		work.canvas.delete(self.id)
		work.canvas.delete(self.text_id)


class Element():

	def __init__(self, A, B):
		self.first = A
		self.last  = B
		self.id = work.canvas.create_line( _X_ + A.x, _Y_ - A.y, _X_ + B.x, _Y_ - B.y, width = 3, fill = color['lines'], tag = 'line' )

	def draw(self):
		x1 = int( _X_ + self.first.x )
		y1 = int( _Y_ - self.first.y )
		x2 = int( _X_ + self.last.x )
		y2 = int( _Y_ - self.last.y )
		work.canvas.coords( self.id, x1, y1, x2, y2)

	def to_erase(self):
		work.canvas.delete(self.id)


class Limit:

	def __init__(self):
		A = Point(-2, -2)
		B = Point(2000, 2000)
		self.lefts(A)
		self.rights(B)
		self.bottoms(A)
		self.tops(B)
		self.id = None

	def __contains__(self, point):
		x1 = self.left.x + self.left_dif
		x2 = self.right.x + self.right_dif
		y1 = self.bottom.y + self.bottom_dif
		y2 = self.top.y + self.top_dif
		return ( (x1 <= point.x <= x2)  and  (y1 <= point.y <= y2) )

	def lefts(self, point, dif=0):
		self.left = point
		self.left_dif = dif

	def rights(self, point, dif=0):
		self.right = point
		self.right_dif = dif

	def bottoms(self, point, dif=0):
		self.bottom = point
		self.bottom_dif = dif

	def tops(self, point, dif=0):
		self.top = point
		self.top_dif = dif

	def draw(self):
		self.to_erase()
		x1 = _X_ + self.left.x + self.left_dif
		y1 = _Y_ - self.bottom.y - self.bottom_dif
		x2 = _X_ + self.right.x + self.right_dif
		y2 = _Y_ - self.top.y - self.top_dif
		self.id = work.canvas.create_rectangle( x1, y1, x2, y2, width = 1, outline = '#C70133' )

	def rectangle(self, A, B):
		self.left.x = min(A.x, B.x)
		self.right.x = max(A.x, B.x)
		self.bottom.y = min(A.y, B.y)
		self.top.y = max(A.y, B.y)

	def to_erase(self):
		work.canvas.delete(self.id)


class Range(Limit):

	def __init__(self):
		super().__init__()

	def generator(self, link = '', nx = const['step_div'], ny = const['step_div']):
		if not link or (link.x == link.end.x and link.y == link.end.y):
			def function():
				return[ (x, y) for x in  range( self.left.x, self.right.x + nx, nx) for y in range(self.bottom.y, self.top.y + ny, ny) ]
			return function
		else:
			def function():
				A, B = link, link.end
				P = Point( round( (A.x + B.x)/2, 2 ), round( (A.y + B.y)/2, 2 ) )
				if A.x == B.x:
					if self.left.x <= P.x <= self.right.x:
						F = Point( Px, self.bottom.y )
						L = Point( Px, self.top.y )
						return [ (P.x, y) for y in range( int(F.y), int(L.y) + ny, ny ) ]
					else:
						return []
				elif A.y == B.y:
					if self.bottom.y <= P.y <= self.top.y:
						F = Point( self.left.x, P.y )
						L = Point( self.right.x, P.y )
						return [ (x, P.y) for x in range( int(F.x), int(L.x) + nx, nx ) ]
					else:
						return []
				else:
					k = -1*(A.x - B.x) / (A.y - B.y)
					b = k*P.x - P.y
					Bo = Point( round( (self.bottom.y + b)/k, 2 ), self.bottom.y)
					To = Point( round( (self.top.y + b)/k, 2 ), self.top.y)
					if    self.left.x == Bo.x or self.left.x == To.x:
						Le = ''
					else:
						Le = Point( self.left.x, round( (k*self.left.x - b), 2 ) )
					if    self.right.x == Bo.x or self.right.x == To.x:
						Ri =''
					else:
						Ri = Point( self.right.x, round( (k*self.right.x - b), 2 ) )
					lst = [ point for point in (Bo, To, Le, Ri)  if point and self.__contains__(point) ]
					if len(lst) == 0:
						return []
					elif len(lst) == 1:
						return [(lst[0].x, lst[0].y)]
					else:
						F, L = lst
				ln = int( chain._length_(F, L) )
				if ln == 0:
					return [ (F.x, F.y, L.x, L.y) ]
				else:
					dx = nx*(F.x - L.x)/ln
					dy = ny*(F.y - L.y)/ln
					return [ ( round( L.x + n*dx, 2), round( L.y + n*dy, 2) ) for n in range( 0, int(ln/nx)+1 ) ]
			return function

	def count(self):
		return len( list( self.generator(nx = const['step_div'], ny = const['step_div'])() ) )

	def draw(self):
		super().draw()
		work.canvas.itemconfig( self.id, outline = '#a3e036' )


class Chain:

	def __init__(self):
		self.config = {}
		self.ends = []
		self.ranges = []
		self.axis = ''
		self.elements = []

	def add_element(self, A, B):
		leng = self._length_(A, B)
		for first, last in (A, B), (B, A):
			if first in self.config:
				self.config[first].update({last: leng})
			else:
				self.config[first] = {last: leng}
			if first.id > last.id:
				element = Element(first, last)
				self.elements.append(element)

	def update(self):   # обновление длин звеньев
		for i in self.config:
			for j in self.config[i]:
				self.config[i][j] = self._length_(i, j)

	def reload_ranges(self):   # создание и обнавление списка координат для точек перебора
		self.ranges = []
		for point in self.config:
			if point.range:
				link_point_to_end = [ link_point for link_point in self.config[point] if link_point.end]
				if not point.movable and link_point_to_end:
					self.ranges.append( (point, point.range.generator( link = link_point_to_end[0] )) )
				else:
					self.ranges.append( (point, point.range.generator( link ='' )) )
		return self.ranges

	def bind_end_points(self, point, A, B): # точка, смежная с двумя другими точками, имеющими конечное положение, так-же получает динамически вычисляемую конечную точку
		def function():
			r1 = self._length_(point, A)
			r2 = self._length_(point, B)
			Q, T = self.intersection_of_circles(A.end, B.end, r1, r2)
			Len = self._length_(point, self.axis)
			if abs(self._length_(Q, self.axis) - Len) >= abs(self._length_(T, self.axis) - Len):
				point.end.move(T.x, T.y)
			else:
				point.end.move(Q.x, Q.y)
		return function

	def reload_ends(self):                                  # создание и обнавление списка точек имеющих конечное положение
		self.ends = []
		for point in self.config:
			if not callable(point.get_end) and point.end:
				self.ends.append(point)
		for point in self.config:
			if callable(point.get_end):                    # является ли атрибут функцией
				point.get_end()                            # запуск отложенного вызова связанного метода
				self.ends.append(point)

	def draw_ends_points(self):
		for point in self.ends:
			point.end.draw()

	def intersection_of_midle_perp(self, A, B, W, U):
		P_x, P_y = (A.x + B.x)/2, (A.y + B.y)/2
		M_x, M_y = (W.x + U.x)/2, (W.y + U.y)/2
		K_ab = -1*(A.x - B.x) / ((A.y - B.y) + .000000001)
		K_wu = -1*(W.x - U.x) / ((W.y - U.y) + .000000001)
		N_x = (M_y - P_y + K_ab*P_x - K_wu*M_x) / (K_ab - K_wu)
		N_y = K_wu*(N_x - M_x) + M_y
		return round(N_x, 2), round(N_y, 2)

	def draw_axis(self):
		if self.axis:
			self.axis.draw(fill = '#C70133')

	def set_axis(self):
		if len(self.ends) > 1:
			A = self.ends[0]
			B = self.ends[1]
			x, y = self.intersection_of_midle_perp(A, A.end, B, B.end)
			if self.axis:
				self.axis.move(x, y)
			else:
				self.axis = Point(x, y)
		elif self.axis:
			self.axis = ''

	def erase_elements(self):
		for element in self.elements:
			element.to_erase()
		self.elements = []

	def get_points(self): # возврашает словарь с точками для сохранения их текущего положения
		points = {}
		for point in self.config:
			points.update( {point.name: (point.x, point.y)} )
		return points

	def set_points(self, points): # расставляет точки по координатам получаемых из словаря от get_points
		for point in self.config:
			for name, coords in points.items():
				if point.name == name:
					point.x, point.y = point.new_x, point.new_y = coords
		self.update()  # обновить длины элементов
		self.drivers() # обновить список драйверов
		self.reload_ends()

	def get_config(self): # взвращает словарь, копию self.config, но вместо обектов Point(), только имена точек
		copy_config = {}
		for i in self.config:
			copy_config[i.name] = {}
			for j in self.config[i]:
				copy_config[i.name].update( {j.name: self.config[i][j]} )
		return copy_config

	def set_config(self, data_points, data_config):
		tmp = {}
		for name in data_points:
			tmp[name] = GivenPoint( *data_points[name], name = name )
			tmp[name].note = Notation( tmp[name] )
		for first in data_config:
			for last in data_config[first]:
				self.add_element( tmp[first], tmp[last] )
		self.update()  # обновить длины элементов
		self.drivers() # обновить список драйверов

	def draw(self): # отрисовывает на холсте все элементы кинематической цепи, диапазонов и пределов
		if work.var_draw.get():
			for element in self.elements:
				element.draw()
			self.draw_ends_points()
			for point in self.config:
				point.draw_point()
				if point.note.var_limit.get():
					point.limit.draw()
				if point.note.var_draw_range.get():
					point.range.draw()
				work.canvas.update()

	def _length_(self, A, B):
		dx = (A.x - B.x)
		dy = (A.y - B.y)
		return round( (dx*dx + dy*dy)**.5, 2 )

	def intersection_of_circles (self, A, B, r1, r2): # возвращает точки пересечения двух окружностей
		d = self._length_(A, B)
		if  d > (r1 + r2) or \
			d < abs(r1 - r2) or \
			(d == 0  and r1 == r2):
			return False, False
		else:
			dx, dy = B.x-A.x, B.y-A.y
			a = ( r1*r1 - r2*r2 + d*d ) / (2*d)
			h = abs(r1*r1 - a*a)**.5
			xm = A.x + a*dx/d
			ym = A.y + a*dy/d
			x1 = round( xm + h*dy/d, 2)
			x2 = round( xm - h*dy/d, 2)
			y1 = round( ym - h*dx/d, 2)
			y2 = round( ym + h*dx/d, 2)
			Q = Point(x1, y1)
			T = Point(x2, y2)
			return Q, T

	def bind_mouse_rotate(self, point):  #получает подвижную точку, возвращает подвижную и неподвижную точки и связывает с событием
		if point.driver:
			for link_point in self.config[point]:
				if not link_point.movable:
					driver = point
					pivot = link_point
					work.canvas.tag_bind( driver.id, "<B1-Motion>", lambda event: self.rotate( event.x -_X_, _Y_ - event.y, driver, pivot ) )
					break

	def rotate(self, x, y, current_driver, pivot):
		dist = ( ((pivot.x - x)**2 + (pivot.y - y)**2)**.5 )+.000001                # расстояние от неподв. точки pivot до курсора с координатами (x, y)
		rad = self.config[pivot][current_driver]                                    
		current_driver.new_x = round( pivot.x + (x - pivot.x)*rad/dist, 2 )         # новые координаты для точки current_driver
		current_driver.new_y = round( pivot.y + (y - pivot.y)*rad/dist, 2 )

		for point in self.config:                                                   # координатам new_x, new_y, подвижных точек, присваиваются нули, дальше
			if point.movable and ( point is not current_driver ):                   # по наличию этих нулей будет определятся получила ли точка новые координаты
				point.new_x = point.new_y = 0

		for iteration in 0, 1, 2:                                                   # количество обходов конфигурации при просчете положений точек
			try:
				for point in self.config:
					if point.movable and ( point.new_x == 0 and point.new_y ==  0):
						link_points = [ link_point for link_point in self.config[point] if (link_point.new_x or link_point.new_y) ]
						if len(link_points) < 2:
							continue
						else:
							link_one, link_two = link_points[:2]
							r1 = self.config[point][link_one]
							r2 = self.config[point][link_two]
							A = Point( link_one.new_x, link_one.new_y )
							B = Point( link_two.new_x, link_two.new_y )
							Q, T = self.intersection_of_circles(A, B, r1, r2)
						if not Q or not T:
							break
						elif self._length_(point, Q) <= self._length_(point, T):
							point.new_x, point.new_y = Q.x, Q.y
						else:
							point.new_x, point.new_y = T.x, T.y
			except:
				print("error")
		if all( [point.new_x + point.new_y for point in self.config] ):
			for point in self.config:
				if point.driver:
					point.old = Point(point.x, point.y)
				point.x, point.y = point.new_x, point.new_y
			return True
		else:
			return False

	def drivers(self):
		'''Возвращает список точек, где каждые три - это точка на окружности, центр этой окружности и её радиус
		Служит для попеременного выбора ведущей точки '''
		driver_list = []
		for point in self.config:
			if point.driver:
				driver_list.append(point)
				for link_point in self.config[point]:
					if not link_point.movable:
						driver_list.append(link_point)
						driver_list.append(self.config[point][link_point])
		return driver_list

	def set_vector(self, driver, pivot, rad, r, vector):
		''' Функция принимает точку на окружности радиусом 'R', с центром в точке 'pivot', шаг смещения длиной 'r'
		и направление вращения 'vector': '1' - по часовой стрелке; '-1' - против часовой стрелки.
		Возвращает точку, на касательной проведенной в точке 'driver' к окружности, на расстояни 'r' от неё.
		Служит для указания направления вращения ведущего звена (кривошип)'''
		dx = (driver.y - pivot.y) * r/rad * vector
		dy = (pivot.x - driver.x) * r/rad * vector
		x = driver.x + dx
		y = driver.y + dy
		return Point(x, y)

	def get_vector(self, old_point, current_point, pivot, rad, r):
		''' Функция принимает предыдущее и текущее положения точки на окружности радиусом 'R',
		с центром в точке 'pivot' и шаг смещения длиной 'r'.
		Возвращает направление вращения: '1' - по часовой стрелке; '-1' - против часовой стрелки
		Служит для определения направления вращения ведомого звена (коромысло)'''
		dist_1 = self._length_( current_point, self.set_vector(old_point, pivot, rad, r, 1) )
		dist_2 = self._length_( current_point, self.set_vector(old_point, pivot, rad, r, -1) )
		return dist_1 < dist_2 or -1

	def auto_move(self, vector = 1, r = 1):
		''' Функция принимает исходное направление и шаг вращения, "прокручивает" механизм, перемещая точку driver,
		пока не будет достигнуто крайнее положение, затем, сменяет точку driver и двигает новую точку в том направлении,
		в котором она двигалась до того, как получила роль ведущей	'''
		driver, pivot, rad, driver_next, pivot_next, rad_next = self.drivers()[:6]
		for iteration in 0, 1, 2, 3, 4:
			lever = Point( driver.x, driver.y )
			while self.rotate( lever.x, lever.y, driver, pivot ):
				lever = self.set_vector( driver, pivot, rad, r, vector )
				yield
			vector  = self.get_vector( driver_next.old, driver_next, pivot_next, rad, r )
			driver, pivot, rad, driver_next, pivot_next, rad_next = driver_next, pivot_next, rad_next, driver, pivot, rad


class Notation:
	frame = ''
	chain = ''

	def __init__(self, point):
		self.point = point
		self.place = tkinter.Frame( Notation.frame, bg = color['note'], bd = 2, relief = 'solid' )
		self.place.pack()
		tkinter.Label( self.place, text = point.name, fg = color['text_interface'], bg = color['note'] ).grid( row = 0, column = 1, rowspan = 3 )
		# функция изменения координат
		def set_x_y(event):
			self.point.move( round( float(self.entry_x.get()), 2), round( float(self.entry_y.get()), 2) )
			Notation.chain.update()
			Notation.chain.draw()
		self.entry_x = tkinter.Entry( self.place, width = 6 )
		self.entry_y = tkinter.Entry( self.place, width = 6 )
		self.entry_x.grid( row = 0, column = 2, rowspan = 3 )
		self.entry_y.grid( row = 0, column = 3, rowspan = 3 )
		self.entry_x.bind('<Return>', lambda event: set_x_y(event))
		self.entry_y.bind('<Return>', lambda event: set_x_y(event))
		# переменные для переключателей
		self.var_driver = tkinter.BooleanVar()
		self.var_move = tkinter.BooleanVar()
		self.var_limit = tkinter.BooleanVar()
		# переключатель movable/not movable
		def set_movable():
			if self.var_move.get():
				self.point.movable = True
				work.canvas.itemconfig( self.point.id, fill = '' )
			else:
				self.point.movable = False
				work.canvas.itemconfig( self.point.id, fill = color['ovals'] )
				self.point.driver = False
				self.var_driver.set(False)
		self.var_move.set( self.point.movable)
		tkinter.Radiobutton( self.place, text = 'not_mov', variable = self.var_move, value = False, command = set_movable, bg = color['note'] ).grid( row = 0, column = 4, sticky = 'w' )
		tkinter.Radiobutton( self.place, text = 'movabl', variable = self.var_move, value = True,  command = set_movable, bg = color['note'] ).grid( row = 1, column = 4, sticky = 'w' )
		# включатель driver
		def set_driver():
			if self.var_driver.get():
				self.point.driver = True
				self.point.old_x = self.point.x
				self.point.old_y = self.point.y
				work.canvas.itemconfig( self.point.id, fill = 'red' )
				self.point.movable = True
				self.var_move.set(True)
				Notation.chain.drivers()
				#print(Notation.chain.driver_list)
			else:
				self.point.driver = False
				work.canvas.itemconfig( self.point.id, fill = '' )
				Notation.chain.drivers()
		self.var_driver.set( self.point.driver )
		tkinter.Checkbutton( self.place, text = 'driver', variable = self.var_driver, onvalue = True, offvalue = False, command = set_driver, bg = color['note'] ).grid( row = 2, column = 4, sticky = 'w' )
		# лимиты
		self.entry_limit_left = tkinter.Entry( self.place, width = 6 )
		self.entry_limit_right = tkinter.Entry( self.place, width = 6 )
		self.entry_limit_bottom = tkinter.Entry( self.place, width = 6 )
		self.entry_limit_top = tkinter.Entry( self.place, width = 6 )
		self.entry_limit_left.grid( row = 1, column = 7 )
		self.entry_limit_right.grid( row = 1, column = 8 )
		self.entry_limit_bottom.grid( row = 2, column = 7, columnspan = 2 )
		self.entry_limit_top.grid( row = 0, column = 7, columnspan = 2 )
		self.entry_limit_left.insert( 0, self.point.limit.left.x + self.point.limit.left_dif )
		self.entry_limit_right.insert( 0, self.point.limit.right.x + self.point.limit.right_dif )
		self.entry_limit_bottom.insert( 0, self.point.limit.bottom.y + self.point.limit.bottom_dif )
		self.entry_limit_top.insert( 0, self.point.limit.top.y + self.point.limit.top_dif )
		self.entry_limit_left.bind( '<Return>', lambda event: set_limit_left(event) )
		self.entry_limit_right.bind('<Return>', lambda event: set_limit_right(event) )
		self.entry_limit_bottom.bind( '<Return>', lambda event: set_limit_bottom(event) )
		self.entry_limit_top.bind('<Return>', lambda event: set_limit_top(event) )
		# скрыть/показать лимиты
		def draw_limit():
			if self.var_limit.get():
				self.point.limit.draw()
			else:
				self.point.limit.to_erase()
		tkinter.Checkbutton( self.place, variable = self.var_limit, onvalue = True, offvalue = False, command = draw_limit, bg = color['note'] ).grid( row = 0, column = 9 )
		# функции изменения лимитов
		def set_limit_left(event):
			val = self.entry_limit_left.get()
			if not val[0].isalpha():
				point = Point( float(val), self.point.limit.left.y)
				self.point.limit.lefts(point)
			else:
				for point in Notation.chain.config:
					if point.name == val[0]:
						self.point.limit.lefts( point, float((val[1:] or 0)) )
			Notation.chain.draw()

		def set_limit_right(event):
			val = self.entry_limit_right.get()
			if not val[0].isalpha():
				point = Point( float(val), self.point.limit.right.y)
				self.point.limit.rights(point)
			else:
				for point in Notation.chain.config:
					if point.name == val[0]:
						self.point.limit.rights( point, float((val[1:] or 0)) )
			Notation.chain.draw()

		def set_limit_bottom(event):
			val = self.entry_limit_bottom.get()
			if not val[0].isalpha():
				point = Point( self.point.limit.bottom.x,  float(val) )
				self.point.limit.bottoms(point)
			else:
				for point in Notation.chain.config:
					if point.name == val[0]:
						self.point.limit.bottoms( point, float((val[1:] or 0)) )
			Notation.chain.draw()

		def set_limit_top(event):
			val = self.entry_limit_top.get()
			if not val[0].isalpha():
				point = Point( self.point.limit.top.x, float(val) )
				self.point.limit.tops(point)
			else:
				for point in Notation.chain.config:
					if point.name == val[0]:
						self.point.limit.tops( point, float((val[1:] or 0)) )
			Notation.chain.draw()
		# диапазоны
		self.var_set_range = tkinter.BooleanVar()
		self.var_draw_range = tkinter.BooleanVar()
		def set_range():
			if self.var_set_range.get():
				self.point.range = Range()
				self.entry_range_left.insert(0, self.point.range.left.x)
				self.entry_range_right.insert(0, self.point.range.right.x)
				self.entry_range_bottom.insert(0, self.point.range.bottom.y)
				self.entry_range_top.insert(0, self.point.range.top.y)
				Notation.chain.reload_ranges()
			else:
				self.var_draw_range.set(False)
				draw_range()
				self.point.range = ''
				self.entry_range_left.delete(0, 20)
				self.entry_range_right.delete(0, 20)
				self.entry_range_bottom.delete(0, 20)
				self.entry_range_top.delete(0, 20)
				Notation.chain.reload_ranges()
		def draw_range():
			if self.var_set_range.get():
				if self.var_draw_range.get():
					self.point.range.draw()
				else:
					self.point.range.to_erase()
		tkinter.Checkbutton( self.place, variable = self.var_set_range, onvalue = True, offvalue = False, command = set_range, bg = color['note'] ).grid(row = 0, column = 12)
		tkinter.Checkbutton( self.place, variable = self.var_draw_range, onvalue = True, offvalue = False, command = draw_range, bg = color['note'] ).grid(row = 1, column = 12)
		self.label_range = tkinter.Label( self.place, text = '1', fg = color['text_interface'], bg = color['note'] )
		self.label_range.grid( row = 2, column = 12)
		self.entry_range_left = tkinter.Entry( self.place, width = 7 )
		self.entry_range_right = tkinter.Entry( self.place, width = 7 )
		self.entry_range_bottom = tkinter.Entry( self.place, width = 7 )
		self.entry_range_top = tkinter.Entry( self.place, width = 7 )
		self.entry_range_left.grid( row = 1, column = 10 )
		self.entry_range_right.grid( row = 1, column = 11 )
		self.entry_range_bottom.grid( row = 2, column = 10, columnspan = 2 )
		self.entry_range_top.grid( row = 0, column = 10, columnspan = 2 )
		self.entry_range_left.bind( '<Return>', lambda event: set_range_left(event) )
		self.entry_range_right.bind( '<Return>', lambda event: set_range_right(event) )
		self.entry_range_bottom.bind( '<Return>', lambda event: set_range_bottom(event) )
		self.entry_range_top.bind( '<Return>', lambda event: set_range_top(event) )
		# функиции изменения диапазонов
		def set_range_left(event):
			val = self.entry_range_left.get()
			self.point.range.lefts( Point(round(float(val)), self.point.range.left.y) )
			self.label_range['text'] = self.point.range.count()
			Notation.chain.draw()
			Notation.chain.reload_ranges()

		def set_range_right(event):
			val = self.entry_range_right.get()
			self.point.range.rights( Point( round(float(val)), self.point.range.right.y) )
			self.label_range['text'] = self.point.range.count()
			Notation.chain.draw()
			Notation.chain.reload_ranges()

		def set_range_bottom(event):
			val = self.entry_range_bottom.get()
			self.point.range.bottoms( Point(self.point.range.bottom.x, round(float(val))) )
			self.label_range['text'] = self.point.range.count()
			Notation.chain.draw()
			Notation.chain.reload_ranges()

		def set_range_top(event):
			val = self.entry_range_top.get()
			self.point.range.tops( Point(self.point.range.top.x, round(float(val))) )
			self.label_range['text'] = self.point.range.count()
			Notation.chain.draw()
			Notation.chain.reload_ranges()
		# ending
		self.var_end = tkinter.BooleanVar()
		def convert(value):
			try:
				x, y = value.split(',')
				return float(x), float(y)
			except:
				work.label_info0['text'] = "введены некорректные данные"
			return 0, 0
		def set_end():
			if self.var_end.get():
				#self.entry_end.delete(0, 20)
				#self.entry_end.insert(0, "100,100")
				self.point.end = End( *convert(self.entry_end.get()) )
			else:
				self.entry_end.delete(0, 20)
				self.point.end.to_erase()
				self.point.end = ''
			Notation.chain.reload_ends()
			Notation.chain.draw_ends_points()
		tkinter.Checkbutton( self.place, variable = self.var_end, onvalue = True, offvalue = False, command = set_end, bg = color['note'] ).grid(row = 1, column = 13)
		def change_end(event):
			if not self.entry_end.get()[0].isalpha():
				self.point.end.move( *convert(self.entry_end.get()) )
			else:
				A, B = [ point for point in Notation.chain.config if point.name in self.entry_end.get() ]
				self.point.get_end = Notation.chain.bind_end_points( self.point, A, B )
				self.point.get_end()
			Notation.chain.set_axis()
			Notation.chain.draw_axis()
			Notation.chain.reload_ends()
			Notation.chain.draw_ends_points()
		self.entry_end = tkinter.Entry( self.place, width = 8 )
		self.entry_end.grid( row = 1, column = 14 )
		self.entry_end.bind('<Return>', lambda event: change_end(event))


class Interface:
	
	path = "d:\\Python\\kinematic_chain\\"
	name = "ABCDEFGHILRQWTUOPSKJV"
	chain = ''

	def __init__(self):
		self.root = tkinter.Tk()
		self.root.geometry( f'{_W_+700}x{_H_+28}+-7+0' )
		self.root['bg'] = color['root'] #self.root.configure( bg = '#517D8F' )
		self.canvas = tkinter.Canvas( self.root, width = _W_, height = _H_, bg = color['canvas'] )
		self.canvas.grid( row = 0, column = 1, sticky = 'nw' )
		def draw_update(event):
			self.canvas.update()
			Interface.chain.draw()
		self.canvas.bind("<B1-Motion>", draw_update)


		self.frame = tkinter.Frame( self.root, bg = color['root'] )
		self.frame_note = tkinter.Frame( self.root, width = 700)
		self.frame_info = tkinter.Frame( self.root )
		self.frame.grid( row = 0, column = 0, sticky = 'nw' )
		self.frame_note.grid( row = 0, column = 2, sticky = 'nw' )
		self.frame_info.grid( row = 1, column = 0, columnspan = 3, sticky = 'n' )

		self.label_info0 = tkinter.Label( self.frame_info, bg = color['root'], text = 'info0:', fg = 'white' )
		self.label_info0.grid( row = 0, column = 0, sticky = 'n' )
		self.label_info1 = tkinter.Label( self.frame_info, bg = color['root'], text = 'info1:', fg = 'white' )
		self.label_info1.grid( row = 0, column = 1, sticky = 'w' )
		self.label_info2 = tkinter.Label( self.frame_info, bg = color['root'], text = 'info2:', fg = 'white' )
		self.label_info2.grid( row = 0, column = 2, sticky = 'w' )

		grid.grid_create( self.canvas, _X_, _Y_, fill = color['grid'], textfill = color['text_grid'] )

		# переключатель отрисовки движения во время расчета
		self.var_draw = tkinter.BooleanVar()
		self.var_draw.set(True)
		tkinter.Checkbutton( self.frame, text = 'draw', variable = self.var_draw, onvalue = True, offvalue = False, bg = color['root'] ).pack() #, command = set_draw )

		def overlapping(x, y):
			''' Функция принмает координаты прямоугольника.
			Возвращает множество пересекающихся с ним обьектов холста'''
			obj = set(self.canvas.find_overlapping(x-5, y-5, x+5, y+5))
			points = set(i.id for i in Interface.chain.config)
			over = list(points & obj)
			if over:
				return [i for i in Interface.chain.config if i.id == over[0]][0]

		def create_element():
			def point_1(event):
				point = overlapping(event.x, event.y)
				if point:
					A = point
				else:
					x = event.x - _X_
					y = _Y_ - event.y
					A = GivenPoint(x, y, name = Interface.name[0])
					Interface.name = Interface.name[1:]
					A.note = Notation(A)
					A.draw_point()

				def point_2(event):
					global name
					point = overlapping(event.x, event.y)
					if point:
						B = point
					else: 
						x = event.x - _X_
						y = _Y_ - event.y
						B = GivenPoint(x, y, name = Interface.name[0])
						Interface.name = Interface.name[1:]
						B.note = Notation(B)
						B.draw_point()
					Interface.chain.add_element(A, B)
					Interface.chain.draw()
					self.canvas.bind("<Button-1>", point_1)

				self.canvas.bind('<Button-1>', point_2)

			self.canvas.bind('<Button-1>', point_1)

		def edit():
			self.canvas.unbind("<Button-1>")
			for i in Interface.chain.config:
				i.bind_mouse()

		def motion_chain():
			self.canvas.unbind("<Button-1>")
			for i in Interface.chain.config:
				i.unbind_mouse()
			Interface.chain.update()
			Interface.chain.draw()
			for i in Interface.chain.config:
				Interface.chain.bind_mouse_rotate(i)

		def deleted():
			def _del_(event):
				global name
				point = overlapping(event.x, event.y)
				if point:
					self.canvas.delete(point.id)                            # удаляем саму точку
					self.canvas.delete(point.text_id)
					if point.end: self.canvas.delete(point.end.id)
					point.note.place.destroy()
					Interface.name = point.name + Interface.name
					for link_point in Interface.chain.config[point]:
						if len(Interface.chain.config[link_point]) == 1:   # и удаляем смежную точку, если у той больше нет связей
							self.canvas.delete(link_point.id)
							self.canvas.delete(link_point.text_id)
							if point.end: self.canvas.delete(link_point.end.id)
							link_point.note.place.destroy()
							Interface.name = link_point.name + Interface.name
					new = Chain()
					for i in Interface.chain.config:
						for j in Interface.chain.config[i]:
							if i != point and j != point:
								new.add_element(i, j)
					for element in Interface.chain.elements:
						element.to_erase()
					Interface.chain.config = new.config
					Interface.chain.elements = new.elements
				Interface.chain.draw()
			self.canvas.bind("<Button-1>", _del_)

		def generator_presets(buff, ranges):
			point, coords = ranges[0]
			if len(ranges) != 1:
				for x_y in coords():
					buff.update( {point.name: x_y} )
					Interface.chain.set_points(buff)
					Interface.chain.reload_ranges()
					for sets in generator_presets( buff, ranges[1:] ):
						yield sets
			else:
				for x_y in coords():
					buff.update( {point.name: x_y} )
					yield buff
					#Point(*x_y).draw()

		def limit_check():
			for point in Interface.chain.config:
				if point.limit:
					if point not in point.limit:
						#Point(point.x, point.y).draw()
						#print(point.name, "limit")
						return False
			return True

		def ending_check():
			check_list = []
			for point in Interface.chain.ends[:2]:
				if point.end == point:
					check_list.append(True)
				else:
					check_list.append(False)
			return all(check_list)

		def write_json(data):
			file = open( Interface.path + "data.json", "w" )
			json.dump(data, file)  #encoding='utf-8'
			file.close()

		def load_preset():
			#file = open( Interface.path + "data.json", "r" )
			data = Interface.data
			preset = data.pop()
			print(preset)
			Interface.chain.set_points(preset)
			Interface.chain.draw()

		def setup_config():
			file = open( Interface.path + "config.json", "r" )
			data = json.load(file)
			Interface.chain.set_config(*data)
			Interface.chain.draw()

		def save_config():
			config = Interface.chain.get_config()
			points = Interface.chain.get_points()
			file = open( Interface.path + "config.json", "w" )
			json.dump( [points, config], file)
			file.close()

		def go_calculate():
			n = 0
			data = []                                                                                                    # расставляем точки цепи в соответствии с предустановкой
			for preset in generator_presets( Interface.chain.get_points(), Interface.chain.reload_ranges() ):            # получаем от функции очередную предустановку точек
				Interface.chain.set_points(preset)  
				config = Interface.chain.config  
				n += 1
				if any( [const['length_min'] > config[first][last] for first in config for last in config[first]] ):     # сравниваем длины звенеьев с минимально установленной
					print('короткое звено')
					continue
				for start_vector in (-1, 1):                                                                             # и запускаем цикл автовращения сначала по часовой стрелке, затем против часовой
					Interface.chain.set_points(preset)                                                                   # расставляем точки после каждой смены направления вращения
					for step in Interface.chain.auto_move(vector = start_vector, r = const['step_rotate']):
						if not limit_check():
							if n%100 == 0: print(n, 'LIMIT')
							break
						chain.draw()
						if ending_check():
							data.append(copy.copy(preset))
							print(n, 'END')
							print(preset)
							break
			write_json(data)
			print(n, 'FINISH')

		tkinter.Button( self.frame, text = 'CREATE',  fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = create_element ).pack()
		tkinter.Button( self.frame, text = 'EDIT',    fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = edit ).pack()
		tkinter.Button( self.frame, text = 'MOTION',  fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = motion_chain ).pack()
		tkinter.Button( self.frame, text = 'DELETED', fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = deleted ).pack()
		tkinter.Button( self.frame, text = 'ROTATE',  fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = go_calculate ).pack()
		tkinter.Button( self.frame, text = 'SAVE',    fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = save_config ).pack()
		tkinter.Button( self.frame, text = 'LOAD',    fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = setup_config ).pack()
		tkinter.Button( self.frame, text = 'NEXT',    fg = color['text_interface'], width = 8, height = 4, bg = color['bottom'], command = load_preset ).pack()



chain = Chain()
work = Interface()
Notation.frame = work.frame_note
Notation.chain = chain
Interface.chain = chain
Range.div = const['step_div']
file = open( "d:\\Python\\kinematic_chain\\" + "data.json", "r" )
Interface.data = json.load(file)

work.root.mainloop()


