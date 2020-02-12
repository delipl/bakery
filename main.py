import sys
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5 import uic

import query

# load both ui file
uifile1 = 'gui/main.ui'
form1, base1 = uic.loadUiType(uifile1)

uifile2 = 'gui/add.ui'
form2, base2 = uic.loadUiType(uifile2)

uifile3 = 'gui/app.ui'
form3, base3 = uic.loadUiType(uifile3)
uifile4 = 'gui/choice.ui'
form4, base4 = uic.loadUiType(uifile4)

# query
query = query.Query()


class MainWindow(form1, base1):
    switchWindow = QtCore.pyqtSignal()

    def __init__(self):
        super(base1, self).__init__()
        self.add = AddWindow()
        self.app = AppWindow()
        self.setupUi(self)
        self.addButton.clicked.connect(self.goToAdd)
        self.startButton.clicked.connect(self.goToApp)

    def goToAdd(self):
        self.add.show()
        self.add.printRecipes()

    def goToApp(self):
        self.app.show()


class AddWindow(form2, base2):
    switchWindow = QtCore.pyqtSignal()

    def __init__(self):
        super(base2, self).__init__()
        self.choise = ChoiceWindow()
        self.setupUi(self)
        self.setWindowTitle("Piekarnia")

        # wyświetl przepis
        self.tableRecipes.cellChanged.connect(self.choose)
        self.tableRecipes.cellClicked.connect(self.saveCell)
        self.selectedRow = 0
        self.selectedColumn = 0

        self.selectedCell = " "
        self.saveButton.disconnect()
        self.saveButton.clicked.connect(self.saveData)
        self.deleteButton.clicked.connect(self.askIfDeleteRecipe)
        self.differencesRecipes = []
        self.differencesData = []

        rows = query.count("tabele")

        self.recipes = []
        self.recipesDb = []
        self.data = []
        self.dataDb = []

    def saveCell(self, row, column):
        print("CZytam")
        self.selectedCell = self.tableRecipes.item(row, column).text()
        cell = self.selectedCell
        if cell != " " and self.checkExistsRecipesInDb(cell):
            cell = str(cell)
            self.selectedCell = cell
            query.selectId(self.selectedCell)
            self.printData()
        elif cell != " ":
            self.clean()
            self.label.setText(self)
        else:
            self.clean()

    def choose(self, row, column):
        cell = self.tableRecipes.item(row, column).text()
        # print(cell)
        if cell != " " and self.checkExistsRecipesInDb(cell):
            cell = str(cell)
            self.selectedCell = cell
            query.selectId(self.selectedCell)
            self.printData()
        elif cell == " ":
            self.clean()
            self.label.setText("Przepis")
        else:
            self.selectedCell = cell
            self.choise.question("Zmodyfikowano recepturę " + self.selectedCell + ".\nCzy chcesz ją zmodyfikować?")
            self.choise.yes.disconnect()
            self.choise.yes.clicked.connect(self.writeRecipeToDb)
            self.choise.show()

    def printRecipes(self):
        rows = query.count("tabele")
        self.tableRecipes.setRowCount(rows + 5)
        # self.tableRecipes.setColumnCount(1)
        # max = rows + 5
        if rows < 13:
            self.tableRecipes.setRowCount(13)
            max = 13
        else:
            self.tableRecipes.setRowCount(rows + 4)
            max = rows + 4
        for i in range(max):
            if i < rows:
                col = query.read("tabele", i + 1)
                item = str(col)
                self.tableRecipes.setItem(i, 0, QTableWidgetItem(item))
            else:
                self.tableRecipes.setItem(i, 0, QTableWidgetItem(" "))

    def printData(self):
        tab = self.selectedCell
        self.label.setText(tab)
        tab = str(tab)
        rows = query.count(tab)
        self.readDataFromDb(tab)
        if rows < 13:
            self.tableData.setRowCount(13)
            max = 13
        else:
            self.tableData.setRowCount(rows + 4)
            max = rows + 4
        self.tableData.setColumnCount(2)
        self.readDataFromDb(tab)
        for i in range(max):
            if i < rows:
                self.tableData.setItem(i, 0, QTableWidgetItem(self.dataDb[i][0]))
                self.tableData.setItem(i, 1, QTableWidgetItem(self.dataDb[i][1]))
            else:
                self.tableData.setItem(i, 1, QTableWidgetItem(" "))
                self.tableData.setItem(i, 0, QTableWidgetItem(" "))

    def clean(self):
        self.tableData.setRowCount(13)
        self.tableData.setColumnCount(2)
        for i in range(13):
            self.tableData.setItem(i, 0, QTableWidgetItem(" "))
            self.tableData.setItem(i, 1, QTableWidgetItem(" "))

    def readRecipesFromDb(self):
        rows = query.count("tabele")
        self.recipesDb = []
        for i in range(rows):
            col = [2]
            if i < rows:
                # col[ = i+1
                col = query.read("tabele", i + 1)
            self.recipesDb.append(str(col))
        # print("Recipes:", self.recipes)

    def readRecipes(self):
        rows = []
        for i in range(self.tableRecipes.rowCount()):
            cell = self.tableRecipes.item(i, 0).text()
            # print(cell)
            if cell != " ": rows.append(i)
        # print(rows)
        self.recipes = []

        for row in rows:
            txt = self.tableRecipes.item(row, 0).text()
            self.recipes.append(txt)
            # self.checkExistsRecipes(self.data)

    def readDataFromDb(self, tab):
        # print(self.data, len(self.data))
        self.dataDb = []
        rows = query.count(tab)
        for i in range(rows):
            a = query.read(tab, i + 1)
            self.dataDb.append(a)
            self.dataDb[i][1] = self.dataDb[i][1][1:-1]
        # print("Jest z gapą?", self.dataDb)

    def readData(self):
        self.data = []
        cell = [" ", " "]
        for i in range(self.tableData.rowCount()):
            cell[0] = self.tableData.item(i, 0).text()
            cell[1] = self.tableData.item(i, 1).text()
            # print(cell)
            if cell[0] != " " and cell[1] != " ":
                self.data.append(cell[:])

    def differenceData(self):
        self.differencesData = []
        self.readData()
        tab = self.selectedCell
        if tab == " ":
            return 0
        # print("differenceData()")
        self.readDataFromDb(tab)
        found = [0]
        index = 0
        # print(self.data)
        send = [0, "", ""]
        save = " "
        if query.count(tab) > 0:
            for data in self.data:
                for dataDb in self.dataDb:
                    # print("porównuję... ",index, data, dataDb)
                    if dataDb[0] == data[0] and dataDb[1] == data[1]:
                        # print("znalazłem")
                        save = dataDb
                        found.append(0)
                        #dokończ query.exists(tab, col1, col2)
                        found[index] = 1
                        break
                    else:
                        found[index] = 0
                        found.append(0)
                        # print("nie istrnieje")
                # print("0: ", data[0], "1: ", data[1])
                if found[index]:# and self.checkExistsDataInDb(tab, data[0], data[1]):
                    index += 1
                    continue
                else:
                    send = [index+1, data[0], data[1]]
                    self.differencesData.append(send)
                    # print("else:", data)
                    index += 1
            if not self.differencesData:
                return 0
            else:
                # print("differences", send)
                return 1
        else:
            for data in self.data:
                send = [index+1, data[0], data[1]]
                self.differencesData.append(send)
                index += 1
                # print("differences", send)
            return 1

    def differenceRecipes(self):
        self.readRecipes()
        self.readRecipesFromDb()
        output = []
        if len(self.recipesDb) == len(self.recipes):
            print("no Difference")
            return [0]
        else:
            found = []
            for i in range(len(self.recipes)):
                found.append(0)
            index = 0
            saved = ""
            for recipe in self.recipes:
                print(recipe)
            index += 1
            print("out: ", output)
            return output

    def saveData(self):
        if self.differenceData():
            print(self.differencesData)
            self.choise.question("Czy na pewno zapisać?")
            self.choise.show()
            self.choise.yes.disconnect()
            self.choise.yes.clicked.connect(self.writeDataToDb)
            self.choise.no.clicked.connect(self.printData)
        else:
            print("nothing to save")

    def writeDataToDb(self):
        index = 0
        self.readData()
        send = []
        for i in self.data:
            if self.data[index][0] == "" or self.data[index][1] == "":
                self.data[index][0] = ""
                self.data[index][1] = ""
            send.append([index + 1, self.data[index][0], self.data[index][1]])
            index += 1
        # print("send", send)
        query.writeData(self.selectedCell, send)
        self.choise.close()
        self.printData()

    def writeRecipeToDb(self):
        query.createTable(self.selectedCell)
        self.choise.close()
        self.printRecipes()
        self.printData()

    def askIfDeleteRecipe(self):
        self.choise.question("Czy chcesz usunąć recepturę " + self.selectedCell +"?")
        self.choise.show()
        self.choise.yes.disconnect()
        self.choise.yes.clicked.connect(self.deleteRecipe)

    def deleteRecipe(self):
        query.deleteTable(self.selectedCell)
        self.tableRecipes.cellClicked.connect(self.choose)
        self.choise.close()
        self.printRecipes()
        self.clean()

    def checkExistsRecipesInDb(self, *args):
        if len(args) == 1:
            tab = args[0]
            ques = query.exists(tab)
            if ques != 1 and tab == " ":
                # print("nie dodano")
                return 1
            elif ques:
                # print("Jest już w bazie")
                return 1
            else:
                # print("Nie ma w bazie")
                # self.differencesRecipes.append(tab)
                return 0
                # self.choice.yes.clicked.connect(self.

    def checkExistsDataInDb(self, *args):
        if len(args) == 3:
            tab = args[0]
            item = args[1]
            quan = args[2]
            rows = query.count(tab)
            for i in range(rows):
                ques = query.exists(tab, item, quan)
                if ques != 1 and tab == " ":
                    # print("nie dodano")
                    return 1
                elif ques:
                    # print("Jest już w bazie")
                    return 1
                else:
                    print("Nie ma w bazie")
                    # self.differencesRecipes.append(tab)
                    return 0

class AppWindow(form3, base3):

    def __init__(self):
        super(base3, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Piekarnia")

    def accept(self):
        self.close()

    def reject(self):
        self.close()

    def printRecipes(self):
        rows = query.count("tabele")
        self.tableRecipes.setRowCount(rows + 5)
        # self.tableRecipes.setColumnCount(1)
        # max = rows + 5
        if rows < 13:
            self.tableRecipes.setRowCount(13)
            max = 13
        else:
            self.tableRecipes.setRowCount(rows + 4)
            max = rows + 4
        for i in range(max):
            if i < rows:
                col = query.read("tabele", i + 1)
                item = str(col)
                self.tableRecipes.setItem(i, 0, QTableWidgetItem(item))
            else:
                self.tableRecipes.setItem(i, 0, QTableWidgetItem(" "))

    def printData(self):
        tab = self.selectedCell
        self.label.setText(tab)
        tab = str(tab)
        rows = query.count(tab)
        self.readDataFromDb(tab)
        if rows < 13:
            self.tableData.setRowCount(13)
            max = 13
        else:
            self.tableData.setRowCount(rows + 4)
            max = rows + 4
        self.tableData.setColumnCount(2)
        self.readDataFromDb(tab)
        for i in range(max):
            if i < rows:
                self.tableData.setItem(i, 0, QTableWidgetItem(self.dataDb[i][0]))
                self.tableData.setItem(i, 1, QTableWidgetItem(self.dataDb[i][1]))
            else:
                self.tableData.setItem(i, 1, QTableWidgetItem(" "))
                self.tableData.setItem(i, 0, QTableWidgetItem(" "))


class ChoiceWindow(form4, base4):
    switchWindow = QtCore.pyqtSignal()

    def __init__(self):
        super(base4, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Piekarnia")
        self.yes.clicked.connect(self.accept)
        self.no.clicked.connect(self.reject)

    def question(self, text):
        self.label.setText(text)

    def accept(self):
        self.close()
        self.question("")
        # self.yes.clicked.connect("")

    def rejected(self):
        self.close()
        self.question("")
        # self.no.clicked.connect("")

def main():
    # print(query.read("tabele"))
    myApp = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(myApp.exec_())
    query.disconnect()


main()
