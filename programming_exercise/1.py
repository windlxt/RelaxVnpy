from PySide6.QtWidgets import QDialog
s = dir('qtawesome_pushbutton.py')
print(s)
for name in s:
    try:
        value = getattr(s, name)
        # print(value)
        if isinstance(value, type):
            print(value)
    except:
        pass
