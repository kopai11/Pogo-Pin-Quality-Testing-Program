import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from collections import defaultdict
import threading
import time
import os

class PinResistanceApp:
    def __init__(self, master):
        self.master = master
        master.title("Pin Resistance Test Monitor")
        master.geometry("1200x800")

        style = ttk.Style()
        style.configure('TNotebook.Tab', font = ('', 10))
        
        self.notebook= ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.setting_page = ttk.Frame(self.notebook)
        self.notebook.add(self.setting_page, text="Setting" )

        self.graph_page = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_page, text="Graph Visualization")
        
        # Data variables
        self.file_path = None
        self.window_size = 10  # Default to showing 10 data points at a time
        self.y_max = 20  # Default max R-Value (mΩ)
        self.last_file_size = 0
        self.running = False
        self.category_map = {
            "0%": 10, "25%": 2, "50%": 3, "75%": 4, "100%": 5,
            "-75%": 6, "-50%": 7, "-25%": 8, "-0%": 9
        }
        self.reverse_category_map = {v: k for k, v in self.category_map.items()}
        self.grouped_data = defaultdict(list)
        
        # Call setting page layout
        self.create_app()

        
    def create_app(self):
        
        #Create graph page frame
        self.graphing_frame = ttk.Frame(self.graph_page)
        self.graphing_frame.pack(fill = tk.X)
        
        #create graph page layout
        stop_frame = ttk.Frame(self.graphing_frame)
        
        stop_frame.pack(side = tk.TOP, fill = tk.X)
        
        
        
        self.stop_button = ttk.Button(stop_frame,
                                      text="Stop",
                                      command= lambda:(self.stop_monitoring(),
                                                       self.notebook.select(self.setting_page)),
                                      state=tk.DISABLED)
        self.stop_button.pack(side=tk.RIGHT, ipady=10)
        
        self.graph_frame = ttk.Frame(self.graphing_frame)
        self.graph_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Create setting page  frames
        self.control_frame = ttk.Frame(self.setting_page, padding="10")
        self.control_frame.pack()
        
        #create setting page layout
        title = ttk.Label(self.control_frame, text= 'Graph Configuration Setting',
                          font = ('', 20, 'bold'))
        title.pack(pady=20)

        style = ttk.Style()
        # Configure TLabelframe.Label specifically - note the capitalization
        style.configure('Custom.TCheckbutton', font=('', 14))
        
        # File selection
        file_frame = ttk.LabelFrame(self.control_frame, text="Data Source", padding="5")
        file_frame.pack(expand = True)
        
        ttk.Label(file_frame, text="Data File:",
                  font= ('',15)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_path_var,
                  width=60,font= ('',15)).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="Browse",
                   command=self.browse_file).grid(row=0, column=2, padx=5)
        
        # Graph controls
        control_panel = ttk.LabelFrame(self.control_frame, text="Graph Controls", padding="5")
        control_panel.pack( expand =True, pady = 30)
        
        ttk.Label(control_panel, text="TestCount Range:",
                  font= ('',15)).grid(row=0, column=0, sticky=tk.W, padx=5)
        self.window_size_var = tk.IntVar(value=10)
        ttk.Entry(control_panel, textvariable=self.window_size_var, width=5,
                  font= ('',14)).grid(row=0, column=1, padx=5)
        
        ttk.Label(control_panel, text="Max R-Value(mΩ):",
                  font= ('',15)).grid(row=1, column=0, sticky=tk.W, padx=5)
        self.y_max_var = tk.IntVar(value=20)
        ttk.Entry(control_panel, textvariable=self.y_max_var, width=5,
                  font= ('',14)).grid(row=1, column=1, padx=5)
                
        # Category selection
        category_frame = ttk.LabelFrame(self.control_frame, text="Categories", padding="5")
        category_frame.pack( expand = True, pady =30)
        
        self.category_vars = {}
        categories = ["0%", "25%", "50%", "75%", "100%", "-75%", "-50%", "-25%", "-0%"]
        
        for i, category in enumerate(categories):
            var = tk.BooleanVar(value=False)  # All NON-selected by default
            self.category_vars[category] = var
            ttk.Checkbutton(category_frame, text=category, variable=var,
                            style ='Custom.TCheckbutton').grid(row=i//3, column=i%3,
                                                               sticky=tk.W, padx=10)

        # Control buttons
        button_frame = ttk.Frame(self.control_frame, padding="5")
        button_frame.pack(side=tk.BOTTOM, expand = True, pady =20)
        
        self.start_button = ttk.Button(button_frame, text="Start Monitoring",
                                       command=lambda :(self.start_monitoring(),
                                                        self.notebook.select(self.graph_page)) )
        self.start_button.pack(side=tk.LEFT, ipady=10)
        
        
        
        # Initial plot setup
        self.fig = None
        self.axes = None
        self.canvas = None
        self.setup_plot()

    def browse_file(self):
        """Open file browser to select data file"""
        filename = filedialog.askopenfilename(
            title="Select Data File",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.file_path = filename

        
    def setup_plot(self):
        # Clear previous one
        if self.fig:
            
            plt.close(self.fig)

        #Get selected Categories
        selected_categories = [cat for cat, var in self.category_vars.items() if var.get()]
        if not selected_categories:
            selected_categories = ["0%"]
            
        #create fig
        self.fig, self.axes = plt.subplots(
            len(selected_categories), 1,
            figsize= (10, 2* len(selected_categories))
        )
        
        # Ensure axes is always a list
        self.axes = np.atleast_1d(self.axes)

        #set up plot
        for i, category in enumerate(selected_categories):
            self.axes[i].set_xlabel("Test Counts")
            self.axes[i].set_ylabel("R-Value (mΩ)")
            self.axes[i].set_ylim(0, self.y_max_var.get())
            self.axes[i].grid(True, linestyle='--', alpha=0.7)
            self.axes[i].text(
                0.95, 0.95, f"{category}", transform=self.axes[i].transAxes,
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(facecolor='white', alpha=0.5, edgecolor='black')
            )
        
        self.fig.tight_layout(pad=1.0)
        
        #Set in Tkinker
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(self.fig, master = self.graph_frame)
        self.canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
    
    def start_monitoring(self):
        if not self.file_path_var.get():
            messagebox.showwarning('Warning', 'Please select data file!')
            return

        #User update configuration
        self.window_size = self.window_size_var.get()
        self.y_max = self.y_max_var.get()

        #setup plot base on update
        self.setup_plot()

        #load initial data
        if not self.load_initial_data():
            return

        #get initial file for monitoring
        self.last_file_size = os.path.getsize(self.file_path)

        #Monitoring thread
        self.running = True
        self.monitor_thread = threading.Thread(target = self.monitor_data_file, daemon =True)
        self.monitor_thread.start()

        self.start_button.config(state =tk.DISABLED)
        self.stop_button.config(state = tk.NORMAL)

    def stop_monitoring(self):
        self.running = False

        self.start_button.config(state = tk.NORMAL)
        self.stop_button.config(state = tk.DISABLED)
    

    def load_initial_data(self):

        
        try:
            #read file
            with open(self.file_path, 'r') as file:
                lines = file.readlines()

            #clearprevious data
            self.grouped_data = defaultdict(list)

            #group data by category
            for line in lines:
                if len(line.strip()) > 0:
                    try:
                        x, y = map(float, line.strip().split(','))
                        x = int(x)
                        self.grouped_data[x].append(y)
                    except ValueError:
                        continue
            #update graph with data
            self.update_graph()

            return True
        except Exception as e:
            messagebox.showwarning('Error', f"Failed to read data: {e}")
            return False


    def monitor_data_file(self):
        while self.running:
            try:
                # Check for file changes
                current_size = os.path.getsize(self.file_path)
                
                if current_size != self.last_file_size:
                    self.last_file_size = current_size
                    # Load new data from file
                    with open(self.file_path, 'r') as file:
                        lines = file.readlines()
                    
                    # Clear and rebuild the data
                    self.grouped_data = defaultdict(list)
                    for line in lines:
                        if len(line.strip()) > 0:
                            try:
                                x, y = map(float, line.strip().split(','))
                                x = int(x)
                                self.grouped_data[x].append(y)
                            except ValueError:
                                continue
                    
                    # Update the graph with new data
                    self.update_graph()
                    
                # Sleep to avoid high CPU usage
                time.sleep(1)
                
            except Exception as e:
                print(f"Error monitoring file: {e}")
                time.sleep(5)

    def update_graph(self):

        try:
            selected_categories =[cat for cat, var in self.category_vars.items() if var.get()]
            if not selected_categories:
                return

            numeric_categories = [self.category_map[cat] for cat in selected_categories]

            cmap = plt.get_cmap('Set1')

            for i, category in enumerate(selected_categories):
                ax = self.axes[i]
                ax.clear()

                cat_value = self.category_map[category]
                y_values = self.grouped_data.get(cat_value, [])

                
                if y_values:
                    # Calculate the start and end indices for the sliding window
                    current_window_start = max(0, len(y_values) - self.window_size)
                    current_window_end = len(y_values)
                    filtered_values = y_values[current_window_start:current_window_end]
                    
                    # Adjust x-axis to show current window position
                    x_values = list(range(current_window_start + 1, current_window_end + 1))
                    
                    # Plot the data
                    color = cmap(i / max(1, len(selected_categories) - 1))
                    ax.plot(x_values, filtered_values, color=color)
                    
                    # Display current window range information
                    ax.text(
                        0.05, 0.05, f"TestCount range of {self.window_size}",
                        transform=ax.transAxes, fontsize=8, verticalalignment='bottom',
                        bbox=dict(facecolor='white', alpha=0.5)
                    )
                else:
                    ax.text(0.5, 0.5, f"No data for {category}",
                          horizontalalignment='center', verticalalignment='center',
                          transform=ax.transAxes)
                
                # Reset axes properties
                ax.set_ylim(0, self.y_max)
                if y_values:
                    ax.set_xlim(
                        max(1, current_window_start + 1),
                        current_window_end
                    )
                else:
                    ax.set_xlim(1, self.window_size)
                    
                ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
                ax.set_xlabel("Test Counts", fontsize=9)
                ax.set_ylabel("R-Value (mΩ)", fontsize=9)
                ax.grid(True, linestyle="--", alpha=0.7)
                ax.text(
                    0.95, 0.95, f"{category}", transform=ax.transAxes,
                    fontsize=10, verticalalignment='top', horizontalalignment='right',
                    bbox=dict(facecolor='white', alpha=0.5, edgecolor='black')
                )
            
            # Adjust layout and redraw
            self.fig.tight_layout(pad=1.0)
            
            # Use the main thread to update the canvas
            self.master.after(0, self._update_canvas)
            
        except Exception as e:
            print(f"Error updating graph: {e}")

    def _update_canvas(self):
        if self.canvas and hasattr(self, 'fig'):
            self.canvas.draw_idle()


def main():
    root = tk.Tk()
    app = PinResistanceApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
        
