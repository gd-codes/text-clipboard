
# Written in Python 3.7.2
# Gautam D
# 3 Mar 2019 - 5 Apr 2019

from pynput.keyboard import *
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import traceback

class Clipboard :
    """Clipboard to keep multiple strings in memory simultaneously, which can be pasted with user-chosen keyboard shortcuts"""

    def __init__(self):
        """Creates main variables and starts the keyboard controller/listener"""
        self.createGUI()
        self.num_items = 0
        self.active_shortcuts = {}
        self.keycombos = {}
        self.texts = {}
        self.pressedkeys = set()
        self.detected = ""

        self.kb = Controller()
        self.listener = Listener(on_press = self.identifyKeyPress, on_release = self.identifyKeyRelease)
        self.listener.start()
        try :
            self.root.mainloop()
        finally :
            self.listener.stop()

    def createGUI(self):
        """Creates the user interface window"""
        self.root = tk.Tk()
        self.root.geometry('725x800')
        self.root.minsize(500,700)
        self.root.title('Clipboard')
        self.root.protocol('WM_DELETE_WINDOW', self.closeWindow)

        self.header = tk.Frame(self.root)
        self.header.pack(pady=10)

        self.logo = tk.PhotoImage(file='./logo120px.png')

        self.logolbl = tk.Label(self.header, image=self.logo)
        self.logolbl.image = self.logo
        self.logolbl.pack(side=tk.LEFT, padx=5, pady=5)
        self.titlelbl = tk.Label(self.header, text='Customisable\nText\nClipboard', font=('American Typewriter', 25, 'bold'))
        self.titlelbl.pack(side=tk.RIGHT, padx=5, pady=5)

        self.infoframe = tk.Frame(self.root)
        self.infoframe.pack(pady=10)

        self.description = tk.Label(self.infoframe, text="Store multiple different text values simultaneously, to paste using custom keyboard shortcuts", font=('Calibri', 11, 'italic'))
        self.description.pack()
        self.helpbtn = tk.Button(self.infoframe, text='How to Use', bg='#cccccc', width=15, font=('American Typewriter', 10, 'bold'), command=self.help)
        self.helpbtn.pack(pady = 5)
        self.instrlbl = tk.Label(self.infoframe, text="Define keyboard shortcuts below : ", font=('Calibri', 12, 'bold'))
        self.instrlbl.pack(pady=10)

        self.defarea = tk.LabelFrame(self.root, text='Clipboard')
        self.defarea.pack(padx=10, pady=10, expand=tk.YES, fill=tk.BOTH)

        self.addnew = tk.Button(self.defarea, text='Add New Shortcut', bg='#333333', fg='#ffffff', width=20, height=2, font=('Calibri', 11, 'bold'), command = self.addNewItem)
        self.addnew.pack(padx=10, pady=10, side=tk.BOTTOM)

        self.scrlframe = tk.Frame(self.defarea)
        self.scrlframe.pack(padx=10, pady=10, side=tk.TOP, expand=tk.YES, fill=tk.BOTH)
        self.scrollarea = tk.Canvas(self.scrlframe, borderwidth=0, bg='white')
        self.scrollarea.grid(column=0, row=0, sticky='NSEW')
        self.main_yscrll = tk.Scrollbar(self.scrlframe, orient=tk.VERTICAL, command=self.scrollarea.yview)
        self.main_yscrll.grid(column=1, row=0, sticky='NS')
        self.main_xscrll = tk.Scrollbar(self.scrlframe, orient=tk.HORIZONTAL, command=self.scrollarea.xview)
        self.main_xscrll.grid(column=0, row=1, sticky='EW')
        self.scrollarea.config(xscrollcommand = self.main_xscrll.set, yscrollcommand = self.main_yscrll.set)
        self.scrollarea.bind_all('<MouseWheel>', self.scrollCanvas)

        self.shortcuts = tk.Frame(self.scrollarea)
        self.scrollarea.bind('<Configure>', self.resizeScrollRegion)
        self.scrollarea.create_window((1,1), window = self.shortcuts, anchor='nw', tags=('TheFrame'))

        self.item_frames = []
        self.item_labels_1 = []
        self.item_labels_2 = []
        self.item_labels_3 = []
        self.item_labels_4 = []
        self.item_keylists_1 = []
        self.item_keyvars_1 = []
        self.item_keylists_2 = []
        self.item_keyvars_2 = []
        self.item_keylists_3 = []
        self.item_keyvars_3 = []
        self.item_contents = []
        self.item_delbtns = []
        self.item_widgets = (self.item_frames, self.item_labels_1, self.item_labels_2, self.item_labels_3, self.item_labels_4, self.item_keylists_1, self.item_keyvars_1,
                             self.item_keylists_2, self.item_keyvars_2, self.item_keylists_3, self.item_keyvars_3, self.item_contents, self.item_delbtns)

        self.saveitem = tk.Button(self.defarea, text='Save', bg='#333333', fg='#ffffff', width=10, height=2, font=('Calibri', 11, 'bold'), command = self.saveItemDetails)

        self.key1opts = ('<NONE>', 'Ctrl', 'Shift', 'Alt')
        self.key2opts = ('<NONE>', 'Ctrl', 'Shift', 'Alt')
        self.key3opts = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '0')
        self.keycodes = {'<NONE>':None, 'Ctrl':Key.ctrl, 'Shift':Key.shift, 'Alt':Key.alt}
        self.key3opt_alts = {'1':r'!', '2':r'@', '3':r'#', '4':r'$', '5':r'%', '6':r'^', '7':r'&', '8':r'*', '9':r'(', '0':r')'}
        

    def resizeScrollRegion(self, event):
        """Updates scrollable area of the window to expand to include newly created widgets"""
        self.scrlframe.rowconfigure(0, weight='1')
        self.scrlframe.columnconfigure(0, weight='1')
        self.scrollarea.configure(scrollregion = self.scrollarea.bbox("all"))
        self.scrollarea.itemconfig('TheFrame', width = (event.width - 5))
        for frame in self.item_frames :
            frame.columnconfigure(3, weight='1')

    def scrollCanvas(self, event):
        """Scroll the window using mouse wheel"""
        self.scrollarea.yview_scroll(int(-1*event.delta/100), 'units')

    def closeWindow(self):
        confirm = messagebox.askyesno('Quit', "Are you sure you want to exit ?\nAll the shortcuts that have been created here will no longer function.")
        if confirm :
            self.root.destroy()
        

    def help(self):
        """Displays 'How to use' info"""
        info = "Customisable Text Clipboard\n\nGautam D\n3,4 March & 4,5 April 2019\n\nWritten in Python 3.7.2 using tkinter GUI\nUses 'pynput' module for keyboard control\n"+\
                            "See https://pypi.org/project/pynput/ for details\n\n\n   To create a new custom hotkey/shortcut, click on the 'Add New Shortcut' button at the bottom of the window, &"+\
                            " a new widget will appear at the bottom of the 'Clipboard' area (scroll down to see it if the visible area is already filled). Choose 3 keys from the menus in the wid"+\
                            "get and type any text in the text-box to the right. Click 'Save' at the bottom of the window and the application will start listening for that combination of keypress"+\
                            "es as long as it is open. Whenever they are detected, the corresponding text entered will be inserted wherever the typing cursor is at that moment. After creating a s"+\
                            "hortcut, a red 'x' button will appear next to it - click on this to close that widget and delete its reference from the app's memory, to stop using that shortcut.\n\n"+\
                            "\tNote : \n1)   The shortcuts defined work in all windows across the system - even in another desktop on this computer.\n2)   The shortcuts can't be saved permanently"+\
                            " and work only as long as the app is running - all references are lost once the app window is closed.\n3)   New lines, tabs, etc. in the shortcut text are stored as t"+\
                            "he non-printable characters '\\n','\\t', etc. and hence may not be equivalent to pressing 'Enter'/'Return' or 'Tab', etc. in all text editors when pasted.\n4)   Some "+\
                            "Unicode characters like emoticons or characters from other languages may cause an error in encoding/decoding while saving or unexpectedly stop the keystoke listener w"+\
                            "ithout a warning - although rarely so.\n5)   For both modifier keys in a created shortcut that are not '<NONE>', the order of presses is not maintained; For example, "+\
                            "if a hotkey is defined as Ctrl+Shift+5 and is not working, try pressing Shift+Ctrl+5, or Ctrl+5+Shift, etc. in those orders to get a match.\n6)   If two or more short"+\
                            "cuts are created with the same keystroke combination, each new such shortcut overwrites the previous one and the text that will be inserted is of the most recently cr"+\
                            "eated.\n7)   The shortcuts, if used in another application which has also defined some actions for those key combinations, don't override those actions, which will be"+\
                            " performed as well as the required text being pasted.\n8)   The text is pasted after the key combination is pressed and fully released."
        print(info)
        messagebox.showinfo('About', info)


    def addNewItem(self):
        """Creates widgets to add a new hotkey"""
        self.addnew.pack_forget()
        self.name = '_0{}_'.format(self.num_items) if len(str(self.num_items))==1 else '_{}_'.format(self.num_items)
        
        self.item_frames.append(tk.LabelFrame(self.shortcuts, name=self.name))
        self.item_frames[self.num_items].pack(padx=5, pady=5, expand=tk.YES, fill=tk.X)
        
        self.item_labels_1.append(tk.Label(self.item_frames[self.num_items], text = 'Key 1'))
        self.item_labels_1[self.num_items].grid(column=0, row=0, padx=5, pady=5)
        self.item_labels_2.append(tk.Label(self.item_frames[self.num_items], text = 'Key 2'))
        self.item_labels_2[self.num_items].grid(column=1, row=0, padx=5, pady=5)
        self.item_labels_3.append(tk.Label(self.item_frames[self.num_items], text = 'Key 3'))
        self.item_labels_3[self.num_items].grid(column=2, row=0, padx=5, pady=5)
        self.item_labels_4.append(tk.Label(self.item_frames[self.num_items], text = 'Text to paste : '))
        self.item_labels_4[self.num_items].grid(column=3, row=0, padx=5, pady=5)

        self.item_keyvars_1.append(tk.StringVar())
        self.item_keyvars_1[self.num_items].set(self.key1opts[1])
        self.item_keylists_1.append(tk.OptionMenu(self.item_frames[self.num_items], self.item_keyvars_1[self.num_items], *self.key1opts))
        self.item_keylists_1[self.num_items].config(bg='#333333', fg='#ffffff', activebackground='#0055bb', activeforeground='#ffffff')
        self.item_keylists_1[self.num_items].grid(column=0, row=1, padx=5, pady=5)
        
        self.item_keyvars_2.append(tk.StringVar())
        self.item_keyvars_2[self.num_items].set(self.key2opts[0])
        self.item_keylists_2.append(tk.OptionMenu(self.item_frames[self.num_items], self.item_keyvars_2[self.num_items], *self.key2opts))
        self.item_keylists_2[self.num_items].config(bg='#333333', fg='#ffffff', activebackground='#0055bb', activeforeground='#ffffff')
        self.item_keylists_2[self.num_items].grid(column=1, row=1, padx=5, pady=5)
        
        self.item_keyvars_3.append(tk.StringVar())
        self.item_keyvars_3[self.num_items].set(self.key3opts[0])
        self.item_keylists_3.append(tk.OptionMenu(self.item_frames[self.num_items], self.item_keyvars_3[self.num_items], *self.key3opts))
        self.item_keylists_3[self.num_items].config(bg='#333333', fg='#ffffff', activebackground='#0055bb', activeforeground='#ffffff')
        self.item_keylists_3[self.num_items].grid(column=2, row=1, padx=5, pady=5)

        self.item_contents.append(ScrolledText(self.item_frames[self.num_items], width=40, height=3, name=self.name))
        self.item_contents[self.num_items].grid(column=3, row=1, padx=5, pady=5, sticky='NSEW')

        self.item_delbtns.append(tk.Button(self.item_frames[self.num_items], name=self.name, bg='#cc3333', fg='#ffffff', text=' × '))
        self.item_delbtns[self.num_items].bind('<ButtonRelease-1>', self.deleteItem)

        self.saveitem.pack(padx=10, pady=10, side=tk.BOTTOM)

        self.root.geometry('{0}x{1}'.format(self.root.winfo_width(), self.root.winfo_height()+1))
        self.root.geometry('{0}x{1}'.format(self.root.winfo_width(), self.root.winfo_height()-1))
        

    def saveItemDetails(self):
        """Saves details of a newly created hotkey"""
        try :
            self.saveitem.pack_forget()

            '''c = {self.keycodes[self.item_keyvars_1[self.num_items].get()],
                 self.keycodes[self.item_keyvars_2[self.num_items].get()],
                 self.item_keyvars_3[self.num_items].get()}
            if None in c :
                c.remove(None)'''
            k1 = self.keycodes[self.item_keyvars_1[self.num_items].get()]
            k2 = self.keycodes[self.item_keyvars_2[self.num_items].get()]
            k3 = self.item_keyvars_3[self.num_items].get()
            c = [k1, k2, k3]
            if None in c :
                for i in range(c.count(None)):
                    c.remove(None)
            if ((Key.shift in c) or (Key.shift in c and Key.alt in c)) and k3.isdigit() :
                c[c.index(k3)] = self.key3opt_alts[k3]
            if (Key.ctrl in c) and (Key.shift in c or Key.alt in c) and ('4' in c) :
                c[c.index('4')] = '₹'
            c = frozenset(c)
            self.keycombos[c] = '{}'.format(self.name)
            
            self.active_shortcuts['{}'.format(self.name)] = tuple(w[self.num_items] for w in self.item_widgets)

            self.texts['{}'.format(self.name)] = """{}""".format(self.item_contents[self.num_items].get('1.0','end-1c'))

            self.item_keylists_1[self.num_items].config(bg='#ffeb99', fg='#000000', state='disabled')
            self.item_keylists_2[self.num_items].config(bg='#ffeb99', fg='#000000',state='disabled')
            self.item_keylists_3[self.num_items].config(bg='#ffeb99', fg='#000000',state='disabled')
            self.item_contents[self.num_items].config(state='disabled')
            self.item_delbtns[self.num_items].grid(column=4, row=1, padx=15, pady=5)

            self.num_items += 1
            self.addnew.pack(padx=10, pady=10, side=tk.BOTTOM)

            print("\nNew item added : id = ", self.name, '\n\tKeys :\n', c)#, '\n\tText : \n', self.texts['{}'.format(self.name)])
            print("______________________________________________________________")
        except UnicodeEncodeError :
            traceback.print_exc()
            messagebox.showerror('Error', "A character that has been entered cannot be processed. The Customisable Text Clipboard keyboard controller may or may not stop running.")
        

    def deleteItem(self, event):
        """Deletes an existing hotkey"""
        who = str(event.widget)[-4:]
        confirm = messagebox.askyesno('Delete', "Delete this shortcut ?\n\nThe text specified will be removed from the clipboard and associated keys will return to normal use.")
        if confirm == True :
            self.active_shortcuts[who][0].pack_forget()
            for combination, itemid in self.keycombos.items() :
                if itemid == who :
                    del self.keycombos[combination]
                    break
            del self.texts[who]
            print('\nDeleted item ', who)
            print("______________________________________________________________")

        
    def identifyKeyPress(self, key):
        """Called by the keyboard listener whenever a key is pressed"""
        try :
            #n1 = len(self.pressedkeys)
            try :
                x = key.char
                self.pressedkeys.add(key.char)
                #print(key.char, ' pressed', end=' ')
                '''n2 = len(self.pressedkeys)
                if n2 - n1 > 1 :
                    self.pressedkeys.discard(key.char)'''  
            except (AttributeError, UnicodeEncodeError) :
                #print(key, ' _pressed_', end='\t')
                if key == Key.ctrl_l or key == Key.ctrl_r :
                    key = Key.ctrl
                elif key == Key.shift_l or key == Key.shift_r :
                    key = Key.shift
                elif key == Key.alt_l or key == Key.alt_r :
                    key = Key.alt
                self.pressedkeys.add(key)
                '''n2 = len(self.pressedkeys)
                if n2 - n1 > 1 :
                    self.pressedkeys.discard(key.char)'''

            #print(self.pressedkeys, '\t', self.keycombos.keys(), end='\t')
            pressed = frozenset(self.pressedkeys)
            if pressed in self.keycombos.keys() :
                #print('------DETECTED!---------')
                self.detected = self.keycombos[pressed]
            #print(' Key pressed  ')
        except Exception as e :
            print(e)
            messagebox.showerror('Error',"An unknown error has been detected ! The Customisable Text Clipboard keystroke listener may or may not stop running.")
            traceback.print_exc()

    def identifyKeyRelease(self, key):
        """Called by the keyboard listener whenever a key is released"""
        try :
            #print(key, ' released', end=' ')
            try :
                # Some Unicode emoticons, etc register 2 keypresses of a character => They have to be removed twice
                self.pressedkeys.discard(key.char)# ; self.pressedkeys.discard(key.char)
            except (AttributeError, UnicodeEncodeError) :
                if key == Key.ctrl_l or key == Key.ctrl_r :
                    key = Key.ctrl
                elif key == Key.shift_l or key == Key.shift_r :
                    key = Key.shift
                elif key == Key.alt_l or key == Key.alt_r :
                    key = Key.alt
                self.pressedkeys.discard(key)# ; self.pressedkeys.discard(key)
            #print(self.pressedkeys, end=' ')
            if len(self.detected)!=0 and len(self.pressedkeys)==0 :
                #print(' DING DONG !!!!!!!!!!!!!!!!!!!! ')
                self.insertFromClipboard(self.detected)
                self.detected = ""
            #print(' || ')
        except Exception as e :
            print(e)
            messagebox.showerror('Error',"An unknown error has been detected ! The Customisable Text Clipboard keystroke listener may or may not stop running.")
            traceback.print_exc()

    def insertFromClipboard(self, textid):
        """Types required text whenever the hotkey press is detected"""
        self.kb.type(self.texts[textid])
        #print(self.texts[textid])
        print(textid)
        #print('------DETECTED!---------')


if __name__ == "__main__" :

    app = Clipboard()


