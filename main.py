import tkinter as tk
import tkinter.filedialog

import pandas as pd
from matplotlib import pyplot as plt


class SettingsWindow(tk.Toplevel):
    COLUMN_NAME_MAX_SIZE = 40

    def __init__(self, master, file_name):
        super().__init__(master)

        """Load data"""
        self.file_name = file_name
        self.data = pd.read_csv(self.file_name, low_memory=False)

        """Open new window for settings"""
        self.title("Dataset settings")
        self.iconbitmap(self.iconbitmap("assets/icon.ico"))
        self.resizable(False, False)
        self.configure(padx=10, pady=10)
        self.grid_rowconfigure(index=1, minsize=5)

        """Setup labelframe"""
        label_frame = tk.LabelFrame(master=self, text="Settings")
        label_frame.grid(row=0, sticky="ew")
        label_frame.configure(padx=5, pady=5)
        label_frame.grid_columnconfigure(index=0, minsize=300)

        """Setup 'Use header checkbox'"""
        self.use_header = tk.BooleanVar(self)
        self.use_header.set(True)
        header_checkbox = tk.Checkbutton(label_frame, variable=self.use_header, text="Use header",
                                         command=self.change_header_usage)
        header_checkbox.grid(row=0, sticky=tk.W)

        """Setup X axis data selector"""
        options_label = tk.Label(label_frame, text="Select X axis dataset:")
        options_label.grid(row=1, sticky=tk.W)
        self.x_axis_var = tk.StringVar(self)
        self.x_axis_var.set("Index")
        option_values = []
        for index, column in enumerate(self.data.columns):
            option_values.append("[{}] {}".format(index, column[:self.COLUMN_NAME_MAX_SIZE]))
        self.options = tk.OptionMenu(label_frame, self.x_axis_var, self.x_axis_var.get(), *option_values)
        self.options.configure(wraplength=300)
        self.options.grid(row=2, sticky="ew")

        """Setup column selection list box"""
        listbox_label = tk.Label(label_frame, text="Select Y axis datasets:")
        listbox_label.grid(row=3, sticky=tk.W)
        self.listbox = tk.Listbox(label_frame, height=10, selectmode=tk.MULTIPLE)
        self.load_listbox()
        self.listbox.grid(row=4, sticky="ew")

        """Setup submit button"""
        submit = tk.Button(master=self, text='Apply', pady=5, padx=10, command=self.create_plot)
        submit.grid(row=2, sticky=tk.E)

    @staticmethod
    def on_pick(event, figure, legend_map):
        """Get legend and line"""
        legend_element = event.artist
        line = legend_map[legend_element]

        """Change visibility"""
        visible = not line.get_visible()
        line.set_visible(visible)
        for key, value in legend_map.items():
            if value == line:
                key.set_alpha(1.0 if visible else 0.2)

        """Redraw the figure"""
        figure.canvas.draw()

    def create_plot(self):
        """Create plot and add lines"""
        figure = plt.figure()
        plt.subplots_adjust(0.05, 0.05, 0.99, 0.99)
        lines = []
        x_data = self.data.index
        if self.x_axis_var.get() != "Index":
            x_data = self.data.iloc[:, self.get_index(self.x_axis_var.get())]
        for index in self.listbox.curselection():
            line, = plt.plot(x_data, self.data.iloc[:, index], label=self.listbox.get(index))
            lines.append(line)

        """Map lines to legend entries and register legend pick event"""
        legend = plt.legend(prop={'size': 6})
        legend_map = {}
        for legend_line, line in zip(legend.get_lines(), lines):
            legend_line.set_picker(True)
            legend_map[legend_line] = line
        for legend_text, line in zip(legend.get_texts(), lines):
            legend_text.set_picker(True)
            legend_map[legend_text] = line

        figure.canvas.mpl_connect('pick_event', lambda event: self.on_pick(event, figure, legend_map))

        """Show plot"""
        plt.get_current_fig_manager().resize(1600, 900)
        plt.show()

        """Destroy settings window"""
        self.destroy()

    def change_header_usage(self):
        """Reload data"""
        if self.use_header.get():
            self.data = pd.read_csv(self.file_name, low_memory=False)
        else:
            self.data = pd.read_csv(self.file_name, header=None, names=[str(i) for i in range(len(self.data.columns))],
                                    low_memory=False)

        """Refresh the content of the input fields"""
        self.listbox.delete(0, self.listbox.size())
        self.load_listbox()

        self.x_axis_var.set("Index")
        self.options["menu"].delete(1, "end")
        for index, column in enumerate(self.data.columns):
            label_value = "[{}] {}".format(index, column[:self.COLUMN_NAME_MAX_SIZE])
            self.options['menu'].add_command(label=label_value, command=tk._setit(self.x_axis_var, label_value))

    def load_listbox(self):
        for index, column in enumerate(self.data.columns):
            self.listbox.insert(index, "[{}] {}".format(index, column[:self.COLUMN_NAME_MAX_SIZE]))

    @staticmethod
    def get_index(string: str) -> int:
        return int(string[string.find("[") + 1: string.find("]")])


class Application(tk.Tk):
    def __init__(self):
        """Window initialization"""
        super().__init__()
        self.title("CSV Viewer")
        self.iconbitmap("assets/icon.ico")
        self.geometry("300x100+10+10")
        self.resizable(False, False)
        self.configure(background='grey')
        self.protocol("WM_DELETE_WINDOW", self.close_all)

        """Label"""
        button = tk.Button(text='Load CSV', font=("Arial", 15), width=25, height=3, command=self.open_file)
        button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        """Setup matplotlib"""
        plt.ion()

    def open_file(self):
        file = tk.filedialog.askopenfile(mode='r', filetypes=[("CSV Files", "*.csv")])
        if file is not None:
            SettingsWindow(self, file.name)

    def close_all(self):
        plt.close("all")
        self.destroy()


if __name__ == '__main__':
    app = Application()
    app.mainloop()
