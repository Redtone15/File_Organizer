import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import threading
import threading


class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("文件整理工具")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("SimHei", 10))
        self.style.configure("TButton", font=("SimHei", 10))
        self.style.configure("TRadiobutton", font=("SimHei", 10))
        self.style.configure("TCheckbutton", font=("SimHei", 10))

        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 源目录选择
        ttk.Label(self.main_frame, text="源文件目录:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_dir_var = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.source_dir_var, width=50).grid(row=0, column=1, pady=5)
        ttk.Button(self.main_frame, text="浏览...", command=self.select_source_dir).grid(row=0, column=2, padx=5,
                                                                                         pady=5)

        # 目标目录选择
        ttk.Label(self.main_frame, text="目标文件目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dest_dir_var = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.dest_dir_var, width=50).grid(row=1, column=1, pady=5)
        ttk.Button(self.main_frame, text="浏览...", command=self.select_dest_dir).grid(row=1, column=2, padx=5, pady=5)
        ttk.Label(self.main_frame, text="(可选，默认与源目录相同)").grid(row=2, column=1, sticky=tk.W)

        # 整理方式选择
        ttk.Label(self.main_frame, text="整理方式:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.organize_type = tk.StringVar(value="type")

        type_frame = ttk.Frame(self.main_frame)
        type_frame.grid(row=3, column=1, sticky=tk.W, pady=5)

        ttk.Radiobutton(type_frame, text="按文件类型", variable=self.organize_type,
                        value="type", command=self.update_time_options_visibility).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="按修改时间", variable=self.organize_type,
                        value="time", command=self.update_time_options_visibility).pack(side=tk.LEFT, padx=10)

        # 时间选项（只保留修改时间相关）
        self.time_frame = ttk.LabelFrame(self.main_frame, text="时间选项")
        self.time_frame.grid(row=4, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5, padx=5)

        ttk.Label(self.time_frame, text="日期格式:").pack(side=tk.LEFT, padx=(20, 5))
        self.date_format = tk.StringVar(value="YYYY-MM-DD")
        date_formats = ["YYYY-MM-DD", "DD-MM-YYYY", "YYYY-MM", "MM-YYYY"]
        date_format_combo = ttk.Combobox(self.time_frame, textvariable=self.date_format, values=date_formats,
                                         state="readonly", width=12)
        date_format_combo.pack(side=tk.LEFT, padx=5)

        # 整理按钮
        self.organize_btn = ttk.Button(self.main_frame, text="开始整理", command=self.start_organizing)
        self.organize_btn.grid(row=5, column=0, columnspan=3, pady=20)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=tk.W + tk.E, pady=10)

        # 状态标签
        self.status_var = tk.StringVar(value="准备就绪")
        ttk.Label(self.main_frame, textvariable=self.status_var).grid(row=7, column=0, columnspan=3, pady=5)

        # 配置列权重，使界面可伸缩
        self.main_frame.columnconfigure(1, weight=1)
        for i in range(8):
            self.main_frame.rowconfigure(i, weight=1)

        # 初始隐藏时间选项
        self.update_time_options_visibility()

    def select_source_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.source_dir_var.set(dir_path)
            # 如果目标目录为空，自动填充与源目录相同
            if not self.dest_dir_var.get():
                self.dest_dir_var.set(dir_path)

    def select_dest_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.dest_dir_var.set(dir_path)

    def update_time_options_visibility(self):
        """根据选择的整理方式显示或隐藏时间选项"""
        if self.organize_type.get() == "time":
            self.time_frame.grid()  # 显示时间选项
        else:
            self.time_frame.grid_remove()  # 隐藏时间选项

    def start_organizing(self):
        source_dir = self.source_dir_var.get()
        dest_dir = self.dest_dir_var.get() or source_dir

        if not source_dir:
            messagebox.showerror("错误", "请选择源文件目录")
            return

        if not os.path.isdir(source_dir):
            messagebox.showerror("错误", "源文件目录不存在")
            return

        if not os.path.isdir(dest_dir):
            messagebox.showerror("错误", "目标文件目录不存在")
            return

        # 禁用按钮，防止重复点击
        self.organize_btn.config(state="disabled")
        self.status_var.set("正在准备整理文件...")

        # 在新线程中执行整理操作，避免界面冻结
        threading.Thread(target=self.organize_files, args=(source_dir, dest_dir), daemon=True).start()

    def organize_files(self, source_dir, dest_dir):
        try:
            # 获取所有文件
            all_files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]
            total_files = len(all_files)

            if total_files == 0:
                self.root.after(0, lambda: messagebox.showinfo("提示", "源目录中没有文件"))
                self.root.after(0, lambda: self.reset_ui())
                return

            organized_count = 0

            for i, filename in enumerate(all_files):
                file_path = os.path.join(source_dir, filename)

                # 根据选择的方式创建目标文件夹
                if self.organize_type.get() == "type":
                    # 按文件类型整理
                    file_ext = os.path.splitext(filename)[1][1:].lower()  # 获取扩展名，不带点
                    if not file_ext:  # 没有扩展名的文件
                        folder_name = "无扩展名文件"
                    else:
                        folder_name = f"{file_ext}*文件"
                else:
                    # 按修改时间整理
                    timestamp = os.path.getmtime(file_path)
                    dt = datetime.fromtimestamp(timestamp)
                    date_format = self.date_format.get()

                    if date_format == "YYYY-MM-DD":
                        folder_name = dt.strftime("%Y-%m-%d")
                    elif date_format == "DD-MM-YYYY":
                        folder_name = dt.strftime("%d-%m-%Y")
                    elif date_format == "YYYY-MM":
                        folder_name = dt.strftime("%Y-%m")
                    elif date_format == "MM-YYYY":
                        folder_name = dt.strftime("%m-%Y")

                # 创建目标文件夹
                target_folder = os.path.join(dest_dir, folder_name)
                os.makedirs(target_folder, exist_ok=True)

                # 移动文件
                target_path = os.path.join(target_folder, filename)
                # 如果文件已存在，添加编号
                counter = 1
                while os.path.exists(target_path):
                    name, ext = os.path.splitext(filename)
                    target_path = os.path.join(target_folder, f"{name}_{counter}{ext}")
                    counter += 1

                shutil.move(file_path, target_path)
                organized_count += 1

                # 更新进度条
                progress = (i + 1) / total_files * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))
                self.root.after(0, lambda f=filename: self.status_var.set(f"正在整理: {f}"))

            # 完成后显示结果
            self.root.after(0,
                            lambda c=organized_count: messagebox.showinfo("完成", f"文件整理完成！共整理了 {c} 个文件"))
        except Exception as e:
            self.root.after(0, lambda err=str(e): messagebox.showerror("错误", f"整理过程中发生错误: {err}"))
        finally:
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.progress_var.set(0)
        self.status_var.set("准备就绪")
        self.organize_btn.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
