import sys
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QHBoxLayout, \
    QLineEdit,  QComboBox
import random
import logging
from os import listdir
from os.path import isfile, join
from datetime import datetime


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.information_label = QLabel()     # common label for all pages
        self.quiz_dir = "quizzes"
        self.result_dir = "results"
        self.file_extension = "json"
        self.question_components = []
        self.question = {}
        self.questions = {}
        self.total_questions = 0
        self.files = [f.split(".")[0] for f in listdir(self.quiz_dir) if isfile(join(self.quiz_dir, f))]    # get names only
        self.results = [f for f in listdir(self.result_dir) if isfile(join(self.result_dir, f))]  # get names only
        self.file_name = ""
        self.score = 0
        self.current_question = None
        self.report = {"correct_answers": [], "false_answers": []}
        self.start_page()                     # run the start page

    # pages
    def start_page(self):

        # reset file name
        self.file_name = ""
        layout = QVBoxLayout()

        self.change_information_label("", "", "")

        combo = QComboBox()
        combo.addItem("choose test!")
        combo.addItems(self.files)
        combo.activated[str].connect(self.combo_choose_quiz)
        layout.addWidget(combo)

        button = QPushButton("Add new questions")
        button.pressed.connect(self.question_adding_page)
        layout.addWidget(button)

        button = QPushButton("Start the quiz")
        button.pressed.connect(self.question_page)
        layout.addWidget(button)

        button = QPushButton("Retake from false answers")
        button.pressed.connect(self.retake_false_questions)
        layout.addWidget(button)

        layout.addWidget(self.information_label)
        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def question_adding_page(self):

        if not self.check(file=True):
            return 0

        layout = QVBoxLayout()               # page layout
        self.question_components = []        # clean up the question for next question

        temp_layout = QHBoxLayout()          # temp layout for union label + editline in 1 row ex: question: [edit line]

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

    def question_page(self):

        self.change_information_label("", "", "")

        if not self.check(file=True):
            return 0

        layout = QVBoxLayout()

        have_questions = self.get_question()

        question = self.question
        options = question["options"]
        answer = question["answer"]
        question_text = question["question_text"]

        label = QLabel(question_text, self)
        layout.addWidget(label)
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

        if not have_questions:
            button.pressed.connect(self.quiz_finish_page)
            button.setText("Finish Quiz")

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def retake_false_questions(self):

        self.reset_file_name()

        layout = QVBoxLayout()
        layout.addWidget(self.information_label)
        widget = QWidget()
        widget.setLayout(layout)

        combo = QComboBox()
        combo.addItem("choose result!")
        combo.addItems(self.results)
        combo.activated[str].connect(self.combo_retake_quiz)
        layout.addWidget(combo)

        button = QPushButton("Start the quiz")
        button.pressed.connect(self.question_page)
        layout.addWidget(button)

        self.setCentralWidget(widget)

    def quiz_finish_page(self):
        layout = QVBoxLayout()
        layout.addWidget(self.information_label)
        widget = QWidget()
        widget.setLayout(layout)

        button = QPushButton(f"Finish")
        button.pressed.connect(self.finish)
        layout.addWidget(button)

        self.setCentralWidget(widget)
        self.change_information_label(f"Quiz finished :) Your score is: {self.score}/{self.total_questions}", "green", "12")

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    # functions
    def combo_choose_quiz(self, text):
        self.file_name = text
        self.load_quiz()

    def combo_retake_quiz(self, text):
        if text != "choose result!" and text:
            file_name = f"{self.result_dir}/{text}"
            correct_answers = []
            try:
                with open(file_name, "r") as f:
                    report = json.load(f)
                correct_answers = report["correct_answers"]
            except:
                logging.error(f"Could not load result file: {file_name}")

            self.file_name = text.split(".")[0]
            self.load_quiz()
            for correct_answer in correct_answers:
                del self.questions[correct_answer]

            self.total_questions = len(self.questions)

    def get_question(self):

        if len(self.questions) == 0:
            self.change_information_label("Quiz finished :)", "green", "12")
            return False
        else:
            random_key = random.choice(list(self.questions.keys()))
            question = self.questions[random_key]
            self.current_question = random_key
            del self.questions[random_key]
            self.question = question
            return True

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

        # extract components of question
        self.question = {'question_text': question_text, 'options': options, 'answer': answer, 'explanation': explanation}
        self.questions[str(number_of_questions)] = self.question

        # write file
        self.write_to_file(f"{self.quiz_dir}/{self.file_name}.{self.file_extension}", self.questions)

        self.change_information_label("Submitted!", "green", "12")

        # re render adding page
        self.question_adding_page()

    # load file, always json
    def load_quiz(self):
        file_name = f"{self.quiz_dir}/{self.file_name}.{self.file_extension}"

        if file_name:
            try:
                with open(file_name, "r") as f:
                    self.questions = json.load(f)
                self.total_questions = len(self.questions)
            except:
                logging.warning(f"There is a problem loading file: {file_name}")

        else:
            logging.warning("Filename is empty")

    # write to file always json
    def write_to_file(self, path: str, content: dict):
        try:
            with open(path, 'w') as f:
                json.dump(content, f)
        except:
            logging.error(f"could not write {self.file_name} to file {path}")

    # actions for correct answer
    def correct_answer(self):
        self.change_information_label("Correct!", "green", "12")
        self.report["correct_answers"].append(self.current_question)
        self.score += 1

    # actions for false answer
    def false_answer(self):
        self.report["false_answers"].append(self.current_question)
        self.change_information_label("False!", "red", "12")

    def change_information_label(self, text, color, size):
        self.information_label.setText(text)
        self.information_label.setStyleSheet(f"color: {color}; font: bold {size}px;")

    # render current questions explanation
    def explain(self):
        explanation = self.question["explanation"]
        self.change_information_label(explanation, "black", "12")

    def reset_file_name(self):
        self.file_name = None

    # checks will be implemented under this function
    def check(self, file: bool):
        if file:
            if not self.file_name or self.file_name == "choose test!":
                text = "You need to specify file first!"
                logging.warning(text)
                self.change_information_label(text, "red", "12")
                return False
            else:
                return True

    # save the result and exit
    def finish(self):
        # <results_dir>/<test_name>_<year-month-day-seconds>.<file_extension>
        self.write_to_file(f"{self.result_dir}/{self.file_name.split(',')[0]}.{datetime.today().strftime('%Y-%m-%d-%H-%M-%S')}.{self.file_extension}", self.report)
        sys.exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()
