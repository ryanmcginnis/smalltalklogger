import collections
import fileinput
import mechanize
import re
from os import chdir
from os import environ
from os import remove
from time import sleep
from time import strftime

home = environ['HOME']
tempFile = "temp.txt"
file = "VLVChatLog_" + strftime("%F") + ".txt"
temp1 = home + "/Desktop/" + tempFile
temp2 = home + "/Desktop/" + file
chdir(home + '/Desktop/')
br = mechanize.Browser()


# http://code.activestate.com/recipes/576694-orderedset/

class OrderedSet(collections.MutableSet):

    def __init__(self, iterable=None):
        self.end = end = [] 
        end += [None, end, end]         # sentinel node for doubly linked list
        self.map = {}                   # key --> [key, prev, next]
        if iterable is not None:
            self |= iterable

    def __len__(self):
        return len(self.map)

    def __contains__(self, key):
        return key in self.map

    def add(self, key):
        if key not in self.map:
            end = self.end
            curr = end[1]
            curr[2] = end[1] = self.map[key] = [key, curr, end]

    def discard(self, key):
        if key in self.map:        
            key, prev, next = self.map.pop(key)
            prev[2] = next
            next[1] = prev

    def __iter__(self):
        end = self.end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def pop(self, last=True):
        if not self:
            raise KeyError('set is empty')
        key = self.end[1][0] if last else self.end[2][0]
        self.discard(key)
        return key

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self))

    def __eq__(self, other):
        if isinstance(other, OrderedSet):
            return len(self) == len(other) and list(self) == list(other)
        return set(self) == set(other)


# get login forms
def select_form(form):
	return form.attrs.get('id', None) == 'auth'	

# authenticate
def auth():
		# br = mechanize.Browser()
		br.set_handle_robots(False)
		br.open('http://board.vivalavinyl.com/chat/history')
		br.select_form(predicate=select_form)
		br.form['name'] = "username" # change this
		br.form['pass'] = "password" # change this
		br.submit()
		br.set_cookie("sid=abcdef; expires=1-Jan-19 23:59:59 GMT")

# scrape and write to file
def wf(x):
		text_file = open(x, 'w')
		response = br.response().read()
		text_file.write(response)
		text_file.close()
		br.open('http://board.vivalavinyl.com/chat/history')

def ff(x):
	# strip first line
	with open(x, 'r') as fin:
		data = fin.read().splitlines(True)
	with open(x, 'w') as fout:
		fout.writelines(data[1:])

	with open(x, 'r') as fin:
		header = fin.read(32)
		lines = fin.readlines()
	with open(x, 'w') as fout:
		fout.writelines(lines)

	# strip nbsp characters 
	with open(x, 'r+') as f:
		text = f.read()
		text = re.sub('&nbsp;', '', text)
		f.seek(0)
		f.write(text)
		f.truncate()
	
	# strip #039 apostrophe characters
	with open(x, 'r+') as f:
		text = f.read()
		text = re.sub('&#039;', '\'', text)
		f.seek(0)
		f.write(text)
		f.truncate()
	
	# strip HTML tags
	with open(x, 'r+') as f:
		text = f.read()
		text = re.sub('<.*?>', '', text)
		f.seek(0)
		f.write(text)
		f.truncate()

# compares temp and master file, then appends differences to master
def sf():
   		with open(temp1) as f: lines1 = OrderedSet(f.readlines())
   		with open(temp2) as f: lines2 = OrderedSet(f.readlines())
   		diffs = (lines1 -lines2)

   		with open(temp2, 'a+') as file_out:
   			for line in diffs:
   				file_out.write(line)

# initial log, creation of master file
try:
	auth()
	wf(temp2)
	ff(temp2)
except: print("Authentication failed!"); quit()

while True:
	try:
		wf(temp1)
		ff(temp1)
		sf()
		print("Logged at " + strftime("%r"))
		sleep(500)
	except KeyboardInterrupt: print("\nUser aborted."); remove(temp1); quit() # would like a more elegant way of quitting
	except: print("Something went wrong during scrape or write."); remove(temp1); quit()
