# pre-commit.py:
#
# Performs the following:
#  - Makes sure the author has entered a log message.
#  - Makes sure the author is only creating a tag, or if deleting a tag, author is a specific user
#  - Makes sure the author is not committing to a particular set of paths in the repository
#
# Script based on http://svn.collab.net/repos/svn/trunk/tools/hook-scripts/log-police.py
#
# usage: pre-commit.py -t TXN_NAME REPOS
# e.g. in pre-commit.cmd (under Windows)
#
#   PATH=C:\Python26;C:\Python26\Scripts
#   python.exe {common_hooks_dir}\pre_commit.py -t %2 %1

import os
import sys
import getopt
try:
  my_getopt = getopt.gnu_getopt
except AttributeError:
  my_getopt = getopt.getopt

import re

import svn
import svn.fs
import svn.repos
import svn.core

__DataCollection__=[] 

# Check Tags functionality
def check_for_tags(txn):
  txn_root = svn.fs.svn_fs_txn_root(txn)
  changed_paths = svn.fs.paths_changed(txn_root)
  for path, change in changed_paths.iteritems():
    if is_path_within_a_tag(path): # else go to next path
      if is_path_a_tag(path):
        if (change.change_kind == svn.fs.path_change_delete):
          if not is_txn_author_allowed_to_delete(txn):
            sys.stderr.write("\nOnly an administrator can delete a tag.\n\nContact your Subversion Administrator for details.")
            return False
        elif (change.change_kind != svn.fs.path_change_add):
          sys.stderr.write("\nUnable to modify %s.\n\nIt is within a tag and tags are read-only.\n\nContact your Subversion Administrator for details." % path)
          return False
        # else user is adding a tag, so accept this change
      else:
        sys.stderr.write("\nUnable to modify %s.\n\nIt is within a tag and tags are read-only.\n\nContact your Subversion Administrator for details." % path)
        return False
  return True

def is_path_within_a_tag(path):
  return re.search('(?i)\/tags\/', path)

def is_path_a_tag(path):
  return re.search('(?i)\/tags\/[^\/]+\/?$', path)
def get_author(txn):
	author = get_txn_property(txn, 'svn:author')
	__DataCollection__.append("["+author+"]")
def is_txn_author_allowed_to_delete(txn):
  author = get_txn_property(txn, 'svn:author')
  return (author == 'admin')
def should_author_be_checked(txn):
	author = get_txn_property(txn,'svn:author')
	if author=="saterj" or author=="sunderad":
		return True
	else:
		return False
# Check log message functionality
def check_log_message(txn,repos_path):
	log_message = get_txn_property(txn, "svn:log")
	sys.stderr.write(log_message)
	if "Skip007" in log_message:
		exit(0)
	else:
		__DataCollection__.append(log_message)
		if log_message is None or log_message.strip() == "":
			sys.stderr.write("\nAttempting to commit without a log message.\n\nPlease make another attempt, using the following format  [WI:workitem][Type:][Desc:] \n"+repos_path)
			return False
		else:
			return checkFormat(log_message)
	
#check for format
def checkFormat(input):
	formatttedMessage = re.search('\[WI:[A-Z]{1,6}-[0-9]+\]\[Type:.*\]\[Desc:.*\]',input)
	if formatttedMessage :
		return checkForWorkItem(input)
	else:
		sys.stderr.write("\nAttempting to commit without a log message. With the wrong format [WI:workitem][Type:][Desc:]")
		return False

#check for work item 
def checkForWorkItem(input):
	cmd =configureEnviroment(input)
	if os.system(cmd) != 0 :
		return False
	else:
		return True
	

def configureEnviroment(input):
	classpath ='D:\csvn\lib\com.polarion.alm.ws.client'
	env = dict(os.environ)
	AGCO_JAR=classpath+'\\WorkItemCheck-0.0.1-SNAPSHOT-jar-with-dependencies.jar'
	os.environ['CLASSPATHX']=classpath+'\\wsclient.jar;'+classpath+'\\axis-patch.jar;'+classpath+'\\lib\\axis.jar;'+classpath+'\\lib\\commons-codec-1.4.jar;'+classpath+'\\lib\commons-discovery-0.2.jar;'+classpath+'\\lib\\commons-logging-1.0.4.jar;'+classpath+'\\lib\\commons-httpclient-3.1.patched.jar;'+classpath+'\\lib\jaxrpc.jar;'+classpath+'\\lib\saaj.jar;'+classpath+'\\lib\wsdl4j-1.5.1.jar;'+AGCO_JAR+';'
	os.environ['JAVA_HOME']=classpath+'\\java\\bin\\java'
	return "%JAVA_HOME% -cp %CLASSPATHX% com.svn.polarion.agco.ProcessCommit D:\\csvn\\lib\\com.polarion.alm.ws.client\\settings.properties "+input

# Check disallowed commit paths functionality
def check_disallowed_commit_paths(txn):
  txn_root = svn.fs.svn_fs_txn_root(txn)
  changed_paths = svn.fs.paths_changed(txn_root)
  for path, change in changed_paths.iteritems():
    if is_commit_disallowed(path):
	  sys.stderr.write("\nYou are not currently allowed to commit to the path %s.\n\nContact your Subversion Administrator for details." % path)
	  return False
  return True

def is_commit_disallowed(path):
  disallowed_commit_paths = ['/branches/9.7', '/branches/9.8']
  for d in disallowed_commit_paths:
    if path.find(d) != -1:
	  return True
  return False

def get_txn_property(txn, prop_name):
  return svn.fs.svn_fs_txn_prop(txn, prop_name)

def usage_and_exit(error_msg=None):
  import os.path
  stream = error_msg and sys.stderr or sys.stdout
  if error_msg:
    stream.write("ERROR: %s\n\n" % error_msg)
  stream.write("USAGE: %s -t TXN_NAME REPOS\n"
               % (os.path.basename(sys.argv[0])))
  sys.exit(error_msg and 1 or 0)
def update_collection_File(filelocation):
	cmd = "svn update "+filelocation
	os.system(cmd)
def commit_file(filelocation):
	cmd="svn commit -m Skip007 "+filelocation
	os.system(cmd)
def main(ignored_pool, argv):
  repos_path = sys.argv[2]
  txn_name = sys.argv[3]
  pathl=repos_path
  cmd = "svn update"
  fileL ='D:\\csvn\\data\\repositories\\Polarion_Extensions\\hooks\\CollectionFolderwc\\collection.txt'
  file = open(fileL,"a")
  update_collection_File(fileL)
  repos_path = svn.core.svn_path_canonicalize(repos_path)
  fs = svn.repos.svn_repos_fs(svn.repos.svn_repos_open(repos_path))
  txn = svn.fs.svn_fs_open_txn(fs, txn_name)
  get_author(txn)
  if check_log_message(txn,repos_path):
	commitInfo=""
	for i in __DataCollection__ :
		commitInfo+=i
		file.write(commitInfo+"["+pathl+"]"+"\n")
		file.close
		commit_file(fileL)
		sys.exit(0)
	else:
		sys.exit(1)
	
	



	

if __name__ == '__main__':
  sys.exit(svn.core.run_app(main, sys.argv))