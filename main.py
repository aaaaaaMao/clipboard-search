from PyQt5.QtWidgets import QApplication

app = QApplication([])
clipboard = app.clipboard()

def read_clipboard():
    data = clipboard.mimeData()
	
    if 'text/plain' in data.formats():
        print(data.text())

clipboard.dataChanged.connect(read_clipboard)
app.exec_()