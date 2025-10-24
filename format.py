# Reserved Characters:
# @, ^, +

# TLS. Tagged Link Storage

import tkinter as tk
import pandas as pd

buildVersion = "0.3.1"

class LiveData:
    def __init__(self, rawTxt: str):
        self.path = ""
        self.fileVersion = ""
        self.name = ""
        self.data = []
        self.playlists = []
        textArray = rawTxt.splitlines()
        # Mode is the section of the file you are in
        mode = "NONE"
        # Increment represents the position within a section
        increment = 0
        for line in textArray:
            # print(line)
            # print(increment)
            # Mode switch and increment reset upon seeing the @ symbol
            if line[0] == "@":
                mode = line[1:]
                increment = 0
                #print("switching to " + mode)
            # Executes mode
            match mode:
                case "META":
                    match increment:
                        case 1:
                            self.fileVersion = line
                        case 2:
                            self.name = line
                case "MAIN":
                    if not increment == 0:
                        self.data.append(line)
                case "PLAYLISTS":
                    if not increment == 0:
                        self.playlists.append(line)
                case "FINAL":
                    break
            increment = increment + 1
    
    # Returns a requested collumn of data
    def select(self, col: int):
        output = []
        for line in self.data:
            output.append(line.split("^")[col])
        return output
    
    # Returns a requested collumn of unique data sorted alphebetically
    def uniqueSelect(self, col: int):
        output = []
        for line in self.data:
            targetList = line.split("^")[col]
            for target in targetList.split("+"):
                if not (target in output):
                    output.append(target)
        return sorted(output)
    
    # Returns data lines that meet a condition
    def filterAuthor(self, target: str):
        output = []
        for line in self.data:
            authors = line.split("^")[3].split("+")
            if target in authors:
                output.append(line)
        return output
    
    def filterTag(self, target: str):
        output = []
        for line in self.data:
            tags = line.split("^")[4].split("+")
            if target in tags:
                output.append(line)
        return output
    
    def getAll(self):
        return self.data
    
    def displayTo(self, entryList: list, lb: tk.Listbox):
        lb.delete(0, tk.END)
        for entry in entryList:
            breakdown = entry.split("^")
            authors = breakdown[3].replace("+", ", ")
            tags = breakdown[4].replace("+", ", ")
            out = breakdown[0] + ": " + breakdown[2] + " | " + authors + " | " + tags
            lb.insert(tk.END, out)

    def getDataByID(self, id: str):
        for line in self.data:
            if line.split("^")[0] == id:
                return line
        return "INVALID ID"
    
    def getIndexOfData(self, id: str):
        index = 0
        for line in self.data:
            if line.split("^")[0] == id:
                return index
            else:
                index = index + 1
        return index
    
    # Finds the next available ID, useful for filling in gaps after entry deletion
    def freeID(self):
        activeIDs = []
        for entry in self.data:
            eID = int(entry.split("^")[0])
            activeIDs.append(eID)
        currentCheck = 1
        searching = True
        while searching:
            if currentCheck in activeIDs:
                currentCheck = currentCheck + 1
            else:
                searching = False
                return currentCheck
            
    def addEntry(self, new: str):
        self.data.append(new)

    def replaceEntry(self, index: int, new: str):
        self.data[index] = new

    def deleteEntry(self, index: int):
        del self.data[index]

    def compileTLS(self):
        output = ""
        output = output + "@META" + "\n"
        output = output + buildVersion + "\n"
        output = output + self.name + "\n"
        output = output + "@MAIN" + "\n"
        for line in self.data:
            output = output + line + "\n"
        output = output + "@PLAYLISTS" + "\n"
        for pl in self.playlists:
            output = output + pl + "\n"
        output = output + "@FINAL"
        return output
    
    def registerPath(self, path: str):
        self.path = path

    def compileDataFrame(self):
        data = {
            "ID": self.select(0),
            "URL": self.select(1),
            "Name": self.select(2),
            "Authors": self.select(3),
            "Tags": self.select(4)
        }
        df = pd.DataFrame(data)

        return df

    def debug(self):
        print(self.path)
        print(self.fileVersion)
        print(self.name)
        print(self.data)
        print(self.playlists)