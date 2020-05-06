import xlrd 
import xlsxwriter

class Workbook_Writer():
    def __init__(self, workbook_name='Default.xlsx', column_names=list()):
        self.workbook = xlsxwriter.Workbook(workbook_name) 
        self.worksheet = self.workbook.add_worksheet()
        self.bold = self.workbook.add_format({'bold': True})        
        self.Write_Row(1, column_names, True)
        

    def Write_Row(self, row_index, row_values, is_bold=False):
        self.base = ord('A')
        row_index = str(row_index)
        col = 0
        for val in row_values:
            if is_bold:
                self.worksheet.write(chr(self.base+col)+row_index, val, self.bold)
            else:
                self.worksheet.write(chr(self.base+col)+row_index, val)
            col += 1
    
    def Write(self, row_values):
        '''
        row_vales = list of list, where each interior list is a list of values for a row
        '''
        row_index = 2
        for row in row_values:
            self.Write_Row(row_index, row)
            row_index += 1

    def End(self):
        self.workbook.close()

if __name__ == "__main__":
    column_names = ['a', 'b', 'c']
    row_values = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]
    test = Workbook_Writer('test.xlsx', column_names)
    test.Write(row_values)
    test.End()
    pass