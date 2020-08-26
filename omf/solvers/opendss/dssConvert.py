# Prereq: `pip install 'git+https://github.com/NREL/ditto.git@master#egg=ditto[all]'`
import os
import sys
from ditto.store import Store
from ditto.readers.opendss.read import Reader as dReader
from ditto.writers.opendss.write import Writer as dWriter
from ditto.readers.gridlabd.read import Reader as gReader
from ditto.writers.gridlabd.write import Writer as gWriter
from collections import OrderedDict
import warnings

def gridLabToDSS(inFilePath, outFilePath):
	''' Convert gridlab file to dss. ''' 
	model = Store()
	# HACK: the gridlab reader can't handle brace syntax that ditto itself writes...
	# command = 'sed -i -E "s/{/ {/" ' + inFilePath
	# os.system(command)
	gld_reader = gReader(input_file = inFilePath)
	gld_reader.parse(model)
	model.set_names()
	dss_writer = dWriter(output_path=".")
	# TODO: no way to specify output filename, so move and rename.
	dss_writer.write(model)

def dssToGridLab(inFilePath, outFilePath, busCoords=None):
	''' Convert dss file to gridlab. '''
	model = Store()
	#TODO: do something about busCoords: 
	dss_reader = dReader(master_file = inFilePath)
	dss_reader.parse(model)
	model.set_names()
	glm_writer = gWriter(output_path=".")
	# TODO: no way to specify output filename, so move and rename.
	glm_writer.write(model)

def dssToTree(pathToDss):
	''' Convert a .dss file to an in-memory, OMF-compatible "tree" object.
	Note that we only support a VERY specifically-formatted DSS file.'''
	# Ingest file.
	with open(pathToDss, 'r') as dssFile:
		contents = dssFile.readlines()
	# Lowercase everything. OpenDSS is case insensitive.
	contents = [x.lower() for x in contents]
	# Clean up the file.
	for i, line in enumerate(contents):
		# Remove whitespace.
		contents[i] = line.strip()
		# Comment removal
		bangLoc = line.find('!')
		if bangLoc != -1:
			contents[i] = line[:bangLoc]
		# Join using the tilde (~) syntax
		if line.startswith('~'):
			# Look back to find the first line with content.
			for j in range(i - 1, 0, -1):
				if contents[j] != '':
					contents[j] = contents[j] + contents[i].replace('~', ' ')
					contents[i] = ''
					break
	# Capture original line numbers and drop blanks
	contents = dict([(c,x) for (c, x) in enumerate(contents) if x != ''])
	# Lex it
	for i, line in contents.items():
		jpos = 0
		try:
			#HACK: only support white space separation of attributes.
			contents[i] = line.split()
			# HACK: only support = assignment of values.
			from collections import OrderedDict 
			ob = OrderedDict() 
			ob['!CMD'] = contents[i][0]
			if len(contents[i]) > 1:
				for j in range(1, len(contents[i])):
					jpos = j
					k,v = contents[i][j].split('=')
					ob[k] = v
			contents[i] = ob
		except:
			raise Exception(f'Error encountered in group (space delimited) #{jpos+1} of line {i + 1}: {line}')
	# Print
	# for line in contents:
	# 	print line
	contents = contents.values()
	return contents

def treeToDss(treeObject, outputPath):
	outFile = open(outputPath, 'w')
	for ob in treeObject:
		line = ob['!CMD']
		for key in ob:
			if key not in ['!CMD']:
				line = line + ' ' + key + '=' + ob[key]
		outFile.write(line + '\n')
	outFile.close()

def evilDssTreeToGldTree(dssTree):
	''' World's worst and ugliest converter. Hence evil. 
	We built this to do quick-and-dirty viz of openDSS files. '''
	gldTree = {}
	g_id = 1
	# TODO: find all buses without coords. Ick.
	# Build bad gld representation of each object
	for ob in dssTree:
		if ob['!CMD'] == 'setbusxy':
			gldTree[str(g_id)] = {
				"object": "node",
				"name": ob['bus'],
				"latitude": ob['y'],
				"longitude": ob['x']
			}
		elif ob['!CMD'] == 'new':
			obtype, name = ob['object'].split('.')
			#TODO: set "object" keys correctly by finding the '.' or splitting.
			if 'bus1' in ob and 'bus2' in ob:
				# line-like object.
				gldTree[str(g_id)] = {
					"object": obtype,
					"name": name,
					# strip the weird dot notation stuff via find.
					"from": ob['bus1'][0:ob['bus1'].find('.')],
					"to": ob['bus2'][0:ob['bus2'].find('.')]
				}
				#TODO: exclude some of the keys.
				other_keys = {k: ob[k] for k in ob if k not in ['object','bus1','bus2','!CMD']}
				gldTree[str(g_id)].update(other_keys)
			elif 'buses' in ob:
				#transformer-like object.
				fro, to = ob['buses'].replace('(','').replace(')','').split(',')
				gldTree[str(g_id)] = {
					"object": obtype,
					"name": name,
					"from": fro,
					"to": to
				}
				other_keys = {k: ob[k] for k in ob if k not in ['object','buses','!CMD']}
				gldTree[str(g_id)].update(other_keys)
			elif 'bus' in ob:
				#load-like object.
				gldTree[str(g_id)] = {
					"object": obtype,
					"name": name,
					"parent": ob['bus']
				}
				other_keys = {k: ob[k] for k in ob if k not in ['object','bus','!CMD']}
				gldTree[str(g_id)].update(other_keys)
			else:
				#config-like object.
				gldTree[str(g_id)] = {
					"object": obtype,
					"name": name
				}
				other_keys = {k: ob[k] for k in ob if k not in ['object','!CMD']}
				gldTree[str(g_id)].update(other_keys)
		elif ob['!CMD'] not in ['new', 'setbusxy']:
			#command-like objects.
			gldTree[str(g_id)] = {
				"object": "!CMD",
				"name": ob['!CMD']
			}
			other_keys = {k: ob[k] for k in ob if k not in ['!CMD']}
			gldTree[str(g_id)].update(other_keys)
		else:
			warnings.warn(f'Ignored {ob}')
		g_id += 1
	return gldTree

if __name__ == '__main__':
	tree = dssToTree('ieee37_ours.dss')
	# treeToDss(tree, 'ieee37p.dss')
	# dssToMem('ieee37.dss')
	# dssToGridLab('ieee37.dss', 'Model.glm') # this kind of works
	# gridLabToDSS('ieee37_fixed.glm', 'ieee37_conv.dss') # this fails miserably
	evil_glm = evilDssTreeToGldTree(tree)
	from omf import feeder, distNetViz
	feeder.dump(evil_glm, './evil.glm')
	distNetViz.viz('./evil.glm', open_file=True) #forceLayout=True, 
	#TODO: make parser accept keyless items with new !keyless_n key?