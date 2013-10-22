

import pycassa
import sys

from pycassa.system_manager import *
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily

class keyspace:
	"""It will contain all keyspace related opertions list,create,delete,select"""
	
	def get_keyspaces(self,machine_id):
		"""Returns all keyspaces in form of list """
		print "->>>in get keyspace function"
		sys = SystemManager(machine_id)
		keyspace_list = sys.list_keyspaces()
		sys.close()
		return keyspace_list
	
	def keyspace_create(self,machine_id,name):
		"""Create keyspace with given name on specified machine_id """
		print "->>>in create keyspace function"
		sys = SystemManager(machine_id)
		sys.create_keyspace(name, SIMPLE_STRATEGY, {'replication_factor': '1'})
		sys.close()
		return 1
	
	def keyspace_delete(self,machine_id,name):
		"""Delete keyspace with given name on specified machine_id """
		print "->>>in delete keyspace function"
		sys = SystemManager(machine_id)
		key = keyspace()
		if (key.keyspace_contains(machine_id,name)):
			sys.drop_keyspace(name)
		sys.close()
		return 1
	
	def keyspace_contains(self,machine_id,name):
		"""Returns true if keyspace with given name is on specified machine_id """
		print "->>>in contain keyspace function"
		sys = SystemManager(machine_id)
		keyspace_list = sys.list_keyspaces()
		sys.close()
		for i in keyspace_list:
			if (i == name):
				return True
		return False

# Important to specify buffer size else cassandra will try to load complete table which can crash system
	def colum_family_content(self,machine_id,keyspace_name,column_family_name):
		"""Returns content of column family of given keyspace """
		print "->>>in column family content function"
		pool = ConnectionPool(keyspace_name, [machine_id])
		col_fam = ColumnFamily(pool, column_family_name)
		result = col_fam.get_range(start='', finish='')
		return result

	def colum_family_create(self,machine_id,keyspace_name,column_family_name):
		"""Create a column family in a given keyspace """
		print "->>>in column family create function"
		sys = SystemManager(machine_id)
		sys.create_column_family(keyspace_name, column_family_name)
		return 1

	def colum_family_delete(self,machine_id,keyspace_name,column_family_name):
		"""Create a column family in a given keyspace """
		print "->>>in column family create function"
		sys = SystemManager(machine_id)
		sys.drop_column_family(keyspace_name, column_family_name)
		return 1
	
	def colum_family_list(self,machine_id,keyspace_name):
		"""List all column family in a given keyspace """
		print "->>>in column family list function"
		sys = SystemManager(machine_id)
		result = sys.get_keyspace_column_families('TK1', use_dict_for_col_metadata=True)
		x=[]
		for key in result:
			print key
			x.append(key)
		return x


def main():
#	print "You are in main" 
	key = keyspace()
	#key.keyspace_delete('localhost:9160','TestKeyspace')
	#key.keyspace_create('localhost:9160','samp4')
	#key.keyspace_delete('localhost:9160','TK1')
	key.colum_family_create('localhost:9160','TK1','MyCF')
	key.colum_family_list('localhost:9160','TK1')
	key.colum_family_delete('localhost:9160','TK1','MyCF')
	key.colum_family_list('localhost:9160','TK1')
	#keyspace_list = key.get_keyspaces('localhost:9160')
	#print "List of key spaces....." 
	#for i in keyspace_list:
	#	print i
	#result = key.colum_family_content('localhost:9160','TK1','TestCF')
	#for key, columns in result:
	#		print key, '=>', columns


if __name__ == "__main__": 
	main()



