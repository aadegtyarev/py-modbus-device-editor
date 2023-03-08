from tkinter import *

tk = Tk()
tk.withdraw()

d = DoubleVar(master=tk, value=0)


def my_event_handler(*args):
    amount = "{:.2f}".format(d.get())
    print("$"+amount)


d.trace(mode="w", callback=my_event_handler)

d.set(5.55)
d.set(15.12)
