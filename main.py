import os
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
#from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel

def final_lst(x): #get image lst
    image_listing = []
    y =  ['bmp', 'gif', 'jpg', 'jpeg', 'png', 'pbm', 'pgm', 'ppm', 'xbm', 'xpm']
    for i in x:
        i = i.lower()
        extension = i[-3:]
        four_char = i[-4:] ## exclusively for jpeg
        if extension in y or four_char in y:
            image_listing.append(i)        
    return image_listing

class displayImage(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
        self.parent = parent
        self.pixmap = QPixmap()
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.assigned_img_full_path = ''
    # gonna update image in widget for full view...
    def update_display_image(self, path_to_image):
        self.assigned_img_full_path = path_to_image
        print(self.assigned_img_full_path)

        ## render the display image when a thumbnail is selected
        self.on_main_window_resize()
    # adjust image size when window gonna be resized....
    def on_main_window_resize(self, event=None):
        main_window_size = self.parent.size()
        print(main_window_size)
        main_window_height = main_window_size.height()
        print(main_window_height)
        main_window_width = main_window_size.width()
        print(main_window_width)

        display_image_max_height = main_window_height - 50
        display_image_max_width = main_window_width - 200
        print(display_image_max_height, display_image_max_width)
        print(1)
        self.pixmap = QPixmap(self.assigned_img_full_path)
        print(2)
        self.pixmap = self.pixmap.scaled(QSize(display_image_max_width, display_image_max_height), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #self.pixmap = self.pixmap.scaledToWidth(display_image_max_width, Qt.SmoothTransformation)
        print(3)
        print(self.pixmap.__dict__)
        print(dir(self.pixmap))
        self.label.setPixmap(self.pixmap)
        self.label.setAlignment(Qt.AlignCenter)

class displayImageList(QWidget):
    def __init__(self, parent = None, album_path='', display_image=None, image_list=None):
        QWidget.__init__(self, parent=parent)
        self.album_path = album_path
        self.image_list = image_list
        self.display_image = display_image
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setVerticalSpacing(30)
        row_in_grid_layout = 0
        first_img_file_path = ''
        for i in self.image_list:
            name  = QLabel()
            image = QLabel()
            # next align image to center of widget......
            name.setAlignment(Qt.AlignCenter)
            image.setAlignment(Qt.AlignCenter)
            # full path of image
            file_path = self.album_path + '\\' + i
            print(file_path)
            # creating pixmap object
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(QSize(100,100), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            image.setPixmap(pixmap)
            name.setText(i)
            # mouse events for both text and image
            image.mousePressEvent = lambda e, index=row_in_grid_layout, file_path=file_path: self.on_thumbnail_click(e, index, file_path)
            name.mousePressEvent = image.mousePressEvent
            # add both into a single widget...
            thumbnail = QBoxLayout(QBoxLayout.TopToBottom)
            thumbnail.addWidget(image)
            thumbnail.addWidget(name)
            # add layout properties
            self.grid_layout.addLayout( thumbnail, row_in_grid_layout, 0, Qt.AlignCenter)
            # setting image file path for image which are currently selected in thumbnail field...
            if row_in_grid_layout == 0: first_img_file_path = file_path
            # increase value for row number
            row_in_grid_layout += 1
        # adding what happened on when click on thumbnail image...
        self.on_thumbnail_click(None, 0, first_img_file_path)

    def on_thumbnail_click(self, event, index, file_path):
        ## Deselect all thumbnails in the image selector
        for text_label_index in range(len(self.grid_layout)):
            text_label = self.grid_layout.itemAtPosition(text_label_index, 0).itemAt(1).widget()
            text_label.setStyleSheet("background-color:none;")

        ## Select the single clicked thumbnail
        text_label_of_thumbnail = self.grid_layout.itemAtPosition(index, 0).itemAt(1).widget()
        text_label_of_thumbnail.setStyleSheet("background-color:white;")

        ## Update the display's image
        self.display_image.update_display_image(file_path) 

class windows(QWidget):
    count = 0
    def __init__(self, path_dir=None, parent=None):
        super(windows, self).__init__()
        #seeting windows attribute
        self.resizeEvent = lambda e : self.on_main_window_resize(e)

        # get album and filenames from album...
        self.path_dir = path_dir
        if self.path_dir == None:
            self.path_dir = os.getcwd()
        else:
            self.path_dir = path_dir
        self.path_list = os.listdir(self.path_dir)
        self.img = final_lst(self.path_list)

        # show image...
        self.display_image = displayImage(self)
        # for getting a list of image and show small size of them
        self.image_file_selector = displayImageList(self, album_path=self.path_dir, display_image=self.display_image, image_list=self.img)
        # scroll for image scrolling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(140)
        nav = scroll
        nav.setWidget(self.image_file_selector)

        # setting widget in places
        layout = QGridLayout(self)
        layout.addWidget(nav, 0, 0, Qt.AlignLeft)
        layout.addWidget(self.display_image.label, 0, 1, Qt.AlignCenter)
        self.setLayout(layout)

    def on_main_window_resize(self, event):
        self.display_image.on_main_window_resize(event)


class MainWindow(QMainWindow):
    def __init__(self, path_dir=None, parent=None):
        super().__init__(parent)
        self.path_dir = path_dir
        #adding widgets into window and adding windows class
        self.viewer = windows(self.path_dir, parent=self)
        self.setCentralWidget(self.viewer)

        #setting windows attribute
        self.setWindowTitle('Photo Viewer')
        self.resize(1024,660)
        self.setAutoFillBackground(True)

        # adding menubar
        openFile = QAction("&Open Folder", self)
        openFile.setShortcut("Ctrl+O")
        openFile.setStatusTip('Open File')
        openFile.triggered.connect(self.openFolder)
        # exit
        exit_act = QAction('Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        exit_act.triggered.connect(self.close)

        # Create menubar
        menu_bar = self.menuBar()
        # For MacOS users, places menu bar in main window
        menu_bar.setNativeMenuBar(False)
        # Create file menu and add actions
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(openFile)
        file_menu.addAction(exit_act)

    def openFolder(self):
        self.name = QFileDialog().getExistingDirectory(self, 'Open File', '') # for open a folder
        self.refresh()
    def refresh(self):
        d = self.viewer.children()
        e = reversed(d)

        for g in e:
            g.deleteLater()
        
        self.viewer = windows(self.name, parent=self)
        self.setCentralWidget(self.viewer)


def main():
    try:
        app
    except:
        app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    # Start the event loop.
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()