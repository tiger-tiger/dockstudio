import math
import sys
import os
from parameter import Parameter
from path import Path
import time,os
from daemon import Daemon

class ScoreDaemon(Daemon):
	def __init__(self,user, db, path, proc_name='job', hold_time = 10):
		Daemon.__init__(self,
			path.pidfile(proc_name),
			stdout = path.stdout(proc_name),
			stderr = path.stderr(proc_name))


		self.path = path
		self.user = user
		self.db = db
		self.proc_name = proc_name
		self.hold_time = hold_time
		self.data = {}

	def getScore(self, pid, cid):
		score_file = self.path.pairdir(pid,cid) + '/scoring.log'

		try:
			with open(score_file) as file:
				scores = []
				for line in file.read().split('\n'):
					if 'Estimated Free Energy of Binding' in line:
						scores.append( float(line.split('=',1)[1].split()[0]) )
			score = min(scores)
			self.max = max(score, self.max)
			self.min = min(score, self.min)

			return score
		except:
	                return '_'

	
	def process_pair(self, pid, cid):
		self.data['{}\t{}'.format(pid,cid)] = self.getScore(pid, cid)
		

	def print_table(self):
		filename = self.path.log + '/' + self.proc_name + '_scoring.txt'
		data = '\n'.join(['{}\t{}'.format(key,score) for key,score in self.data.items()])

		with open(filename,'w') as file:
			file.write('{}\t{}\n'.format(self.min, self.max))
			file.write(data.replace('_',self.outside()) + '\n')

	def outside(self):
		try:
			p = int(math.pow(10, int(math.log10(self.max) + 3)))
			return str(p)
		except:
			return 'xxxx'


	def print_score_matrix(self):
		file = open(self.path.log + '/' + self.proc_name + '_matrix.txt','w')
		columns = []
		rows = []
		for key, score in self.data.items():
			x,y = key.split('\t')
			if x not in columns:
				columns.append(x)
			if y not in rows:
				rows.append(y)


		columns = sorted(columns)
		rows = sorted(rows)

		file.write('{}\t{}'.format(self.min,self.max) + '\n\t' + '\t'.join(columns) + '\n')
		outside = self.outside()
		for y in rows:
			file.write(y)
			for x in columns:
				score = str(self.data['{}\t{}'.format(x,y)]).replace('_', outside)
				file.write('\t{}'.format(score))
			file.write('\n')

		file.close()


	def print_heat_matrix(self):
		file = open(self.path.log + '/' + self.proc_name + '_heat_matrix.txt','w')
		columns = []
		rows = []
		for key, score in self.data.items():
			x,y = key.split('\t')
			if x not in columns:
				columns.append(x)
			if y not in rows:
				rows.append(y)


		columns = sorted(columns)
		rows = sorted(rows)

		file.write('{}\t{}'.format(self.min,self.max) + '\n\t' + '\t'.join(columns) + '\n')
		outside = self.outside()
		for y in rows:
			file.write(y)
			for x in columns:
				score = str(self.data['{}\t{}'.format(x,y)]).replace('_', outside)

				if score == 'xxxx' or score == '10000':
					file.write('\t{}'.format(score))
				else:
					score = (float(score) - self.min)/(self.max - self.min)
					file.write('\t{0:.2f}'.format(score))

			file.write('\n')

		file.close()

		

	def print_score(self):
		self.print_table()
		self.print_score_matrix()
		self.print_heat_matrix()

	def run(self):
		while True:
			self.max = float('-inf')
			self.min = float('+inf')
			self.db.foreach(
				lambda pid, cid: self.process_pair(pid, cid)
			)

			self.print_score()
			time.sleep(self.hold_time)

	def restart(self):
		Daemon.restart(self)

	def stop(self):
		self.db.close()
		Daemon.stop(self)


process_name = 'scoring'

p = Parameter()
pt = Path(p)
