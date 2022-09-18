import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QFileDialog, QLineEdit
import random
import logging


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.information_label = QLabel()     # common label for all pages
        self.question_components = []
        self.question = {}
        self.questions = {}
        self.file_name = ""
        self.start_page()                     # run the start page

    # pages
    def start_page(self):
        layout = QVBoxLayout()

        self.change_information_label("", "", "")

        button = QPushButton("Add new questions")
        button.pressed.connect(self.question_adding_page)
        layout.addWidget(button)

        button = QPushButton("Quiz Page")
        button.pressed.connect(self.quiz_page)
        layout.addWidget(button)

        layout.addWidget(self.information_label)
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def question_adding_page(self):
        layout = QVBoxLayout()               # page layout
        self.question_components = []        # clean up the question for next question

        temp_layout = QHBoxLayout()          # temp layout for union label + editline in 1 row ex: question: [edit line]

        button = QPushButton("Choose File")
        button.pressed.connect(self.open_file)
        layout.addWidget(button)

        label = QLabel("question: ")
        temp_layout.addWidget(label)

        editable_line = QLineEdit()
        self.question_components.append(editable_line)
        temp_layout.addWidget(editable_line)
        layout.addLayout(temp_layout)

        for i in range(4):                   # 4*edit line for adding choices
            abcd = {0: "a", 1: "b", 2: "c", 3: "d"}

            temp_layout = QHBoxLayout()
            label = QLabel(f"{abcd[i]}")
            temp_layout.addWidget(label)

            editable_line = QLineEdit()
            self.question_components.append(editable_line)
            temp_layout.addWidget(editable_line)
            layout.addLayout(temp_layout)

        temp_layout = QHBoxLayout()
        label = QLabel("correct answer (a,b,c,d):")
        temp_layout.addWidget(label)

        editable_line = QLineEdit()
        self.question_components.append(editable_line)
        temp_layout.addWidget(editable_line)
        layout.addLayout(temp_layout)

        temp_layout = QHBoxLayout()
        label = QLabel("explanation:")
        temp_layout.addWidget(label)

        editable_line = QLineEdit()
        self.question_components.append(editable_line)
        temp_layout.addWidget(editable_line)
        layout.addLayout(temp_layout)

        button = QPushButton("Submit the question")
        button.pressed.connect(self.submit_question)
        self.question_components.append(button)
        layout.addWidget(button)

        layout.addWidget(self.information_label)

        button = QPushButton("Back")
        button.pressed.connect(self.start_page)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def quiz_page(self):

        self.file_name = ""

        layout = QVBoxLayout()

        button = QPushButton("Choose File")
        button.pressed.connect(self.open_file)
        layout.addWidget(button)

        layout.addWidget(self.information_label)

        button = QPushButton("Start Quiz")
        button.pressed.connect(self.question_page)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def question_page(self):

        self.change_information_label("", "", "")

        if not self.file_name:
            text = "You need to specify file first!"
            logging.warning(text)
            self.change_information_label(text, "red", "12")
            return 0

        layout = QVBoxLayout()

        self.get_question()

        question = self.question
        options = question["options"]
        answer = question["answer"]
        question_text = question["question_text"]

        label = QLabel(question_text, self)
        layout.addWidget(label)
        print(f"Correct answer is: {answer}")
        for i in options:  # buttons for options
            for key, value in i.items():

                widget = QPushButton(f"{key}: {value}")
                widget.pressed.connect(self.false_answer)
                if key == answer:
                     widget.pressed.connect(self.correct_answer)
                layout.addWidget(widget)

        layout.addWidget(self.information_label)


        button = QPushButton(f"Show Explanation")
        button.pressed.connect(self.explain)
        layout.addWidget(button)

        button = QPushButton(f"Next")
        button.pressed.connect(self.question_page)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    # functions
    def open_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                   "All Files (*);;Python Files (*.py)", options=options)
        if self.file_name:
            print("loading file")
            self.load_file()

    def get_question(self):
        if len(self.questions) == 0:
            print("questions finished")
            sys.exit(1)

        random_key = random.choice(list(self.questions.keys()))
        question = self.questions[random_key]
        del self.questions[random_key]
        self.question = question

    def submit_question(self):
        if not self.file_name:
            self.change_information_label("You need to choose a file for either add new questions or start the quiz", "red", "12")
            return 0

        for component in self.question_components:
            if not component.text():
                self.change_information_label("You need to add all parts of the question!", "red", "12")
                return 0

        question_text = self.question_components[0].text()

        abcd = {0: "a", 1: "b", 2: "c", 3: "d"}
        options = []

        for i in range(4):
            options.append({abcd[i]: self.question_components[i + 1].text()})   # building 'a': 'answer_text'

        answer = self.question_components[5].text()
        explanation = self.question_components[6].text()

        number_of_questions = len(self.questions)

        self.question = {'question_text': question_text, 'options': options, 'answer': answer, 'explanation': explanation}
        self.questions[str(number_of_questions)] = self.question
        self.write_to_file() # write file
        self.information_label.setText("Submitted!")
        self.information_label.setStyleSheet("color: green; font: bold 12px;")
        self.question_adding_page() # re render adding page

    def load_file(self):
        file_name = self.file_name

        if file_name:
            try:
                with open(file_name, "r") as f:
                    self.questions = json.load(f)
            except:
                logging.warning(f"file: {file_name} is empty!")
        else:
            logging.warning("Filename is empty")

    def write_to_file(self):
        file_name = self.file_name
        if file_name:
            with open(file_name, 'w') as f:
                json.dump(self.questions, f)

    def correct_answer(self):
        self.change_information_label("Correct!", "green", "12")

    def false_answer(self):
        self.change_information_label("False!", "red", "12")

    def change_information_label(self, text, color, size):
        self.information_label.setText(text)
        self.information_label.setStyleSheet(f"color: {color}; font: bold {size}px;")

    def explain(self):
        explanation = self.question["explanation"]
        self.change_information_label(explanation, "black", "12")
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
