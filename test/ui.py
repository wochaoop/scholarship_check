import tkinter as tk
import main as main


class AppWindow(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("奖学金核查脚本")

        # 获取用户的屏幕尺寸
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # 计算窗口的位置
        x = (screen_width - 800) / 2
        y = (screen_height - 600) / 2
        self.geometry(f"800x600+{int(x)}+{int(y)}")

        # 加载项目中的图片文件
        self.original_image = tk.PhotoImage(file="upload.png")
        self.resized_image = self.original_image.subsample(6, 6)

        # 创建带有图片的按钮
        self.button = tk.Button(self, text="上传汇总文件", image=self.resized_image, compound=tk.LEFT, command=lambda: main.open_gpa_files())
        self.button.pack()


if __name__ == "__main__":
    app = AppWindow()
    app.mainloop()
