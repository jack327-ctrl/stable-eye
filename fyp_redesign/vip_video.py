from PyQt5.QtWidgets import QPushButton, QWidget, QLabel,QScrollArea, QApplication, QMainWindow
from PyQt5.QtCore import Qt
import sys

class UIMainTeacher(object):
    def setupUI(self, MainWindow):
        MainWindow.setGeometry(50, 50, 400, 450)
        MainWindow.setFixedSize(1800, 1000)
        MainWindow.setWindowTitle("Main")

        self.mainWindow = MainWindow
        self.centralwid = QScrollArea(MainWindow)
        self.centralwid.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.centralwidget = QWidget(self.centralwid)

        self.exitButton = QPushButton("Exit", self.centralwid)
        self.exitButton.move(1700, 0)
        self.CourseLabel = QLabel("No Kourse yet", self.centralwid)
        self.CourseLabel.move(900, 20)
        self.AddCourseButton = QPushButton('Add Course', self.centralwid)
        self.AddCourseButton.move(1700, 25)
        self.CourseLabel = QLabel("Course", self.centralwidget)
        self.CourseLabel.move(900, 20)
        self.AddStudentsButton = QPushButton("Add Students", self.centralwid)
        self.AddStudentsButton.move(1700, 100)

        self.taskLabel = QLabel("TASKS:", self.centralwidget)
        self.taskLabel.move(160, 20)
        self.AddTaskButton = QPushButton('Add Task', self.centralwid)
        self.AddTaskButton.move(1700, 50)

        self.centralwid.setWidget(self.centralwidget)
        MainWindow.setCentralWidget(self.centralwid)

        x, y = 600, 0
        for _ in range(200):
            label = QLabel("Test Test", self.centralwidget)
            label.move(x, y)
            y += 50
        self.centralwidget.setFixedWidth(800)
        self.centralwidget.setFixedHeight(y)

app = QApplication(sys.argv)
form = UIMainTeacher()
# form.show()
sys.exit(app.exec_())