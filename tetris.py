#!/usr/bin/env python3
#-*- coding: utf-8 -*-

# Very simple tetris implementation
# 
# Control keys:
# Down - Drop stone faster
# Left/Right - Move stone
# Up - Rotate Stone clockwise
# Escape - Quit game
# P - Pause game
#
# Have fun!

# Copyright (c) 2010 "Kevin Chabowski"<kevin@kch42.de>
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from random import randrange as rand
import os.path
import sys
import pygame
import pygame.freetype

# The configuration
config = {
	"cell_size": 20,
	"cols": 8,
	"rows": 16,
	"delay": 750,
	"maxfps": 30,
	"font": "green_fuz.otf",
	"font_dir": "Fonts"
}

# colours
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 150, 0)
BLUE = (0, 0, 255)
ORANGE = (255,120, 0)
YELLOW = (255, 255, 0)
MAGENTA = (180, 0, 255)
CYAN = (0, 220, 220)
GREY = (23, 23, 23)
WHITE = (200, 200, 200)

#shapes
T = [[1, 1, 1], [0, 1, 0]]
FOUR = [[0, 2, 2], [2, 2, 0]]
S = [[3, 3, 0], [0, 3, 3]]
SEVEN = [[4, 0, 0], [4, 4, 4]]
L = [[0, 0, 5], [5, 5, 5]]
BAR = [[6, 6, 6, 6]]
SQUARE = [[7, 7], [7, 7]]

class Shape:
	def __init__(self, nr_cols = config['cols'], shape = None):
		self.nr_cols = nr_cols
		if not shape:
			tetris_shapes = [T, FOUR, S, SEVEN, L, BAR, SQUARE]
			self.shape = tetris_shapes[rand(len(tetris_shapes))]
		else:
			self.shape = shape

		self.x = int(nr_cols / 2 - len(self.shape[0])/2)
		self.y = 0
		
	def __len__(self):
		return len(self.shape[0])
		
	def rotate(self):
		rotaded_shape = [[self.shape[y][x] for y in range(len(self.shape))] for x in range(len(self.shape[0]) - 1, -1, -1)]	
		
		shape = Shape(self.nr_cols, rotaded_shape)
		shape.x = self.x
		shape.y = self.y
		
		return shape 
		
	def __iter__(self):
		yield from self.shape
		
	def __repr__(self):
		return '\n'.join([' '.join([str(item) for item in row]) for row in self.shape]) + '\n'


class Board:
	def __init__(self, nr_cols, nr_rows):
		self.board = [[0]*nr_cols for y in range(nr_rows)]
		self.board += [[1]*nr_cols]
		self.nr_cols = nr_cols
		
	def __getitem__(self, idx):
		return self.board[idx]
		
	def remove_full_row(self, idx):
		del self.board[idx]	
		self.board = [[0]*self.nr_cols] + self.board
		
	def __repr__(self):
		return '\n'.join([' '.join([str(item) for item in row]) for row in self.board]) + '\n'

	def add_shape(self, shape, offset):
		off_x, off_y = offset
		for cy, row in enumerate(shape):
			for cx, val in enumerate(row):
				self.board[cy+off_y-1][cx+off_x] += val

	def check_collision(self, shape):
		for cy, row in enumerate(shape):
			for cx, cell in enumerate(row):
				try:
					if cell and self.board[cy + shape.y][cx + shape.x]:
						return True
				except IndexError:
					return True
				except AttributeError:
					raise AssertionError("Input variables should be Shape")
		return False

			
class TetrisApp:
	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(250, 25)
		self.width = config['cell_size']*config['cols']
		self.height = config['cell_size']*config['rows']
		score_board_width = 100
		
		self.screen = pygame.display.set_mode((self.width + score_board_width, self.height))
		caption = "Tetris " + str(config['rows']) + " * " + str(config['cols'])
		pygame.display.set_caption(caption)
		# We do not need mouse movement events, so we block them
		pygame.event.set_blocked(pygame.MOUSEMOTION) 

		self.init_game()
		self.colors = [BLACK, RED, GREEN, BLUE, ORANGE, YELLOW, MAGENTA, CYAN]
		
		font_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),config["font_dir"],config["font"])
		font_size = 15
		self.font = pygame.freetype.Font(font_path, font_size)
		
	def draw_grid(self):
		for x in range(0, self.width, config['cell_size']):
			for y in range(0, self.height, config['cell_size']):
				rect = pygame.Rect(x, y, config['cell_size'], config['cell_size'])
				pygame.draw.rect(self.screen, GREY, rect, 1)	
				
	def new_stone(self):
		self.stone = Shape()
		
		if self.board.check_collision(self.stone):
			self.gameover = True
	
	def init_game(self):
		self.board = Board(config['cols'], config['rows'])
		self.new_stone()
		self.bps_score = 0
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			(msg_image, _) = self.font.render(line, WHITE, BLACK)
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
		
			self.screen.blit(msg_image, (self.width // 2-msgim_center_x, self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix):
		try:
			off_x, off_y  = matrix.x, matrix.y
		except AttributeError:
			off_x, off_y = 0, 0
		cell_size = config['cell_size']
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					pygame.draw.rect(self.screen, self.colors[val], pygame.Rect((off_x+x)*cell_size, (off_y+y)*cell_size, cell_size, cell_size),0)	
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone.x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > config['cols'] - len(self.stone):
				new_x = config['cols'] - len(self.stone)
			
			test_stone = self.stone
			test_stone.x = new_x
			if not self.board.check_collision(test_stone):
				self.stone = test_stone
	
	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit(0)
	
	def update_bps_score(self, nr_full_rows):
		if nr_full_rows > 0:
			nr_full_rows = min(4, nr_full_rows)
			rows_score = {1: 40, 2: 100, 3: 300, 4: 1200}
			self.bps_score += rows_score[nr_full_rows]
		
	def drop(self):
		if not self.gameover and not self.paused:
			self.stone.y += 1
			if self.board.check_collision(self.stone):
				self.board.add_shape(self.stone, (self.stone.x, self.stone.y))
				count_full_rows = 0
				while True:					
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board.remove_full_row(i)
							count_full_rows += 1
							break
					else:
						break
				self.update_bps_score(count_full_rows)
				self.new_stone()
				
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			rotated = self.stone.rotate()
			if not self.board.check_collision(rotated):
				self.stone = rotated
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False
	
	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		self.drop,
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game
		}
		
		self.gameover = False
		self.paused = False
		
		pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
		dont_burn_my_cpu = pygame.time.Clock()
		while True:
			self.screen.fill(BLACK)
			if self.gameover:
				self.center_msg("Game Over!\nPress space to continue")
			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					self.draw_matrix(self.board)
					self.draw_matrix(self.stone)
					self.draw_grid()
					self.font.render_to(self.screen, (self.width + 4, 4), "Score: " + str(self.bps_score), WHITE, BLACK, size = 18)
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop()
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_"+key):
							key_actions[key]()
					
			dont_burn_my_cpu.tick(config['maxfps'])

if __name__ == '__main__':
	App = TetrisApp()
	App.run()
