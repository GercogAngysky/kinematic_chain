

class grid_create:
	"""построение координатной сетки"""
	def __init__(self, canv, X, Y, fill = '#C8AF64', textfill = 'black'):

		W = int( canv.config('width')[-1] )
		H = int( canv.config('height')[-1] )
		step = 20
		# линии паралельно X
		for y in range( int(Y/step) ):
			canv.create_line( 10, Y-step*y, W-10, Y-step*y, fill = fill, width = 2 if y%5==0 else 1 )
			if y%5==0:
				canv.create_text( X-10, Y - step*y-6, text = f'{step*y}', fill = textfill )
		# линии паралельно Y
		for x in range( int((W-X)/step) ):
			canv.create_line( X+step*x, 10, X+step*x, H-10, fill = fill, width = 2 if x%5==0 else 1 )
			if x%5==0:
				canv.create_text( X+step*x+4, Y + 10, text = f'{step*x}', fill = textfill )



def test():
	import tkinter as tk

	W, H = 500, 500
	X0, Y0 = 50, H-50
	root = tk.Tk()
	canv = tk.Canvas( root, width = W, height = H, bg = '#dfc370' )
	canv.pack()
	grid = grid_create( canv, X0, Y0 )
	root.mainloop()

if __name__ == "__main__":
	test()