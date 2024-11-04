import sys
from PyQt6.QtWidgets import QApplication
from concurrent.futures import ThreadPoolExecutor
from utils.file_operations import open_file, open_folder, query_excel
from utils.ui_operations import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()

    # Create a thread pool executor
    executor = ThreadPoolExecutor(max_workers=3)

    # Connect buttons to their respective functions using the executor
    window.button_open_file.clicked.connect(lambda: executor.submit(open_file, window.text_edit))
    window.button_open_folder.clicked.connect(lambda: executor.submit(open_folder, window.text_edit))
    window.button_query_csv.clicked.connect(lambda: executor.submit(query_excel, window.text_edit))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
