from tkinter import *


class MajButton(Button):
    def __init__(self, master, row, col, text: str, val: int, color=None, **kwargs):
        self.text = text
        self.row = row
        self.column = col
        self.val = val
        self.inputArray = None
        self.master = master
        self.color = color
        self.show = None
        self.maxInputLength = 0
        self.clickcount = 0
        super().__init__(master)
        self['text'] = self.text
        self["width"] = 1
        self["height"] = 1
        self["fg"] = self.color
        self["font"] = ('Arial', 20)
        self.grid(row=self.row, column=self.column)
        self["command"] = self.importButtonClick

    def importButtonClick(self):
        if len(self.inputArray) >= self.maxInputLength:
            return
        # print(self.val)
        self.inputArray.append(self.val)
        self.show["text"] += self.text

    def setInputArray(self, toSet):
        self.inputArray = toSet

    def setShow(self, toShow):
        self.show = toShow

    def setInputLength(self, length):
        self.maxInputLength = length
