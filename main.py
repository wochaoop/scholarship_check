from utils.file_operations import open_file, open_folder, query_csv
from utils.ui_operations import create_window, create_text_widget, create_buttons


def main():
    root_window = create_window()
    output_text = create_text_widget(root_window)
    create_buttons(root_window, output_text, open_file, open_folder, query_csv)
    root_window.mainloop()


if __name__ == "__main__":
    main()
