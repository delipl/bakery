import sqlite3


class Query:

    # def __init__(self):

    def __init__(self):
        self.conn = sqlite3.connect('base/piekarnia.db')
        self.c = self.conn.cursor()

    def connect(self):
        pass

    def disconnect(self):
        self.conn.commit
        self.conn.close()

    def save(self):
        self.conn.commit()

    def read(self, *args):
        with self.conn:
            if len(args) == 1 and isinstance(args[0], str):
                tab = args[0]
                tab = str(tab)
                q = "SELECT * FROM "
                q += tab
                self.c.execute(q)
                rows = self.c.fetchall()
                for row in rows:
                    # output = self.c.fetchall()
                    # print(output)
                    print(row)
                self.save()
                return rows

            elif len(args) == 2 and isinstance(args[0], str):
                tab = args[0]
                wie = args[1]
                tab = str(tab)
                wie = str(wie)
                if tab == "tabele":
                    q = "SELECT tabela FROM "
                    q += tab
                    q += " WHERE ID = " + wie
                    self.c.execute(q)
                    item = self.c.fetchone()
                    # print(item)
                    item = self.clean(item)
                    # print(item)
                    return item
                else:
                    q = "SELECT składnik FROM '" + tab + "' WHERE ID = " + wie
                    self.c.execute(q)
                    item = self.c.fetchone()
                    q = "SELECT ilość FROM '" + tab + "' WHERE ID = " + wie
                    self.c.execute(q)

                    quan = self.c.fetchone()
                    item = self.clean(item)
                    quan = str(quan)
                    quan = quan[1:-2]
                    # print(quan)

                    # print(item, quan)
                    return [item, quan]

            elif len(args) == 3 and isinstance(args[0], str):
                tab = args[0]
                kol = args[1]
                wie = args[2]
                tab = str(tab)
                kol = str(kol)
                q = "SELECT " + kol + " FROM '" + tab + "' WHERE ID = " + str(wie) + ";"
                self.c.execute(q)
                output = self.c.fetchall()
                print(output)

    def count(self, tab):
        q = "SELECT COUNT(ID) FROM '" + tab + "';"
        self.c.execute(q)
        rows = self.c.fetchone()
        for row in rows:
            return row

    def selectId(self, tab):
        q = "SELECT ID FROM '" + tab + "';"
        self.c.execute(q)
        rows = self.c.fetchall()
        for i in range(len(rows)):
            rows[i] = str(rows[i])[1:-2]
        #print("rows     ", rows)
        selected = []
        limit = len(rows)
        index = 0
        for i in range(len(rows)):
            if i == 0 and rows[0] == 1:
                selected.append(rows[0])
                index += 1
                continue
            elif i == 0 and rows[0] != 1:
                selected.append("")
                index += 1
                continue
            elif i == limit:
                selected.append(rows[i])
                index += 1
                continue

            for j in range(index + 1, limit+1):
                # print("porównuję...", int(rows[i]), j)
                if int(rows[i]) == j:
                    selected.append(rows[i])
                    break
                else:
                    selected.append("")
                    i -= 1
                    index += 1
                    break
            index += 1
        #print("selected ", selected)
        return selected

    def writeData(self, tab, args):
        with self.conn:
            row = args[:]
            print("row", row)
            ID = []
            skladnik = []
            ilosc = []
            for i in range(len(row)):
                print("actual row", row[i])
                ID.append(row[i][0])
                skladnik.append(row[i][1])
                ilosc.append(row[i][2])
            tab = str(tab)
            for i in range(len(ID)):
                skladnik[i] = str(skladnik[i])
                ilosc[i] = str(ilosc[i])
                print(ilosc[i])
                #ID[i] = str(ID[i])
            for i in ID:
                q = "DELETE FROM '" + tab + "' WHERE ID = " + str(i) + " ;"
                print(q)
                self.c.execute(q)
            print("skladniki i ilosc", skladnik, ilosc)
            for i in range(len(ID)):
                print("jestem w pętli")
                ID[i] = str(ID[i])
                if str(skladnik[i]) == "" or str(ilosc[i]) == "":
                    print("Puste któreś jest")
                    # i -= 1
                    for j in range(i, len(ID)):
                        if ID[j] != "":
                            ID[j] = int(ID[j])
                            ID[j] -= 1
                    continue
                q = "INSERT INTO '" + tab + "' (ID, składnik, ilość) VALUES(" + ID[i] + ", '" + skladnik[i] + "', " + ilosc[i] + ");"

                print(q)
                self.c.execute(q)
            #self.read(tab)
            self.save()

    def writeRecipes(self, send):
        row = send
        ID = []
        recipe = []
        for i in row:
            ID.append(i[0])
            recipe.append(i[1])

    def exists(self, *args):
        if len(args) == 1 and isinstance(args[0], str):
            count = self.ask("SELECT COUNT(tabela) FROM tabele")
            count = self.clean(count)
            name = str(args[0])
            tab = []
            count = int(count)
            for i in range(count):
                q = "SELECT tabela FROM tabele WHERE ID = " + str(i + 1) + " ;"
                tab.append(self.clean(self.ask(q))[1:-1])
            # print(tab)
            for i in tab:
                # print(i, name)
                if i == name:
                    return True
            # print("nie ma takiego")
            return False

        if len(args) == 3 and isinstance(args[0], str) and isinstance(args[1], str):
            tab = args[0]
            item = args[1]
            quan = args[2]
            q = "SELECT Składnik, Ilość FROM '" + tab + "' WHERE (Składnik = '" + item + "' AND Ilość = " + str(quan) + " );"
            data = self.ask(q)

            print("query.exists() data", data)
            rows = self.count(tab)
            for i in range(rows):
                if data[0] == item and data[1] == quan:
                    return 1
            return 0

    def clean(self, data):
        data = str(data)[2:-3]
        return data

    def createTable(self, tab):
        if self.exists(tab) == 0:
            tab = str(tab)
            q = "CREATE TABLE '" + tab + "' ('ID' INTEGER NOT NULL PRIMARY KEY, 'składnik' VARCHAR(100), 'ilość' " \
                                         "VARCHAR(100)) "
            print(q)
            self.ask(q)

            q = "INSERT INTO tabele (tabela) VALUES('" + tab + "')"
            # print(q)
            self.ask(q)
            # self.save()

    def deleteTable(self, tab):
        tab = str(tab)
        q = "DELETE FROM tabele WHERE tabela = '" + tab + "';"
        print(q)
        self.ask(q)
        q = "DROP TABLE '" + tab + "';"
        print(q)
        self.ask(q)
        self.save()

    def ask(self, ask):
        self.c.execute(ask)
        data = self.c.fetchall()
        return data
