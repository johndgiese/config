import sys,csv,argparse
from os.path import abspath
import urllib2
import HTMLParser # note that in python 3 this will be html.parser

# TODO: Figure out how to handle tags inside of <td> or <th> tags... currently
# all calls to handle_data will just append on more data (making it looking like
# there are more cells than there really are...). It is not clear to me what the
# most logical way to handle this is. An especially important case is tables
# inside other tables; because tables used to be used for layout purposes, it is
# not unlikely that there will be a table inside another table that has useful
# information in it.  We need to figure out a graceful way to handle this case.

# It turns out that this is more difficult to do than it looks like, and another
# html parsing library may be better suited for it...

class TableExtractor(HTMLParser.HTMLParser):
  ''' see docstring for html_table_to_list '''
  def __init__(self,):
    HTMLParser.HTMLParser.__init__(self)
    self.data = []
    self.in_cell = False  

  def handle_starttag(self, tag, attrs):
    if tag == 'table':
      self.data.append([])
    if tag == 'tr': 
      self.data[-1].append([])
    if tag == 'td' or tag == 'th':
      self.in_cell = True

  def handle_endtag(self, tag): 
    if tag == 'td' or tag == 'th':
      self.in_cell = False

  def handle_data(self, data):
    if self.in_cell:
      self.data[-1][-1].append(data.strip())  

def html_table_to_list(htmlfile):
  ''' Given an html file, will return a list with all the data extracted.
  
  The returned list has an element for each table found on the page, and each 
  table element is itself a list of lists containing the row and cell 
  information (a cell is either a <td> or <th> tag).
  
  For example:
    table_data = html_table_to_list(file)
    row_data = table_data[2][4] # third table, fifth row
    cell_data = row_data[4] # ... fifth element
    
  Note that <tbody> and <thead> tags are appropriatly handled.
  '''
  # TODO: add another parameter that provides custom processing of td content    
  htmlparser = TableExtractor()
  text = htmlfile.read()
  # TODO: add more sophisticated unicode support
  if type(text) == 'unicode':
    text = text.encode('ascii',errors='strict')
  htmlparser.feed(text)
  data = htmlparser.data
  htmlparser.close()
  return data

def table_list_to_csv(table_data, savefile, dialect='excel'):
  ''' Write all of the tables to a single CSV file. '''
  writer = csv.writer(savefile, dialect=dialect)
  for table in table_data:
    writer.writerows(table)

def main(argv=None):
  ''' Interactive tool to convert HTML tables to csv files. '''
  if argv is None:
    argv = sys.argv    
    
  # TODO: add some intelligent table reject heuristic (e.g. small tables are ignored)
  
  ## Parse command line arguments
  parser = argparse.ArgumentParser(description='Extract data from any HTML \
      tables present at a supplied URL (or local file) and save to a CSV file.')  
  parser.add_argument('-i', '--interactive', action='store_true', 
      help='preview and interactively select which tables to save')
  parser.add_argument('-f', '--localfile', action='store_true', help='extract \
      html tables from local file instead of from a URL')
  parser.add_argument('LOC', help='Location of the HTML tables to be extracted.\
      If -f is flagged, then LOC is assumed to be a local file\notherwise it \
      is assumed to be a URL (http is assumed if no protocol is specified)')
  parser.add_argument('DEST', help='destination of the saved CSV file', 
      type=argparse.FileType('wb'))
  args = parser.parse_args(argv[1:])
  is_interactive = args.interactive
  use_local_file = args.localfile
  LOC = args.LOC
  savefile = args.DEST
  
  ## Open the html file (from URL, or a local file)
  if use_local_file:
    html_file = open(LOC,'r')
  else:
    if LOC.find('://') == -1:
      LOC = 'http://' + LOC  
    # make pages think we are a browser:
    req = urllib2.Request(LOC, headers={'User-Agent' : 'Magic Browser'}) 
    html_file = urllib2.urlopen(req)
  
  ## Process data and print summary
  table_data = html_table_to_list(html_file)
  print('')
  if use_local_file:
    prep = 'in'
  else:
    prep = 'at'
  if len(table_data) == 0:
    print('No tables were found %s %s' % (prep, LOC))
    return
  elif len(table_data) == 1:
    print('1 table found %s %s' % (prep, LOC))
  else:
    print('%d tables were found %s %s' % (len(table_data), prep, LOC))
  if is_interactive:    
    ## Print the first few rows of each table
    #  rows_to_print = int(raw_input('How many rows do you want printed? '))
    rows_to_print = 5
    for table_num, table in enumerate(table_data):
      print('\nTable %d (%d rows)' % (table_num + 1,len(table)))
      for row_num, row in enumerate(table[:rows_to_print]):
        print(str(row_num + 1) + ': "' + '", "'.join(row) + '"')
      if rows_to_print < len(table):
        print(str(rows_to_print + 1) + ': ...')      
    
    ## Prompt for tables to save
    tables_to_save = None
    while not tables_to_save:
      tables_to_save = raw_input('\nSelect which tables to download (e.g. 1,2,5,7): ')
      try:
        tables_to_save = [int(tn) for tn in tables_to_save.split(',')]
      except Exception:
        print('Poorly formed input: ' + tables_to_save)
        tables_to_save = None
      if any([True for t in tables_to_save if t > len(table_data)]):
        print('All table numbers must be less than %d.' % len(table_data))
        tables_to_save = None
     
    ## Delete all tables that won't be saved
    table_data = [table_data[i - 1] for i in tables_to_save]
  
  ## Write data to indicated CSV file
  table_list_to_csv(table_data, savefile)
  print('\nData succesfully written to ' + abspath(savefile.name))
  
  return 0
  
if __name__ == '__main__':
  sys.exit(main())
