''' Run this from command prompt using: python tools_test.py -v '''

import tools,unittest,os
from tempfile import TemporaryFile

class TestTableToList(unittest.TestCase):
    
  def setUp(self):
    pass  
    
  def run_html_table_test(self, test_str, correct):
    ''' Simple wrapper function to avoid repeating table-testing code. '''
    test_file = TemporaryFile()
    test_file.write(test_str)
    test_file.seek(0)    
    testdata = tools.html_table_to_list(test_file)
    msg = '\ngot: ' + str(testdata) + '\ncorrect: ' + str(correct)
    self.assertTrue(testdata == correct, msg)
    test_file.close()
    
  def test_simple_tables(self):
    test_str = """<html><body>
               <table>
                 <tr id="23" ><td>  1 </td><td>2</td></tr>
                 <tr><td>3</td><td>4</td></tr>
               </table>              
               <table>
               <caption>OOPS</caption>
                 <tbody>
                 <tr><td>5</td><td>6</td></tr>
                 <tr><td>7</td><td>8</td></tr>
                 </tbody>
               </table>
               
             </body></html>"""
    correct = [[['1','2'],['3','4']],[['5','6'],['7','8']]]       
    self.run_html_table_test(test_str,correct)
    
  def test_table_with_html(self):
    test_str = """<html><body>    
               <table>
                 <tr><td><p>1</p></td></tr>                 
               </table>               
             </body></html>"""
    correct = [[['<p>1</p>']]]       
    self.run_html_table_test(test_str,correct)
    
  def test_local_file(self):
    test_str = """<html><body>
               <table>
                 <tr><td>1</td><td>2</td></tr>
                 <tr><td>3</td><td>4</td></tr>
               </table>                             
             </body></html>"""
    f = open('unittest.html','w')
    f.write(test_str)
    f.close()
    
    tools.main(['tools.py','-f','unittest.html','unittest.csv'])
  
  def teadDown(self):
    pass

if __name__ == '__main__':
  unittest.main()