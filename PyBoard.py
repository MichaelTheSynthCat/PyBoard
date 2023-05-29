# PyBoard.py
# Main program script
# Author: Michal Krulich

from tkinter import *
from tkinter import ttk
from tkinter import colorchooser
from tkinter import filedialog
import csv
import os
from squareboard_class import *  # custom classes
from edgeboard_class import *
from cornerboard_class import *


symbols = ('None', 'Cross', 'Char')  # Possible symbol identifiers
cwd = os.getcwd()


class SBobject:  # universal object storing position and type
    Names = {'c': 'Corner', 'he': 'Horizontal edge',
             've': 'Vertical edge', 's': 'Square'}

    def __init__(self, columns, rows, _type):
        self.pos = [columns, rows]
        self.type = _type


class Colorselect(Canvas):  # preview color for NewData window
    def __init__(self, frame, value, dimension=30, **kwargs):
        Canvas.__init__(self, frame, height=dimension,
                        width=dimension, **kwargs)
        if value.get() != 'None':
            self['bg'] = value.get()
        self.color = value
        self.bind('<1>', lambda event: self.change(event))

    def change(self, event):
        color = colorchooser.askcolor(initialcolor='#ff0000')[1]
        if color is not None:
            self['bg'] = color
            self.color.set(color)
        try:
            newdatawin.lift(tk)
        except:
            pass


class CheckWrite(Checkbutton):
    def __init__(self, frame, variable, **kwargs):
        Checkbutton.__init__(self, frame, variable=variable,
                             onvalue='True', offvalue='False', **kwargs)


class NewData(Toplevel):  # window for creating new squareboard
    def __init__(self):
        global newdatawin
        Toplevel.__init__(self, tk)
        newdatawin = self

        self.crframe = Frame(self)
        self.crframe.grid(column=0, row=5, columnspan=5)
        f = self.crframe

        self.opt = {'columns': StringVar(value=10), 'rows': StringVar(value=10),
                    'colors': {'Squares': StringVar(value='#ffffff'), 'Edges': StringVar(value='#000000'),
                               'Corners': StringVar(value='#000000')},
                    'background': StringVar(value='#ffffff'), 'symbol': StringVar(value='None'),
                    'sqdimension': StringVar(value=60), 'linewidth': StringVar(value=7),
                    'charsame': StringVar(value='True'), 'charsize': StringVar(value=50)}

        Label(self, text='Chart settings').grid(column=0, row=0, columnspan=5)
        Label(f, text='Columns:').grid(column=0, row=5)
        Spinbox(f, textvariable=self.opt['columns'], from_=1, to=1000, width=5).grid(
            column=1, row=5)
        Label(f, text='Rows').grid(column=2, row=5)
        Spinbox(f, textvariable=self.opt['rows'], from_=1, to=1000, width=5).grid(
            column=3, row=5)

        ttk.Separator(self, orient=HORIZONTAL).grid(
            column=0, row=6, sticky=(W, E), columnspan=5)

        Label(self, text='Graphical settings').grid(
            column=0, row=7, columnspan=5)
        self.colorframe = Frame(self)
        self.colorframe.grid(column=0, row=8, columnspan=5)
        f = self.colorframe
        i = 0
        for part in iter(self.opt['colors']):
            Label(f, text=part).grid(column=0, row=8+i, sticky=E)
            Colorselect(f, self.opt['colors'][part]).grid(
                column=1, row=8 + i, sticky=W)
            i += 1
        Label(f, text='Background').grid(column=0, row=8+i, sticky=E)
        Colorselect(f, self.opt['background']).grid(
            column=1, row=8 + i, sticky=W)
        Label(f, text='Symbol').grid(column=2, row=8)
        ttk.Combobox(f, textvariable=self.opt['symbol'], width=10,
                     values=symbols).grid(column=3, row=8)
        Label(f, text='Square size').grid(column=2, row=9)
        Spinbox(f, textvariable=self.opt['sqdimension'], width=7, from_=1, to=500).grid(
            column=3, row=9)
        Label(f, text='Line width').grid(column=2, row=10)
        Spinbox(f, textvariable=self.opt['linewidth'], width=7, from_=1, to=500).grid(
            column=3, row=10)
        Label(f, text='Char size').grid(column=2, row=11)
        self.charcustomizer = Spinbox(f, textvariable=self.opt['charsize'], width=7,
                                      state=DISABLED)
        self.charcustomizer.grid(column=3, row=11)
        CheckWrite(f, variable=self.opt['charsame'], text='Char size as square', command=self.customchar_handler)\
            .grid(column=2, row=12, columnspan=2)

        ttk.Separator(self, orient=HORIZONTAL).grid(
            column=0, row=90, sticky=(W, E), columnspan=5)

        self.bframe = Frame(self)
        self.bframe.grid(column=0, row=100, columnspan=5, sticky=E)
        Button(self.bframe, text='Cancel',
               command=self.cancel).grid(column=4, row=100)
        Button(self.bframe, text='Create',
               command=self.confirm).grid(column=5, row=100)

    def customchar_handler(self):
        if eval(self.opt['charsame'].get()):
            self.charcustomizer['state'] = DISABLED
        else:
            self.charcustomizer['state'] = 'normal'

    def confirm(self):
        global data, newdatawin, workspace
        workspace.destroy()
        del workspace
        del data
        data = DataBank(int(self.opt['columns'].get()), int(self.opt['rows'].get()),
                        colors={'squares': self.opt['colors']['Squares'].get(),
                                'edges': self.opt['colors']['Edges'].get(),
                                'corners': self.opt['colors']['Corners'].get(),
                                'background': self.opt['background'].get()},
                        symbol=self.opt['symbol'].get())
        if eval(self.opt['charsame'].get()):
            self.opt['charsize'].set(self.opt['sqdimension'].get())
        print(self.opt['charsize'].get())
        workspace = GraphicEngine(int(self.opt['columns'].get()), int(self.opt['rows'].get()),
                                  sqdimension=int(
                                      self.opt['sqdimension'].get()),
                                  linewidth=int(self.opt['linewidth'].get()),
                                  charsize=int(self.opt['charsize'].get()))
        self.destroy()
        del newdatawin

    def cancel(self):
        global newdatawin
        self.destroy()
        del newdatawin


# Quick dialog window for changing dimension of certain type of objects
class ChangeViewDialog(Toplevel):
    dic = {'sqdimension': 'Square dimension',
           'linewidth': 'Line width', 'charsize': 'Charsize'}

    def __init__(self, opt):
        Toplevel.__init__(self, main)
        self.title(self.dic[opt])
        self.opt = opt
        self.value = StringVar(value=eval('workspace.'+opt))
        Label(self, text='Set value:').grid(column=0, row=0)
        spin = Spinbox(self, textvariable=self.value, width=7, from_=1, to=500)
        spin.grid(column=1, row=0)
        spin.focus()
        Button(self, text='Cancel', command=self.cancel).grid(column=0, row=100)
        Button(self, text='Confirm', command=self.confirm).grid(
            column=1, row=100)

        self.bind('<Return>', lambda e: self.confirm())

    def confirm(self):
        self.destroy()
        eval('workspace.changeview({}={})'.format(self.opt, self.value.get()))
        del self

    def cancel(self):
        self.destroy()
        del self


class Main(Frame):  # mainframe
    def __init__(self):
        global tk
        Frame.__init__(self, tk, bg="#c0c0c0")
        self.grid(column=0, row=0)

    def start(self):
        pass


class Menubar(Menu):  # menubar class
    def __init__(self):
        Menu.__init__(self, tk)
        tk['menu'] = self
        tk.option_add('*tearOff', FALSE)
        self.tabs = {'main': Menu(self), 'view': Menu(self)}

        self.add_cascade(menu=self.tabs['main'], label='Main')
        self.tabs['main'].add_command(label='New', command=NewData)
        self.tabs['main'].add_command(label='Open', command=fileopen)
        self.tabs['main'].add_command(label='Save', command=filesave)
        self.tabs['main'].add_command(label='Exit', command=tk.destroy)

        self.add_cascade(menu=self.tabs['view'], label='View')
        self.tabs['view'].add_command(
            label='Square dimension', command=lambda opt='sqdimension': ChangeViewDialog(opt))
        self.tabs['view'].add_command(
            label='Line width', command=lambda opt='linewidth': ChangeViewDialog(opt))
        self.tabs['view'].add_command(
            label='Char size', command=lambda opt='charsize': ChangeViewDialog(opt))

        self.add_command(label='Help', command=help_dialog)


class DataBank:  # data storage class
    def __init__(self, columns, rows,
                 colors={'squares': '#ffffff', 'edges': '#000000',
                         'corners': '#000000', 'background': '#ffffff'},
                 symbol='None'):
        # create storage classes for squares, edges and corners
        self.squareboard = SquareBoard(
            columns, rows, color=colors['squares'], background=colors['background'], symbol=symbol)
        self.edgeboard_horizontal = Edgeboard(
            columns, rows+1, orient="horizontal", color=colors['edges'])
        self.edgeboard_vertical = Edgeboard(
            columns+1, rows, orient="vertical", color=colors['edges'])
        self.cornerboard = Cornerboard(
            columns+1, rows+1, color=colors['corners'])
        self.types = {'s': self.squareboard, 'he': self.edgeboard_horizontal,
                      've': self.edgeboard_vertical, 'c': self.cornerboard}
        self.chart = [columns, rows]

    def edit(self, event):  # edit selected object, also mouse button 1 event handler
        obj = viewer.find_object(event)[0]
        if obj.type == 's' and not eval(palette.selectedit['square'].get()):
            return
        if obj.type in ('he', 've') and not eval(palette.selectedit['edge'].get()):
            return
        if obj.type == 'c' and not eval(palette.selectedit['corner'].get()):
            return
        if eval(palette.allowwrite['value'].get()):
            self.types[obj.type].data[obj.pos[1]][obj.pos[0]
                                                  ].value = palette.edit['value'].get()
        if eval(palette.allowwrite['symbol'].get()) and obj.type == 's':
            self.types[obj.type].data[obj.pos[1]][obj.pos[0]
                                                  ].symbol = palette.edit['symbol'].get()
        if eval(palette.allowwrite['color'].get()):
            self.types[obj.type].data[obj.pos[1]][obj.pos[0]
                                                  ].color = palette.edit['color'].get()
        if eval(palette.allowwrite['background'].get()) and obj.type == 's':
            self.types[obj.type].data[obj.pos[1]][obj.pos[0]
                                                  ].background = palette.edit['background'].get()
        workspace.render()


class GraphicEngine(Canvas):  # canvas for squareboard
    def __init__(self, columns, rows, sqdimension=60, linewidth=7, charsize=None):
        width = linewidth*(columns+1)+columns*sqdimension+10
        height = linewidth*(rows+1)+rows*sqdimension+10
        Canvas.__init__(self, main, width=width, height=height)
        self.grid(column=20, row=0, columnspan=10,
                  rowspan=10, padx=10, pady=10)
        self.chart = [columns, rows]  # number of columns and rows
        self.dimensions = [width, height]  # width and height in pixels
        self.sqdimension = sqdimension  # dimension of a square in pixels
        self.linewidth = linewidth  # width of a line in pixels
        if charsize is None:
            self.charsize = self.sqdimension
        else:
            self.charsize = charsize
        self.render()

        self.bind('<1>', lambda event: data.edit(event))
        self.bind('<Motion>', lambda event: viewer.showinfo(event))

    def render(self):  # render the squareboard
        self.delete('last')  # erase previous view
        # squares
        for r in range(self.chart[1]):
            for c in range(self.chart[0]):
                if data.squareboard.data[r][c].symbol == 'None':
                    self.create_rectangle(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                                          self.dimensions[1] - self.linewidth - r *
                                          (self.sqdimension + self.linewidth) - 5,
                                          (c + 1) * (self.sqdimension +
                                                     self.linewidth) + 5,
                                          self.dimensions[1] - (r + 1) * (
                                              self.sqdimension + self.linewidth) - 5,
                                          fill=data.squareboard.data[r][c].color,
                                          outline=data.squareboard.data[r][c].color, tags='last')
                else:
                    self.create_rectangle(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                                          self.dimensions[1]-self.linewidth-r *
                                          (self.sqdimension+self.linewidth) - 5,
                                          (c + 1) * (self.sqdimension +
                                                     self.linewidth) + 5,
                                          self.dimensions[1] - (r + 1) * (
                                              self.sqdimension + self.linewidth) - 5,
                                          fill=data.squareboard.data[r][c].background,
                                          outline=data.squareboard.data[r][c].background, tags='last')
                    if data.squareboard.data[r][c].symbol == 'Cross':
                        self.create_line(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                                         self.dimensions[1] - self.linewidth - r *
                                         (self.sqdimension + self.linewidth) - 5,
                                         (c + 1) * (self.sqdimension +
                                                    self.linewidth) + 5,
                                         self.dimensions[1] - (r + 1) * (
                                             self.sqdimension + self.linewidth) - 5,
                                         fill=data.squareboard.data[r][c].color, width=self.sqdimension//10,
                                         tags='last')
                        self.create_line(self.linewidth + c * (self.sqdimension + self.linewidth) + 5,
                                         self.dimensions[1] - (r + 1) * (
                                             self.sqdimension + self.linewidth) - 5,
                                         (c + 1) * (self.sqdimension +
                                                    self.linewidth) + 5,
                                         self.dimensions[1] - self.linewidth - r *
                                         (self.sqdimension + self.linewidth) - 5,
                                         fill=data.squareboard.data[r][c].color, width=self.sqdimension//10,
                                         tags='last')
                    if data.squareboard.data[r][c].symbol == 'Char':
                        if len(data.squareboard.data[r][c].value) > 1:
                            char = data.squareboard.data[r][c].value[0]
                        else:
                            char = data.squareboard.data[r][c].value
                        self.create_text(self.linewidth + c * (self.sqdimension + self.linewidth) + 5 + self.sqdimension//2,
                                         self.dimensions[1] - (r + 1) * (
                                             self.sqdimension + self.linewidth) - 5 + self.sqdimension//2+self.sqdimension//25,
                                         text=char, fill=data.squareboard.data[r][c].color, font=(
                                             'Arial', self.charsize),
                                         tags=('last', 'char'))
        # horizontal edges
        for r in range(self.chart[1]+1):
            for c in range(self.chart[0]):
                for e in range(self.linewidth):
                    self.create_line(self.linewidth+c*(self.sqdimension+self.linewidth)+5,
                                     self.dimensions[1]-r *
                                     (self.sqdimension+self.linewidth)-e-5,
                                     (c+1)*(self.sqdimension+self.linewidth)+5,
                                     self.dimensions[1]-r *
                                     (self.sqdimension+self.linewidth)-e-5,
                                     fill=data.edgeboard_horizontal.data[r][c].color, tags='last')
        # vertical edges
        for r in range(self.chart[1]):
            for c in range(self.chart[0]+1):
                for e in range(self.linewidth):
                    self.create_line(c*(self.sqdimension+self.linewidth)+e+5,
                                     self.dimensions[1]-self.linewidth-r *
                                     (self.sqdimension+self.linewidth)-5,
                                     c*(self.sqdimension+self.linewidth)+e+5,
                                     self.dimensions[1]-(r+1) *
                                     (self.sqdimension+self.linewidth)-5,
                                     fill=data.edgeboard_vertical.data[r][c].color, tags='last')
        # corners
        for r in range(self.chart[1]+1):
            for c in range(self.chart[0]+1):
                self.create_rectangle(c*(self.sqdimension+self.linewidth)+5,
                                      self.dimensions[1]-r *
                                      (self.sqdimension+self.linewidth)-5,
                                      c*(self.sqdimension+self.linewidth) +
                                      self.linewidth-1+5,
                                      self.dimensions[1]-r*(self.sqdimension +
                                                            self.linewidth)-self.linewidth+1-5,
                                      fill=data.cornerboard.data[r][c].color,
                                      outline=data.cornerboard.data[r][c].color, tags='last')
        self.tag_raise('char')  # push characters to the front

    # Change current rendering dimensions of squares, corners and edges in pixels.
    # None value means: do not change.
    def changeview(self, sqdimension=None, linewidth=None, charsize=None):
        if sqdimension is not None:
            self.sqdimension = sqdimension
        if linewidth is not None:
            self.linewidth = linewidth
        if charsize is not None:
            self.charsize = charsize
        width = self.linewidth * \
            (self.chart[0]+1)+self.chart[0]*self.sqdimension+10
        height = self.linewidth * \
            (self.chart[1]+1)+self.chart[1]*self.sqdimension+10
        self['width'] = width
        self['height'] = height
        self.dimensions = [width, height]
        self.render()


class Palette(Frame):  # palette with customizing tools
    def __init__(self):
        global main
        Frame.__init__(self, main)
        self.grid(column=0, row=0)
        # tkinter string variables
        self.edit = {'color': StringVar(value='#000000'), 'background': StringVar(value='#ffffff'),
                     'symbol': StringVar(value='None'), 'value': StringVar(value='')}
        self.allowwrite = {'color': StringVar(value='True'), 'background': StringVar(value='True'),
                           'symbol': StringVar(value='True'), 'value': StringVar(value='True')}

        # preview colors
        self.colorframe = Frame(self)
        self.colorframe.grid(column=0, row=0)
        self.maincolor = Colorselect(
            self.colorframe, self.edit['color'], dimension=50)
        self.maincolor.grid(column=0, row=1, columnspan=2)
        Label(self.colorframe, text='Main color').grid(
            column=0, row=0, columnspan=2)
        Label(self.colorframe, textvariable=self.edit['color']).grid(
            column=0, row=2)
        CheckWrite(self.colorframe, variable=self.allowwrite['color']).grid(
            column=1, row=2)
        self.bgcolor = Colorselect(
            self.colorframe, self.edit['background'], dimension=50)
        self.bgcolor.grid(column=2, row=1, columnspan=2)
        Label(self.colorframe, text='Background').grid(
            column=2, row=0, columnspan=2)
        Label(self.colorframe, textvariable=self.edit['background']).grid(
            column=2, row=2)
        CheckWrite(self.colorframe, variable=self.allowwrite['background']).grid(
            column=3, row=2)

        # other options
        self.otherframe = Frame(self)
        self.otherframe.grid(column=0, row=5)
        Label(self.otherframe, text='Symbol').grid(column=0, row=5)
        ttk.Combobox(self.otherframe, textvariable=self.edit['symbol'], width=10,
                     values=symbols).grid(column=1, row=5)
        CheckWrite(self.otherframe, variable=self.allowwrite['symbol']).grid(
            column=2, row=5)
        Label(self.otherframe, text='Value').grid(column=0, row=6)
        Entry(self.otherframe, textvariable=self.edit['value'], width=12).grid(
            column=1, row=6)
        CheckWrite(self.otherframe, variable=self.allowwrite['value']).grid(
            column=2, row=6)

        ttk.Separator(self, orient=HORIZONTAL).grid(
            column=0, row=9, sticky=(W, E), columnspan=5)

        # Edit lock
        # Lets you choose, which objects can be edited.
        self.selectedit = {'square': StringVar(value='True'),
                           'edge': StringVar(value='True'),
                           'corner': StringVar(value='True')}
        self.selframe = Frame(self)
        self.selframe.grid(column=0, row=10)
        i = 0
        for sel in self.selectedit:
            Label(self.selframe, text=sel.capitalize()).grid(
                column=0, row=10+i)
            CheckWrite(self.selframe, variable=self.selectedit[sel]).grid(
                column=1, row=10+i)
            i += 1


class Viewer(Frame):  # show info about the object which cursor is pointing at
    def __init__(self):
        global main
        Frame.__init__(self, main)
        self.grid(column=50, row=0)
        self.prefix = {'text': "Type: {}\nColumn: {}  Row: {}\nValue: {}\nColor: {}\nBackground: {}\nSymbol: {}",
                       'realpos': 'X: {}    Y: {}'}
        self.obj = {'realpos': StringVar(value=self.prefix['realpos'])}
        Label(self, text="Pointing at           ").grid(
            column=50, row=0, sticky=W)
        Label(self, textvariable=self.obj['realpos']).grid(
            column=50, row=1, sticky=W)
        self.info = Text(self, height=12, width=30)
        self.info.grid(column=50, row=2, sticky=W)
        self.info.insert(END, self.prefix['text'])
        self.info.tag_add('main', '1.0', END)
        self.info.tag_config('main', font='Arial')

    def find_object(self, event):  # calculate at which object cursor is pointing
        fx = event.x
        fy = workspace.dimensions[1] - event.y
        if fx > workspace.dimensions[0]-5 or fx < 5 or fy > workspace.dimensions[1]-5 or fy < 5:
            return None, None
        fx -= 5
        fy -= 5

        c = fx // (workspace.linewidth + workspace.sqdimension)
        r = fy // (workspace.linewidth + workspace.sqdimension)
        x = fx % (workspace.linewidth+workspace.sqdimension)
        y = fy % (workspace.linewidth+workspace.sqdimension)
        if y <= workspace.linewidth:
            xline = True
        else:
            xline = False
        if x <= workspace.linewidth:
            yline = True
        else:
            yline = False
        if xline and yline:
            _type = 'c'
        elif xline:
            _type = 'he'
        elif yline:
            _type = 've'
        else:
            _type = 's'
        return SBobject(c, r, _type), [fx, fy]

    def showinfo(self, event):
        obj, fpos = self.find_object(event)
        if obj is None:
            return
        adress = data.types[obj.type].data[obj.pos[1]][obj.pos[0]]
        self.obj['realpos'].set(
            self.prefix['realpos'].format(fpos[0], fpos[1]))
        if obj.type == 's':
            bg = adress.background
            sym = adress.symbol
        else:
            bg = 'Doesn\'t have'
            sym = 'Doesn\'t have'
        self.info.delete('1.0', END)
        self.info.insert(END, self.prefix['text'].format(obj.Names[obj.type], obj.pos[0], obj.pos[1],
                                                         adress.value, adress.color, bg, sym))
        self.info.tag_add('main', '1.0', END)
        self.info.tag_config('main', font='Arial')


# Save currently viewed squareboard as a CSV file.
def filesave():
    # open system dialog
    path = filedialog.asksaveasfilename(initialdir=cwd,
                                        filetypes=(("Comma separated values *.csv", "*.csv"), ("all files", "*.*")))
    if path == '':
        return
    if path[-4:] != '.csv':
        path += '.csv'
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            [workspace.sqdimension, workspace.linewidth, workspace.charsize])
        writer.writerow(data.chart)
        for r in range(data.chart[1]):
            for c in range(data.chart[0]):
                if data.squareboard.data[r][c].value == '':
                    value = '<Empty>'
                else:
                    value = data.squareboard.data[r][c].value
                writer.writerow([data.squareboard.data[r][c].color, data.squareboard.data[r][c].background,
                                 value, data.squareboard.data[r][c].symbol])
        for r in range(data.chart[1]+1):
            for c in range(data.chart[0]):
                if data.edgeboard_horizontal.data[r][c].value == '':
                    value = '<Empty>'
                else:
                    value = data.edgeboard_horizontal.data[r][c].value
                writer.writerow(
                    [data.edgeboard_horizontal.data[r][c].color, value])
        for r in range(data.chart[1]):
            for c in range(data.chart[0]+1):
                if data.edgeboard_vertical.data[r][c].value == '':
                    value = '<Empty>'
                else:
                    value = data.edgeboard_vertical.data[r][c].value
                writer.writerow(
                    [data.edgeboard_vertical.data[r][c].color, value])
        for r in range(data.chart[1]+1):
            for c in range(data.chart[0]+1):
                if data.cornerboard.data[r][c].value == '':
                    value = '<Empty>'
                else:
                    value = data.cornerboard.data[r][c].value
                writer.writerow([data.cornerboard.data[r][c].color, value])

# Open a PyBoard CSV file containing a squareboard data.


def fileopen():
    path = filedialog.askopenfilename(initialdir=cwd,
                                      filetypes=(("Comma separated values *.csv", "*.csv"), ("all files", "*.*")))
    if path == '':
        return
    global data, workspace
    workspace.destroy()
    del data, workspace
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file)
        viewopt = next(reader)
        for x in range(len(viewopt)):
            viewopt[x] = int(viewopt[x])
        chart = next(reader)
        data = DataBank(int(chart[0]), int(chart[1]))
        for r in range(data.chart[1]):
            for c in range(data.chart[0]):
                line = next(reader)
                data.squareboard.data[r][c].color = line[0]
                data.squareboard.data[r][c].background = line[1]
                value = line[2]
                if value == '<Empty>':
                    data.squareboard.data[r][c].value = ''
                else:
                    data.squareboard.data[r][c].value = value
                data.squareboard.data[r][c].symbol = line[3]
        for r in range(data.chart[1]+1):
            for c in range(data.chart[0]):
                line = next(reader)
                data.edgeboard_horizontal.data[r][c].color = line[0]
                value = line[1]
                if value == '<Empty>':
                    data.edgeboard_horizontal.data[r][c].value = ''
                else:
                    data.edgeboard_horizontal.data[r][c].value = value
        for r in range(data.chart[1]):
            for c in range(data.chart[0]+1):
                line = next(reader)
                data.edgeboard_vertical.data[r][c].color = line[0]
                value = line[1]
                if value == '<Empty>':
                    data.edgeboard_vertical.data[r][c].value = ''
                else:
                    data.edgeboard_vertical.data[r][c].value = value
        for r in range(data.chart[1]+1):
            for c in range(data.chart[0]+1):
                line = next(reader)
                data.cornerboard.data[r][c].color = line[0]
                value = line[1]
                if value == '<Empty>':
                    data.cornerboard.data[r][c].value = ''
                else:
                    data.cornerboard.data[r][c].value = value
    workspace = GraphicEngine(int(chart[0]), int(
        chart[1]), viewopt[0], viewopt[1], viewopt[2])


def help_dialog():
    global winhelp
    try:
        winhelp.destroy()
    except NameError:
        pass
    winhelp = Toplevel(tk)
    winhelp.title("PyBoard - Help")
    winhelp.resizable(False, False)
    text = Text(winhelp, height=40, width=100)
    text.grid()
    text.insert('1.0',
                """<<<----- PyBoard ----->>>
PyBoard is a free open source program for Windows written in Python that lets you visualize
squareboards, 2D arrays and more!

--- Palette with tools ---
Use the tool palette on the left side to tweak current painting tools.
If the tool's checkbox is ticked, the tool is used.
If the checkbox with object type is checked, the type of object can be edited.

--- Info Panel ---
The panel on the right side tells you about the object which mouse cursor is pointing at.

--- Everything is too small? ---
Use View option on the top menubar to change rendering size of the certain objects.

--- Save for later ---
You can save your current squarboard for later as a CSV file and open it whenever you want.
You can find these options in the Main menu.

--- Characters in the squares ---
Write one character into the Value field and set Symbol type to Char.
Click on a square and the character will be displayed there.

--- License and author ---
Author: Michal Krulich
License: GNU GPL 3.0

--- Github repository ---
https://github.com/MichaelTheSynthCat/PyBoard
    """)
    text['state'] = DISABLED


if __name__ == '__main__':
    tk = Tk()
    tk.title("PyBoard")
    tk.menu = Menubar()
    main = Main()
    data = DataBank(10, 10)
    workspace = GraphicEngine(data.chart[0], data.chart[1])
    palette = Palette()
    viewer = Viewer()
    tk.mainloop()
