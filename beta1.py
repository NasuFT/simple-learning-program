from tkinter import *
from tkinter.messagebox import *
from tkinter import filedialog

import sqlite3, os, webbrowser

APPLICATION_NAME = "APP"
app = None

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "data/file.db"))
c = conn.cursor()

class Application(Frame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.parent.resizable(width = True, height = True)

        self.editor = None
        self.appEditor = None

        self.buttonRows = []
        self.frameWindow = 0
        self.isEditorActive = 0
        self.buttonValues = None
        self.checkBoxes = []
        self.checkBoxesState = []
        self.buttonMaster = []
        self.buttonMaster.append(0)
        self.buttonIDs = []
                
        self.createconnection()
        self.initializeFrame()
        
    def initializeFrame(self):
        self.iterationRow = 0

        self.create_widgets()

    def createconnection(self):
        c.execute("create table if not exists buttons (buttonKey int primary key not null, buttonWindow int not null, buttonText text, buttonMaster int not null, buttonHTML text, isBackKey int not null, isEditorKey int not null)")

    def create_widgets(self):
        c.execute("SELECT buttonKey FROM buttons WHERE buttonWindow = ? and isBackKey = 1",
                  (self.frameWindow, ))
        backKeys = c.fetchall()

        if not backKeys:
            c.execute("INSERT INTO buttons (buttonWindow, buttonText, buttonMaster, buttonHTML, isBackKey, isEditorKey) VALUES (?, ?, 0, ?, 1, 0)",
                      (self.frameWindow, "Back", None))
        
        c.execute("SELECT buttonText, buttonKey, buttonHTML, isBackKey, isEditorKey FROM buttons WHERE buttonWindow=? and (buttonMaster=? or buttonMaster=0)",
                  (self.frameWindow, self.buttonMaster[len(self.buttonMaster) - 1]))
        self.buttonValues = c.fetchall()
    
        for row in self.buttonValues:
            if(row[3] != 1 and row[4] != 1):
                self.buttonRows.append(Button(self, text = row[0], command = lambda buttonKey = row[1], buttonHTML = row[2], isBackKey = row[3], isEditorKey = row[4]:
                                          self.buttonCheck(buttonKey, buttonHTML, isBackKey, isEditorKey)))
                self.buttonRows[self.iterationRow].grid(column = 0, row = self.iterationRow, padx = (0, 5), pady = (0, 5), sticky= 'nswe')
                self.buttonIDs.append(row[1])
                self.iterationRow += 1
                
        for row in self.buttonValues:
            if(row[4] == 1 or row[3] == 1):
                self.buttonRows.append(Button(self, text = row[0], command = lambda buttonKey = row[1], buttonHTML = row[2], isBackKey = row[3], isEditorKey = row[4]:
                                          self.buttonCheck(buttonKey, buttonHTML, isBackKey, isEditorKey)))
                self.buttonRows[self.iterationRow].grid(column = 0, row = self.iterationRow, padx = (0, 5), pady = (0, 5), sticky= 'nswe')
                self.iterationRow += 1

        if(self.isEditorActive == 1):
                self.addButtonChecks()
        
        self.setWeight(self.iterationRow)

    def addButtonChecks(self):
        for row in self.buttonValues:
            if(row[3] != 1 and row[4] != 1):
                self.checkBoxesState.append(IntVar())
                self.checkBoxes.append(Checkbutton(self, variable = self.checkBoxesState[len(self.checkBoxesState) - 1]))
                self.checkBoxes[len(self.checkBoxes) - 1].grid(column = 1, row = len(self.checkBoxes) - 1, padx = (0, 5), pady = (0, 5))
        for row in self.buttonValues:
            if(row[3] == 1 or row[4] == 1):
                self.checkBoxesState.append(IntVar())
                self.checkBoxes.append(Checkbutton(self, variable = self.checkBoxesState[len(self.checkBoxesState) - 1]))
                self.checkBoxes[len(self.checkBoxes) - 1].grid(column = 1, row = len(self.checkBoxes) - 1, padx = (0, 5), pady = (0, 5))
                self.checkBoxes[len(self.checkBoxes) - 1].config(state=DISABLED)

    def buttonCheck(self, buttonKey = 0, buttonHTML = None, isBackKey = 0, isEditorKey = 0):
        if(isBackKey == 1):
            self.frameWindow -= 1

            if(self.frameWindow >= 0):
                self.buttonMaster.pop()

                self.windowChange()
            else:
                self.terminate()
        elif(isEditorKey == 1):
            if(self.isEditorActive == 1):
                showerror("Error!", "Editor already open!")
            else:
                self.editor = Toplevel()
                self.editor.minsize(width = 200, height = 200)
                self.editor.protocol("WM_DELETE_WINDOW", self.editorCloseEvent)
                self.isEditorActive = 1
                self.appEditor = Editor(parent=self.editor)
                self.appEditor.pack(fill = "both", expand = True)
        else:
            if(buttonHTML != None):
                webbrowser.open(buttonHTML, new = 2)
            else:
                self.buttonMaster.append(buttonKey)
                self.frameWindow += 1

                self.windowChange()

    def clearCheckBoxes(self):
        for i in range(len(self.checkBoxes)):
            self.checkBoxes[i].destroy()

        del self.checkBoxes[:]
        del self.checkBoxesState[:]

    def editorCloseEvent(self):
        result = askokcancel(APPLICATION_NAME, "Would you like to quit the editor and save your data?")
        if(result == True):
            conn.commit()
            app.windowChange()
        else:
            conn.rollback()
            app.windowChange()
        
        self.clearCheckBoxes()
        
        self.isEditorActive = 0
        self.editor.destroy()
                
    def windowChange(self):
        for i in range(len(self.buttonRows)):
            self.buttonRows[i].destroy()

        del self.buttonRows[:]

        if(self.isEditorActive == 1):
            self.clearCheckBoxes()

        del self.buttonIDs[:]

        self.initializeFrame()
        
    def setWeight(self, iterationRow = None):
        counter = 0
        
        while(counter < iterationRow):
            self.rowconfigure(counter, weight = 1)
            counter += 1

        self.columnconfigure(0, weight = 1)

    def terminate(self):
        conn.close()
        
        self.parent.destroy()

class Editor(Frame):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.parent.resizable(width = False, height = False)

        self.buttonRows = []
        self.iterationRow = 0

        self.checkBoxesList = []

        self.addCheckBoxes()
        self.create_widgets()

    def create_widgets(self):
        c.execute("SELECT editorButtonKey, editorButtonText FROM editor")
        buttonValues = c.fetchall()

        for row in buttonValues:
            self.buttonRows.append(Button(self, text = row[1], command = lambda buttonKey = row[0] :self.checkButton(buttonKey)))
            self.buttonRows[self.iterationRow].grid(column = 0, row = self.iterationRow, padx = (0, 5), pady = (0, 5), sticky = "news")
            self.iterationRow += 1

        self.setWeight(self.iterationRow)

    def checkButton(self, buttonKey = None):
        if(buttonKey == 1):
            self.ClassDialogBox = Toplevel()
            self.ClassDialogBox.minsize(width = 200, height = 200)
            self.ClassDialogBox.protocol("WM_DELETE_WINDOW", self.addDialogBoxOnClose)
            self.dialogBox = AddButtonDialogBox(parent=self.ClassDialogBox)
            self.dialogBox.pack(fill = "both", expand = True)
        elif(buttonKey == 2):
            if(any([app.checkBoxesState[i].get() == 1 for i in range(len(app.checkBoxesState))])):
                self.buttonRemoveList = [j for j in range(len(app.checkBoxesState)) if app.checkBoxesState[j].get() == 1]
                self.finalButtonRemoveIDs = []
                for value in self.buttonRemoveList:
                    self.finalButtonRemoveIDs.append(app.buttonIDs[value])

                print(self.finalButtonRemoveIDs)
                for x in self.finalButtonRemoveIDs:
                    c.execute("DELETE FROM buttons WHERE buttonKey = ?", (x,))

                app.windowChange()
                showinfo(APPLICATION_NAME, "Buttons removed.")
            else:
                showerror(APPLICATION_NAME, "No buttons selected!")
            
        elif(buttonKey == 3):
            app.editorCloseEvent()

    def addDialogBoxOnClose(self):
        self.ClassDialogBox.destroy()
    
    def setWeight(self, iterationRow = None):
        counter = 0
        
        while(counter < iterationRow):
            self.rowconfigure(counter, weight = 1)
            counter += 1

        self.columnconfigure(0, weight = 1)
    
    def addCheckBoxes(self):
        app.addButtonChecks()

class AddButtonDialogBox(Frame):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.parent.resizable(width = False, height = False)

        self.cb = None
        self.cbState = IntVar()
        self.link = None
        self.bb = None
        self.eb = None

        self.checkAdd()
        self.setWeight()

        self.grab_set()

    def checkAdd(self):
        Label(self, text = "Text").grid(row = 0, column = 0, sticky = "news", padx = (0, 5), pady = (0, 5))
        self.eb = Entry(self)
        self.eb.grid(row = 0, column = 1, columnspan = 2, sticky = "news", padx = (0, 5), pady = (0, 5))

        self.bb = Button(self, text = "HTML File", command = lambda:self.openFileDialog(), state = DISABLED)
        self.bb.grid(row = 1, column = 1, sticky = "news", padx = (0, 5), pady = (0, 5))

        self.cb = Checkbutton(self, variable = self.cbState, text = "Link to HTML?", command = self.checkButtonReverse)
        self.cb.grid(row = 1, column = 0, sticky = "w", padx = (0, 5), pady = (0, 5))
        
        Button(self, text = "OK", command = lambda:self.okButton()).grid(row = 2, sticky = "news", padx = (0, 5), pady = (0, 5))        
        Button(self, text = "Cancel", command = lambda:self.parent.destroy()).grid(row = 2, column = 1, sticky = "news", padx = (0, 5), pady = (0, 5))

    def okButton(self):
        c.execute("INSERT INTO buttons (buttonWindow, buttonText, buttonMaster, buttonHTML, isBackKey, isEditorKey) VALUES (?, ?, ?, ?, 0, 0)",
                  (app.frameWindow, self.eb.get(), app.buttonMaster[len(app.buttonMaster) - 1], self.link))
        self.parent.destroy()
        app.windowChange()

    def checkButtonReverse(self):
        if(self.cbState.get() == 1):
            self.bb.config(state = NORMAL)
        else:
            self.bb.config(state = DISABLED)

    def openFileDialog(self):
        self.link = filedialog.asksaveasfilename(initialdir = "C:\\", title = "Select HTML File", filetypes = (("HTML File (*.html)", "*.html"),))

    def setWeight(self):
        for i in range(0, 2):
            self.rowconfigure(i, weight = 1)

        for j in range(0, 1):
            self.columnconfigure(j, weight = 1)

def main():
    root = Tk()
    global app
    app = Application(parent=root)
    root.minsize(width = 200, height = 200)
    root.protocol("WM_DELETE_WINDOW", app.terminate)
    app.pack(fill="both", expand=True)
    app.mainloop()
    
if __name__ == '__main__':
    main()
