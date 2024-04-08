from tkinter import *
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
import requests, sys, bs4, os, lxml, time, img2pdf, threading, multiprocessing

mangalist = []
dest = ""
imgdir = ""
# mangaselection = ""
# ENDCHP: int = 0
# STARTCHP: int = 0

mainwin = Tk()
mainwin.title("Download Manga GUI")
mainwin.geometry('500x500')
def search():
    global manganamelist, mangalist
    mangalist = []
    manganamelist = []
    listvar.set([])
    qry = getquery(inp.get())
    getmangaurl(query= qry)
    manganamelist = [mangalist[i][0] for i in range(len(mangalist))]
    listvar.set(manganamelist)

def reset():
    global manganamelist, mangalist
    mangalist = []
    manganamelist = []
    listvar.set([])
    progress_bar.stop()
    inp.set(init_name)
    startchp.set(0)
    endchp.set(0)
    download_label.place_forget()
    progress_bar.place_forget()
    download_b.place(x= 250, y= 400, anchor= 'n')

def th():
    for i in range(startchp.get(), endchp.get() + 1):
        time.sleep(1)
        download_label.config(text= f"Downloading {mangalist[mangalistbox.curselection()[0]][0]} Chapter {i}...")
        downloadManga(mangalist[mangalistbox.curselection()[0]][2], mangalist[mangalistbox.curselection()[0]][0], i)
        progress_bar.step((100/(endchp.get() - startchp.get() + 1))-0.1)
    download_label.config(text= f"{(endchp.get() - startchp.get() + 1)} Chapters downloaded.")
    for stuff in stuff_to_disable:
        stuff.config(state= 'normal')

def download():
    if mangalist == []:
        # t = Tk()
        # Label(t, text= "Enter manga name", font= ("Arial", 13)).pack()
        messagebox.showwarning(title="Warning", message= "Enter a valid manga name")
        
    elif mangalistbox.curselection() == ():
        messagebox.showwarning(title="Warning", message= "Select a manga")
    else:
        try:
            startchp.get()
            endchp.get()
            if decide(startchp.get(), endchp.get()) == 'error':
                
                pass
            elif startchp.get() == 0 and endchp.get() == 0:
                messagebox.showwarning(title="Warning", message= "Invalid Chapter no")
                
            elif dest == "" or imgdir == "":
                #print(dest, imgdir)
                messagebox.showwarning(title="Warning", message= "Select appropriate folders")
                
            else:
                for stuff in stuff_to_disable:
                    stuff.config(state = 'disabled')
                download_b.place_forget()
                download_label.place(x= 200, y= 400, anchor= 'center')
                progress_bar.place(x= 250, y= 420, anchor= 'n')
                threading.Thread(target= th).start()
                opendir_b.place(x= 380, y= 420) 

        except:
            messagebox.showwarning(title="Warning", message= "Invalid Chapter no")
            
        

def selectdirdest(labelname, text):
    global dest
    arg = filedialog.askdirectory()
    dest = arg
    if arg != "":
        labelname.config(text= arg)
    else:
        labelname.config(text= text)

def selectdirimg(labelname, text):
    global imgdir
    arg = filedialog.askdirectory()
    imgdir = arg
    if arg != "":
        labelname.config(text= arg)
    else:
        labelname.config(text= text)
        
def search_state(*args):
    if init_name == inp.get():
        search_b.config(state= 'disabled')
    elif name_box.get() == '':
        search_b.config(state= 'disabled')
    else:
        search_b.config(state= 'active')

def decide(a, b):
    if a == b:
        return 'single'
    elif a > b:
        messagebox.showwarning(title="Warning", message= "Invalid sequence of chapters")
        return 'error'
    else:
        return 'multiple'

def getquery(args):
    q = ''
    arg = args.split(" ")
    for c in arg:
        q += c
        q += "%20"
    return q

def getmangaurl(query):
    res = requests.get(f'{queryurl}{query}')
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    for i in range(1, 13):
        try:
            mangaurl = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > h3 > a')[0].attrs['href']
            chpurl = f"https://ww7.mangakakalot.tv/chapter{mangaurl[6:]}/chapter-"
            manganame = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > h3 > a')[0].getText()
            #temp = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > em:nth-child(2) > a')[0].attrs['title'].split(" ")
            try:    
                temp = str(soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > span:nth-child(4)')[0]).split()
                auth = ''
                for c in temp[2:]:
                    if c == "</span>":
                        break
                    else:
                        auth += c
                        auth += " "
                lastup = soup.select(f'body > div.container > div.main-wrapper > div.leftCol > div.daily-update > div > div:nth-child({i}) > div > span:nth-child(5)')[0].getText().lstrip("Updated : ")
            except:
                auth = "N/A"
                lastup = "N/A"
            mangalist.append([manganame, mangaurl, chpurl])
        except:
            break
    
def downImg(i, src):
    req = requests.get(src)
    with open(f"{imgdir}/{i+1}.abc", "wb") as f:
        f.write(req.content)

def downloadpages(url):
    threads = []
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'lxml')
    img = soup.select('#vungdoc > img')
    for i in img:
        src = i.attrs['data-src']
        downImgThread = threading.Thread(target= downImg, args= (img.index(i), src))
        threads.append(downImgThread)
        downImgThread.start()
        # print(f"Downloading page no. {img.index(i)+1}...")
        # if i == img[-1]:
        #     print("\n")
    
    for th in threads:
        th.join()

def makepdf(namaiwa):
    directory_path = imgdir
    
    ls = os.listdir(directory_path)
    for j in range(len(ls)):
        for i in range(len(ls) - 1):
            try:
                if int(ls[i].split('.')[0]) > int(ls[i + 1].split('.')[0]):
                    temp = ls[i+1]
                    ls[i+1] = ls[i]
                    ls[i] = temp
            except:
                continue

    with open(f"{dest}/{namaiwa}.pdf", "wb") as file:
        file.write(img2pdf.convert([os.path.join(directory_path, i) for i in ls if i.endswith(".abc")]))
    #print(f"Downloaded {namaiwa}.pdf")

    if openchp.get():
        os.startfile(f"{dest}/{namaiwa}.pdf")

def deleteimg():
    p = imgdir
    for c in os.listdir(p):
        if c.endswith(".abc"):
            os.remove(Path(f"{p}/{c}"))


def downloadManga(curl, name, chpno):
    #print(f"Downloading {name} Chapter {str(chpno)}...")
    downloadpages(curl + str(chpno))
    makepdf(f"{name} Chapter {str(chpno)}")
    deleteimg()

    

init_name = 'Ex: One Piece'
name_label = Label(mainwin, text= "Enter manga name")
name_label.place(x= 250, y= 20, anchor= 'center')

inp = StringVar(value= 'Ex: One Piece')
name_box = Entry(mainwin, textvariable= inp)
name_box.place(x= 250, y= 44, anchor= 'center')
name_box.bind("<Button-1>", lambda e: name_box.delete(0, END))
inp.trace_add('write', search_state)


queryurl = 'https://ww7.mangakakalot.tv/search/'

search_b = Button(mainwin, text= 'Search', command= search, state= 'disabled')
search_b.place(x= 350, y= 44, anchor= 'center')

select_label = Label(mainwin, text= "Select manga you wish to download...")
select_label.place(x= 150, y= 60)

manganamelist = []
listvar = StringVar(value= manganamelist)
mangalistbox = Listbox(mainwin, height= 10, width= 47, listvariable= listvar)
mangalistbox.place(x= 250, y= 80, anchor= 'n')

download_label = Label(mainwin, text= "Download Chapter")
download_label.place(x= 100, y= 250)

startchp = IntVar() 
startchp_box = Entry(mainwin, textvariable= startchp, width= 5)
startchp_box.place(x= 227, y= 253, anchor= 'n')
#startchp_box.bind("<Button-1>", lambda e: startchp_box.delete(0, END))

to_label = Label(mainwin, text= 'to Chapter')
to_label.place(x= 250, y= 250)

endchp = IntVar() 
endchp_box = Entry(mainwin, textvariable= endchp, width= 5)
endchp_box.place(x= 332, y= 253, anchor= 'n')
#endchp_box.bind("<Button-1>", lambda e: endchp_box.delete(0, END))

openchp = IntVar()
openchp_box = Checkbutton(mainwin, text= "Open chapters as soon as they finish downloading?", variable= openchp)
openchp_box.place(x= 230, y= 275, anchor= 'n')

dir_label_text = "Select folder to save manga."
dir_label = Label(mainwin, text= dir_label_text)
dir_label.place(x= 100, y= 310)

dirbrowse_b = Button(mainwin, text= "Browse", command= lambda: selectdirdest(dir_label, dir_label_text))
dirbrowse_b.place(x= 330, y= 310)

img_label_text = "Select folder to save downloaded images,\n these will be deleted when program closes."
img_label = Label(mainwin, text= img_label_text)
img_label.place(x= 80, y= 340)

imgbrowse_b = Button(mainwin, text= "Browse", command= lambda: selectdirimg(img_label, img_label_text))
imgbrowse_b.place(x= 330, y= 340)

download_b = Button(mainwin, text= 'Download', command= download)
download_b.place(x= 250, y= 400, anchor= 'n')

download_label = Label(mainwin, text= "Downloading")

progress_bar = ttk.Progressbar(mainwin, length= 200, mode= 'determinate')

ph = PhotoImage(file= "./folder.png")
opendir_b = Button(mainwin, image= ph, command= lambda: os.startfile(dest))


quit_b = Button(mainwin, text= "Quit", width= 6, command= sys.exit)
quit_b.place(x= 430, y= 465)

reset_b = Button(mainwin, text= "Reset", width= 6, command= reset)
reset_b.place(x= 20, y= 465)

cred = Label(mainwin, text= "Made by QuXnt", font= ("Georgia", 12))                         #Author
cred.place(x= 190, y= 470)

stuff_to_disable = [name_box, search_b, mangalistbox, openchp_box, startchp_box, endchp_box, dirbrowse_b, imgbrowse_b, reset_b]



mainwin.mainloop()