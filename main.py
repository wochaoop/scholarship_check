import warnings
from concurrent.futures import ThreadPoolExecutor
from utils.file_operations import open_file, open_folder, query_excel
from utils.ui_operations import create_window, create_text_widget, create_buttons


def main():
    warnings.filterwarnings('ignore', category=UserWarning)
    root_window = create_window()
    output_text = create_text_widget(root_window)

    # 创建一个线程池执行器
    executor = ThreadPoolExecutor(max_workers=3)

    # 将函数和参数传递给executor.submit，它会返回一个Future对象
    # 这个对象代表了一个计算尚未完成的操作
    create_buttons(root_window, output_text,
                   lambda _: executor.submit(open_file, output_text),
                   lambda _: executor.submit(open_folder, output_text),
                   lambda _: executor.submit(query_excel, output_text))

    root_window.mainloop()

    # 确保所有的任务都已经完成并且线程池已经被关闭
    executor.shutdown(wait=True)


if __name__ == "__main__":
    main()
