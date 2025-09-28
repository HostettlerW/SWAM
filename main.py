import tkinter as tk
from tkinter import filedialog
from format import LiveData
import pyperclip
import os, sys


buildVersion = "0.3.0"

# Will Hostettler

# Please forgive my spagetti code.

# Code for executable path adjustment
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

root = tk.Tk()
root.geometry("300x300")
# Searchable Web Address Management
root.title("SWAM")

logo = tk.PhotoImage(file=resource_path("logo.png"))
logoLabel = tk.Label(root, image=logo)
logoLabel.pack()

instr = tk.Label(root, text="Load a TLS file to start.")
instr.pack()

def startApp(ld: LiveData):
    app = tk.Toplevel(root)
    app.title(ld.name)
    app.geometry("600x600")

    scrollbar = tk.Scrollbar(app)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    view = tk.Listbox(app, yscrollcommand=scrollbar.set)
    view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    menu = tk.Menu(app)
    app.config(menu=menu)

    def allEntries():
        data = ld.getAll()
        ld.displayTo(data, view)

    def saveFile():
        fileData = ld.compileTLS()
        with open(ld.path, "w") as file:
            file.write(fileData)
    
    def makeCSV():
        df = ld.compileDataFrame()
        filepath = tk.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
    
        # If a path was selected, create the file
        if filepath:
            df.to_csv(filepath, index=False, header=True)

    fileMenu = tk.Menu(menu)
    menu.add_cascade(label='File', menu=fileMenu)
    fileMenu.add_command(label='Save', command=saveFile)
    fileMenu.add_command(label='Export to CSV', command=makeCSV)

    def createNew():
        create = tk.Toplevel(app)
        create.title("Create New")
        create.geometry("250x200")
        idStr = str(ld.freeID())
        tk.Label(create, text='URL: ').grid(row=0)
        e1 = tk.Entry(create)
        e1.grid(row=0, column=1)
        tk.Label(create, text='Name: ').grid(row=1)
        e2 = tk.Entry(create)
        e2.grid(row=1, column=1)
        tk.Label(create, text='Author(s): ').grid(row=2)
        e3 = tk.Entry(create)
        e3.grid(row=2, column=1)
        tk.Label(create, text='Tag(s): ').grid(row=3)
        e4 = tk.Entry(create)
        e4.grid(row=3, column=1)
        idExtra = "ID: " + idStr
        tk.Label(create, text=idExtra).grid(row=4)

        def compileEntry():
            output = idStr + "^" + e1.get() + "^" + e2.get() + "^" + e3.get() + "^" + e4.get()
            ld.addEntry(output)
            allEntries()
            create.destroy()

        tk.Button(create, text="Save", command=compileEntry).grid(row=5, column=1)

        create.mainloop()

    def editEntry():
        selected_indices = view.curselection()
        if selected_indices:
            selected_item = view.get(selected_indices[0])
            itemID = selected_item.split(":")[0]
            dataLine = ld.getDataByID(itemID)

            create = tk.Toplevel(app)
            create.title("Edit")
            create.geometry("250x200")

            tk.Label(create, text='URL: ').grid(row=0)
            e1 = tk.Entry(create)
            e1.insert(0, dataLine.split("^")[1])
            e1.grid(row=0, column=1)
            tk.Label(create, text='Name: ').grid(row=1)
            e2 = tk.Entry(create)
            e2.insert(0, dataLine.split("^")[2])
            e2.grid(row=1, column=1)
            tk.Label(create, text='Author(s): ').grid(row=2)
            e3 = tk.Entry(create)
            e3.insert(0, dataLine.split("^")[3])
            e3.grid(row=2, column=1)
            tk.Label(create, text='Tag(s): ').grid(row=3)
            e4 = tk.Entry(create)
            e4.insert(0, dataLine.split("^")[4])
            e4.grid(row=3, column=1)
            idExtra = "ID: " + dataLine.split("^")[0]
            tk.Label(create, text=idExtra).grid(row=4)

            def compileEntry():
                output = dataLine.split("^")[0] + "^" + e1.get() + "^" + e2.get() + "^" + e3.get() + "^" + e4.get()
                index = ld.getIndexOfData(dataLine.split("^")[0])
                ld.replaceEntry(index, output)
                allEntries()
                create.destroy()

            tk.Button(create, text="Save", command=compileEntry).grid(row=5, column=1)

            create.mainloop()

    def copyLink():
        selected_indices = view.curselection()
        if selected_indices:
            selected_item = view.get(selected_indices[0])
            itemID = selected_item.split(":")[0]
            dataLine = ld.getDataByID(itemID)
            pyperclip.copy(dataLine.split("^")[1])

    def delete():
        selected_indices = view.curselection()
        if selected_indices:
            selected_item = view.get(selected_indices[0])
            itemID = selected_item.split(":")[0]
            dataIndex = ld.getIndexOfData(itemID)
            ld.deleteEntry(dataIndex)
            allEntries()

    def addToPlaylist():
        selected_indices = view.curselection()
        if selected_indices:
            selected_item = view.get(selected_indices[0])
            itemID = selected_item.split(":")[0]

            find = tk.Toplevel(app)
            find.title("Playlists")
            find.geometry("250x300")

            select = tk.Button(find, text="Add")
            select.pack()

            scrollbar2 = tk.Scrollbar(find)
            scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

            view2 = tk.Listbox(find, yscrollcommand=scrollbar2.set)
            view2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            for pl in ld.playlists:
                if pl[-1] == "^":
                    vids = 0
                else:
                    vids = len(pl.split("^")[1].split("+"))
                item = pl.split("^")[0] + ". | " + str(vids) + " Items"
                view2.insert(tk.END, item)

            def selectClick():
                nonlocal itemID
                selected_indices = view2.curselection()
                if selected_indices:
                    # The goal here is to take the edited data sent to the listbox, and reverse it back into a full playlist code
                    selected_item = view2.get(selected_indices[0])
                    name = selected_item.split(".")[0]

                    nameList = []
                    for pl in ld.playlists:
                        nameList.append(pl.split("^")[0])

                    index = nameList.index(name)
                    playlist = ld.playlists[index]

                    if not (playlist[-1] == "^"):
                        playlist = playlist + "+" + str(itemID)
                    else:
                        playlist = playlist + str(itemID)
                    ld.playlists[index] = playlist
                    find.destroy()
            
            select.config(command=selectClick)

            find.mainloop()

    def newPlaylist():
        newPL = tk.Toplevel(app)
        newPL.title("Create New Playlist")
        newPL.geometry("300x100")
        tk.Label(newPL, text='Playlist Name: ').grid(row=0)
        e1 = tk.Entry(newPL)
        e1.grid(row=0, column=1)

        def create():
            name = e1.get()
            ld.playlists.append(name + "^")
            newPL.destroy()

        tk.Button(newPL, text="Create", command=create).grid(row=1, column=1)
        newPL.mainloop()

    def delFromPlaylist():
        selected_indices = view.curselection()
        if selected_indices:
            selected_item = view.get(selected_indices[0])
            itemID = selected_item.split(":")[0]

            # Finds all playlists itemID is a part of
            activeLists = []
            for pl in ld.playlists:
                videos = pl.split("^")[1].split("+")
                if itemID in videos:
                    activeLists.append(pl)

            if not (len(activeLists) == 0):
                find = tk.Toplevel(app)
                find.title("Connected Playlists")
                find.geometry("250x300")

                select = tk.Button(find, text="Remove From...")
                select.pack()

                scrollbar2 = tk.Scrollbar(find)
                scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

                view2 = tk.Listbox(find, yscrollcommand=scrollbar2.set)
                view2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                for pl in activeLists:
                    if pl[-1] == "^":
                        vids = 0
                    else:
                        vids = len(pl.split("^")[1].split("+"))
                    item = pl.split("^")[0] + ". | " + str(vids) + " Items"
                    view2.insert(tk.END, item)

                def purge():
                    nonlocal itemID
                    selected_indices = view2.curselection()
                    if selected_indices:
                        selected_item = view2.get(selected_indices[0])
                        name = selected_item.split(".")[0]

                        nameList = []
                        for pl in ld.playlists:
                            nameList.append(pl.split("^")[0])

                        index = nameList.index(name)
                        playlist = ld.playlists[index]

                        # Break down videos into a list then removes the ID
                        videos = playlist.split("^")[1].split("+")
                        videos = [i for i in videos if i != itemID]

                        rebuild = ""
                        for vid in videos:
                            if rebuild == "":
                                rebuild = str(vid)
                            else:
                                rebuild = rebuild + "+" + str(vid)

                        playlist = playlist.split("^")[0] + "^" + rebuild

                        ld.playlists[index] = playlist
                        find.destroy()

                select.config(command=purge)
                find.mainloop()

    entryMenu = tk.Menu(menu)
    menu.add_cascade(label='Entry', menu=entryMenu)
    entryMenu.add_command(label='Create New', command=createNew)
    entryMenu.add_command(label='Copy Link', command=copyLink)
    entryMenu.add_command(label='Edit', command=editEntry)
    entryMenu.add_command(label='Delete', command=delete)

    plMenu = tk.Menu(menu)
    menu.add_cascade(label='Playlist', menu=plMenu)

    plMenu.add_command(label='New Playlist', command=newPlaylist)
    plMenu.add_command(label='Add To Playlist...', command=addToPlaylist)
    plMenu.add_command(label='Delete From Playlist...', command=delFromPlaylist)

    def viewAuthor():
        find = tk.Toplevel(app)
        find.title("View Author")
        find.geometry("200x300")

        select = tk.Button(find, text="Select")
        select.pack()

        scrollbar2 = tk.Scrollbar(find)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

        view2 = tk.Listbox(find, yscrollcommand=scrollbar2.set)
        view2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        data = ld.uniqueSelect(3)
        for item in data:
            view2.insert(tk.END, item)

        def selectClick():
            selected_indices = view2.curselection()
            if selected_indices:
                selected_item = view2.get(selected_indices[0])
                data = ld.filterAuthor(selected_item)
                ld.displayTo(data, view)
                find.destroy()
        
        select.config(command=selectClick)

        find.mainloop()

    def viewTag():
        find = tk.Toplevel(app)
        find.title("View Tag")
        find.geometry("200x300")

        select = tk.Button(find, text="Select")
        select.pack()

        scrollbar2 = tk.Scrollbar(find)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

        view2 = tk.Listbox(find, yscrollcommand=scrollbar2.set)
        view2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        data = ld.uniqueSelect(4)
        for item in data:
            view2.insert(tk.END, item)

        def selectClick():
            selected_indices = view2.curselection()
            if selected_indices:
                selected_item = view2.get(selected_indices[0])
                data = ld.filterTag(selected_item)
                ld.displayTo(data, view)
                find.destroy()
        
        select.config(command=selectClick)

        find.mainloop()

    def viewPlaylists():
        find = tk.Toplevel(app)
        find.title("Playlists")
        find.geometry("200x300")

        select = tk.Button(find, text="Select")
        select.pack()

        scrollbar2 = tk.Scrollbar(find)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)

        view2 = tk.Listbox(find, yscrollcommand=scrollbar2.set)
        view2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for pl in ld.playlists:
            if pl[-1] == "^":
                vids = 0
            else:
                vids = len(pl.split("^")[1].split("+"))
            print(pl.split("^")[1].split("+"))
            item = pl.split("^")[0] + ". | " + str(vids) + " Items"
            view2.insert(tk.END, item)

        def selectClick():
            selected_indices = view2.curselection()
            if selected_indices and (vids > 0):
                # The goal here is to take the edited data sent to the listbox, and reverse it back into a full playlist code
                selected_item = view2.get(selected_indices[0])
                name = selected_item.split(".")[0]

                nameList = []
                for pl in ld.playlists:
                    nameList.append(pl.split("^")[0])

                index = nameList.index(name)
                playlist = ld.playlists[index]

                data = []
                for id in playlist.split("^")[1].split("+"):
                    data.append(ld.getDataByID(id))
                ld.displayTo(data, view)
                find.destroy()
        
        select.config(command=selectClick)

        find.mainloop()


    viewMenu = tk.Menu(menu)
    menu.add_cascade(label='View', menu=viewMenu)
    viewMenu.add_command(label='All Entries', command=allEntries)
    viewMenu.add_command(label='View Author', command=viewAuthor)
    viewMenu.add_command(label='View Tag', command=viewTag)
    viewMenu.add_command(label='View Playlists', command=viewPlaylists)

    def analyzeAuthors():
        output = ""
        authors = ld.uniqueSelect(3)
        for author in authors:
            count = 0
            for entry in ld.data:
                if author in entry.split("^")[3].split("+"):
                    count = count + 1
            output = output + author + ": " + str(count) + "\n"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")]
        )
        with open(filepath, 'w') as file:
                file.write(output)

    def analyzeTags():
        output = ""
        authors = ld.uniqueSelect(4)
        for author in authors:
            count = 0
            for entry in ld.data:
                if author in entry.split("^")[4].split("+"):
                    count = count + 1
            output = output + author + ": " + str(count) + "\n"
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt")]
        )
        with open(filepath, 'w') as file:
                file.write(output)

    aMenu = tk.Menu(menu)
    menu.add_cascade(label='Analytics', menu=aMenu)
    aMenu.add_command(label='Authors', command=analyzeAuthors)
    aMenu.add_command(label='Tags', command=analyzeTags)

    scrollbar.config(command=view.yview)

    view.insert(0,"Online")

    # Default View
    allEntries()
    app.mainloop()

def load():
    filePath = filedialog.askopenfilename(filetypes=[("Tagged Link Storage", "*.tls")])
    try:
        with open(filePath) as file:
            db = LiveData(file.read())
            db.registerPath(filePath)
            startApp(db)
    except Exception as e:
        instr.config(text="Invalid Filepath")
        print(e)

def quickLoad(path: str):
    try:
        with open(path) as file:
            db = LiveData(file.read())
            db.registerPath(path)
            startApp(db)
    except Exception as e:
        instr.config(text="Invalid Filepath")
        print(e)

def createNewTLS():
    filepath = filedialog.asksaveasfilename(
        defaultextension=".tls",
        filetypes=[("Tagged Link Storage", "*.tls")]
    )
    
    # If a path was selected, create the file
    if filepath:

        newFile = tk.Toplevel(root)
        newFile.title("Create New File")
        newFile.geometry("250x100")
        tk.Label(newFile, text='Database Name: ').grid(row=0)
        e1 = tk.Entry(newFile)
        e1.grid(row=0, column=1)

        def writeFile():
            newName = e1.get()
            output = "@META" + "\n"
            output = output + buildVersion + "\n"
            output = output + newName + "\n"
            output = output + "@MAIN" + "\n"
            output = output + "@PLAYLISTS" + "\n"
            output = output + "@FINAL"

            with open(filepath, 'w') as file:
                file.write(output)

            newFile.destroy()
            quickLoad(filepath)
            

        tk.Button(newFile, text="Create", command=writeFile).grid(row=1, column=1)

loadFile = tk.Button(root, text="Load File", command=load)
loadFile.pack()

newFile = tk.Button(root, text="Create New", command=createNewTLS)
newFile.pack()

root.mainloop()