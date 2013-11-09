import pycassa
import bisect
import hashlib
import sys

from pycassa.system_manager import *
from pycassa.pool import ConnectionPool
from pycassa.columnfamily import ColumnFamily

class keyspace:
	"""It will contain all keyspace related opertions list,create,delete,select"""
	server_ips = []
	complete_list = {}
	
#------------------------------------------- Error testing ---------------------------------------------------------------------
	# Input : machine_id = '10.3.3.20:9160' name = "keyspace_name"
	# Output :  True/False
	def keyspace_contains(self,keyspace_name,column_family_name = ''):
		"""Returns true if keyspace with given name and/or column family is on specified machine_id """
		for key in keyspace.complete_list:
			if (key == keyspace_name):
				if(column_family_name != ''):
					for cf in keyspace.complete_list[key]:
						if(cf == column_family_name):
							return True
					return False
				else:					
					return True
		return False

	# Input : machine_id = '10.3.3.20:9160' name = "keyspace_name"
	# Output :  True/False
	def keyspace_columnfamily_list(self,machine_id):
		"""Returns dictionary of all keyspace with their column family on specified machine_id """
		sys = SystemManager(machine_id)
		keyspace.complete_list.clear()
		keyspace_list = sys.list_keyspaces()
		for key in keyspace_list:
			x=[]
			result = sys.get_keyspace_column_families(key, use_dict_for_col_metadata=True)
			for i in result:
				x.append(i)
			keyspace.complete_list[key] = x
		sys.close()
		return keyspace.complete_list
			
	# Input : machine_ip = '10.3.3.20' ,machine_port = '9160'
	# Output : ['10.3.3.20:9160','10.3.3.242:9160']		the latest updated list
	def machine_add(self,machine_ip,machine_port ='9160'):
		"""Add the machine to list(server_ips) which can be used in pool"""
		entry = machine_ip +":"+ machine_port
		keyspace.server_ips.append(entry)
		return keyspace.server_ips
	
	def machine_get_list(self):
		return keyspace.server_ips
		
#************************************************** End ************************************************************************

#------------------------------------------- Keyspace----- ---------------------------------------------------------------------
	# Input : machine_id = '10.3.3.20:9160'
	# Output :  ['TK1', 'system', 'testks']	    List of all keyspace on that machine, not possible to pass list of server like in pool 
	def keyspace_get_list(self,machine_id):
		"""Returns all keyspaces in form of list """
		sys = SystemManager(machine_id)
		keyspace_list = sys.list_keyspaces()
		sys.close()
		return keyspace_list

	# Input : machine_id = '10.3.3.20:9160'
	# Output : True
	# Unsuccessful : False
	def keyspace_create(self,machine_id,keyspace_name):
		"""Create keyspace with given name on specified machine_id """
		if (self.keyspace_contains(keyspace_name) == True):
			print "Error : Keyspace with this name already exist."
			return False
		sys = SystemManager(machine_id)
		print sys.create_keyspace(keyspace_name, SIMPLE_STRATEGY, {'replication_factor': '1'})
		self.keyspace_columnfamily_list('localhost:9160')
		sys.close()
		return True
	
	# Input : machine_id = '10.3.3.20:9160' name = "keyspace_name"
	# Output : True
	# Unsuccessful : False
	def keyspace_delete(self,machine_id,keyspace_name):
		"""Delete keyspace with given name on specified machine_id """
		if (self.keyspace_contains(keyspace_name) == False):
			print "Error : Keyspace with this name dosenot exist."
			return False
		sys = SystemManager(machine_id)
		sys.drop_keyspace(keyspace_name)
		self.keyspace_columnfamily_list('localhost:9160')
		sys.close()
		return True
#************************************************** End ************************************************************************

#------------------------------------------- Column Family ---------------------------------------------------------------------
	# Input : machine_id = '10.3.3.20:9160'keyspace_name = 'ks1'
	# Output : ['TestCF','Testcf2']		
	# Unsuccessful : False
	def colum_family_list(self,machine_id,keyspace_name):
		"""List all column family in a given keyspace """
		if (self.keyspace_contains(keyspace_name) == False):
			print "Error : Keyspace with this name dosenot exist."
			return False
		sys = SystemManager(machine_id)
		result = sys.get_keyspace_column_families(keyspace_name, use_dict_for_col_metadata=True)
		x=[]
		for key in result:
			x.append(key)
		return x

	# Input : machine_id = '10.3.3.20:9160',keyspace_name = 'ks1',column_family_name = 'cf1'
	# Output : True
	# Unsuccessful : False
	def colum_family_create(self,machine_id,keyspace_name,column_family_name):
		"""Create a column family in a given keyspace """
		if (self.keyspace_contains(keyspace_name) == False):
			print "Error : Keyspace with this name dosenot exist."
			return False
		sys = SystemManager(machine_id)
		sys.create_column_family(keyspace_name, column_family_name)
		self.keyspace_columnfamily_list('localhost:9160')
		sys.close()
		return True

	# Input : machine_id = '10.3.3.20:9160',keyspace_name = 'ks1',column_family_name = 'cf1'
	# Output : True
	# Unsuccessful : False
	def colum_family_delete(self,machine_id,keyspace_name,column_family_name):
		"""Create a column family in a given keyspace """
		if (self.keyspace_contains(keyspace_name,column_family_name) == False):
			print "Error : Keyspace:column family could not be found."
			return False
		sys = SystemManager(machine_id)
		sys.drop_column_family(keyspace_name, column_family_name)
		self.keyspace_columnfamily_list('localhost:9160')
		sys.close()
		return True
	
	# Important to specify buffer size else cassandra will try to load complete table in main memory which can crash system
	# Input : machine_id = '10.3.3.20:9160',keyspace_name = 'ks1',column_family_name = 'cf1'
	# Output : [ ('Key1', OrderedDict([('AGE', '24'), ('NAME', 'PRAJIT')])),('Key2', OrderedDict([('AGE', '23'), ('NAME', 'MAYUR')])) ]
	# Unsuccessful : False
	def colum_family_content(self,machine_id,keyspace_name,column_family_name):
		"""Returns content of column family of given keyspace """
		if (self.keyspace_contains(keyspace_name,column_family_name) == False):
			print "Error : Keyspace:column family could not be found."
			return False
		pool = ConnectionPool(keyspace = keyspace_name, server_list = keyspace.server_ips, prefill = False)
		col_fam = ColumnFamily(pool, column_family_name)
		tmp_result = col_fam.get_range(start='', finish='',row_count=5,buffer_size=10)
		result = []			
		for i in tmp_result:
			result.append(i)
		#print sum(1 for _ in result)			# for count
		return result

	# Input : machine_id = '10.3.3.20:9160',keyspace_name = 'ks1',column_family_name = 'cf1'
	# Output : True
	# Unsuccessful : False
	def colum_family_insert(self,machine_id,keyspace_name,column_family_name,user_content):
		"""Insert into a column family for a given keyspace """
		if (self.keyspace_contains(keyspace_name,column_family_name) == False):
			print "Error : Keyspace:column family could not be found."
			return False
		pool = ConnectionPool(keyspace = keyspace_name, server_list = keyspace.server_ips, prefill=False)
		col_fam = ColumnFamily(pool, column_family_name)
		for content in user_content:
			col_fam.insert(content,user_content[content])
		#col_fam.insert('Key2', {'name':'mayur', 'age':'23'})
		return True

	# Input : machine_id = '10.3.3.20:9160',keyspace_name = 'ks1',column_family_name = 'cf1'
	# Output : True
	# Unsuccessful : False
	def column_family_remove(self,machine_id,keyspace_name,column_family_name,key):
		"""Remove a key from column family for a given keyspace """
		if (self.keyspace_contains(keyspace_name,column_family_name) == False):
			print "Error : Keyspace:column family could not be found."
			return False
		pool = ConnectionPool(keyspace = keyspace_name, server_list =  keyspace.server_ips, prefill=False)
		col_fam = ColumnFamily(pool, column_family_name)
		col_fam.remove(key)
		return True

def main():
	print "You are in main" 
	key = keyspace()
	#key.machine_add('10.3.3.20','9160')
	#key.machine_add('10.3.3.242','9160')
	key.machine_add('localhost','9160')
	print key.keyspace_columnfamily_list('localhost:9160')
	machine = 'localhost:9160'
	while(True):
		print 'Enter your choice: \n 1) List all keyspace \n 2) Create a keyspace \n 3) Delete a keyspace'
		print ' 4) List all column family for a keyspace \n 5) Create a column family for keyspace'
		print ' 6) Delete a column family from a keyspace \n 7) List content of a column family from keyspace'
		print ' 8) Add content to a column family \n 9) Delete content from a column family'
		print ' 10) List all machines in pool \n 11) Exit'
		x = int(raw_input())
		if (x==1) :
			print "\n"
			result = key.keyspace_get_list('localhost:9160')
		elif (x==2) :
			name = raw_input('Enter name for keyspace to be created :')
			result = key.keyspace_create(machine,name)
		elif (x==3) :
			name = raw_input('Enter keyspace name to be deleted :')
			result = key.keyspace_delete(machine,name)
		elif (x==4) :
			name = raw_input('Enter keyspace name :')
			result = key.colum_family_list(machine,name)
		elif (x==5) :
			ks_name = raw_input('Enter keyspace name :')
			cf_name = raw_input('Enter column family name :')
			result = key.colum_family_create(machine,ks_name,cf_name)
		elif (x==6) :
			ks_name = raw_input('Enter keyspace name :')
			cf_name = raw_input('Enter column family name :')
			result = key.colum_family_delete(machine,ks_name,cf_name)
		elif (x==7) :
			ks_name = raw_input('Enter keyspace name :')
			cf_name = raw_input('Enter column family name :')
			result = key.colum_family_content(machine,ks_name,cf_name)
		elif (x==8) :
			ks_name = raw_input('Enter keyspace name :')
			cf_name = raw_input('Enter column family name :')
			content = raw_input('Enter content :')
			inp = { 'Key1': {'name':'prajit', 'age':'24'} , 'Key2': {'name':'mayur', 'age':'23'} }
			result = key.colum_family_insert( machine, ks_name, cf_name, inp)
		elif (x==9) :
			ks_name = raw_input('Enter keyspace name :')
			cf_name = raw_input('Enter column family name :')
			cf_key = raw_input('Enter key :')
			result = key.column_family_remove(machine,ks_name,cf_name,cf_key)
		elif (x==10) :
			print 'List of machines :\n'
			result = key.machine_get_list()
		else :
			print 'Exit........ing...........\n'
			break
		print result
		raw_input('Press any key to continue...')


if __name__ == "__main__": 
	main()

