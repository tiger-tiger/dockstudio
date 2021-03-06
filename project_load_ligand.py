import os
from parameter import Parameter
from path import Path
from ligand import Ligand

p = Parameter()
pt = Path(p)

#locate tree
dir = p._('project.dir')
name = p._('project.wizard.create.name')
project_dir = dir + '/' + name
data_dir = project_dir + '/data' 

filename = '{}/stage/{}'.format(project_dir,p._('project.wizard.load.ligand'))

#import data
molecule = Ligand(pt.liganddb)
molecule.clear()

for id in open(filename):
	id = id.strip('\n')
	molecule.add(id)

molecule.commit()

# download ligand structures
def instage(id, pt):
	return pt.filename('{}.pdb'.format(id), pt.stage, '*.pdb') != None

def copy(id, dir, pt, pids):
	try:
		stagefile = pt.filename('{}.pdb'.format(id), pt.stage, '*.pdb')
		os.system('cp {} {}/{}.pdb'.format(stagefile, dir, id.upper()))

		print('!','stage: ', id, sep = '\t')
	except:
		print('?','stage: ', id, sep = '\t')
		pids.append(id)

def save(id, s, format, dir):
	filename = '{}/{}.{}'.format(dir,id, format)
	with open(filename,'w') as file:
		file.write(s)
	print(id)

structure_dir = project_dir + '/data/structure/ligand'
pids = []
molecule.foreachStructure(
	lambda id, s, format: save(id, s, format, structure_dir),
	lambda id : not instage(id, pt),
	lambda id : copy(str(id), structure_dir, pt, pids)
)

molecule.close()
