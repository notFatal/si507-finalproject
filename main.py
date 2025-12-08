import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from itertools import combinations
import os
import sys

# Set data directory
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

class F1TeammateNetwork:
    """
    Backend Logic Class: Handles data processing and graph algorithms.
    (Modified from original main.py to return data instead of printing)
    """
    def __init__(self, data_path):
        self.data_path = data_path
        self.graph = nx.Graph()
        self.drivers = {}        # ID -> Name
        self.driver_names = {}   # Name (lowercase) -> ID
        self.constructors = {}   # ID -> TeamName
        self.constructor_names = {} # TeamName (lowercase) -> ID
        self.races = {}          # raceId -> Year
        self.results_df = None
        self.is_loaded = False

    def _get_path(self, filename):
        return os.path.join(self.data_path, filename)

    def load_data(self):
        try:
            # 1. Load Drivers
            drivers_path = self._get_path('drivers.csv')
            drivers_df = pd.read_csv(drivers_path, encoding='utf-8')
            drivers_df['full_name'] = drivers_df['forename'] + " " + drivers_df['surname']
            
            for _, row in drivers_df.iterrows():
                d_id = row['driverId']
                name = row['full_name']
                self.drivers[d_id] = name
                self.driver_names[name.lower()] = d_id
                self.graph.add_node(d_id, label=name, nationality=row['nationality'])

            # 2. Load Constructors
            const_path = self._get_path('constructors.csv')
            const_df = pd.read_csv(const_path, encoding='utf-8')
            for _, row in const_df.iterrows():
                c_id = row['constructorId']
                name = row['name']
                self.constructors[c_id] = name
                self.constructor_names[name.lower()] = c_id

            # 3. Load Races
            races_path = self._get_path('races.csv')
            races_df = pd.read_csv(races_path, encoding='utf-8')
            self.races = pd.Series(races_df.year.values, index=races_df.raceId).to_dict()

            # 4. Load Results & Build Graph
            results_path = self._get_path('results.csv')
            self.results_df = pd.read_csv(results_path, usecols=['raceId', 'driverId', 'constructorId'])
            self.build_graph()
            self.is_loaded = True
            return True, f"Loaded successfully: {self.graph.number_of_nodes()} drivers, {self.graph.number_of_edges()} relationships"
        except Exception as e:
            return False, f"Data load error: {str(e)}\nPlease check Data folder path."

    def build_graph(self):
        self.results_df['year'] = self.results_df['raceId'].map(self.races)
        grouped = self.results_df.groupby(['raceId', 'constructorId'])
        edge_batch = []
        
        for (race_id, const_id), group in grouped:
            driver_ids = group['driverId'].tolist()
            year = self.races.get(race_id, "Unknown")
            if len(driver_ids) > 1:
                for d1, d2 in combinations(driver_ids, 2):
                    edge_batch.append((d1, d2, year))

        for d1, d2, year in edge_batch:
            if self.graph.has_edge(d1, d2):
                self.graph[d1][d2]['weight'] += 1
                self.graph[d1][d2]['years'].add(year)
            else:
                self.graph.add_edge(d1, d2, weight=1, years={year})

    def find_id_by_name(self, name):
        query = name.lower().strip()
        if query in self.driver_names:
            return self.driver_names[query]
        matches = [k for k in self.driver_names.keys() if query in k]
        if len(matches) == 1:
            return self.driver_names[matches[0]]
        return None

    def find_team_id_by_name(self, name):
        query = name.lower().strip()
        if query in self.constructor_names:
            return self.constructor_names[query]
        matches = [k for k in self.constructor_names.keys() if query in k]
        if len(matches) == 1:
            return self.constructor_names[matches[0]]
        return None

    def get_teammates(self, d_id):
        if d_id not in self.graph: return []
        teammates = []
        for neighbor in self.graph.neighbors(d_id):
            data = self.graph[d_id][neighbor]
            t_name = self.drivers[neighbor]
            count = data['weight']
            years = sorted(list(data['years']))
            year_str = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0])
            teammates.append((t_name, count, year_str))
        teammates.sort(key=lambda x: x[1], reverse=True)
        return teammates

    def get_shortest_path(self, id1, id2):
        try:
            path = nx.shortest_path(self.graph, source=id1, target=id2)
            names = [self.drivers[uid] for uid in path]
            return names
        except nx.NetworkXNoPath:
            return None

    def get_top_connected(self, limit=10):
        centrality = nx.degree_centrality(self.graph)
        top_list = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:limit]
        result = []
        for d_id, score in top_list:
            degree = self.graph.degree(d_id)
            result.append((self.drivers[d_id], degree))
        return result

    def get_drivers_by_team(self, c_id):
        drivers_in_team = self.results_df[self.results_df['constructorId'] == c_id]['driverId'].unique()
        names = [self.drivers[d] for d in drivers_in_team if d in self.drivers]
        return sorted(names)

class F1GUI:
    def __init__(self, root, backend):
        self.root = root
        self.backend = backend
        self.root.title("F1 Teammate Network Analysis Tool")
        self.root.geometry("900x700")

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Status Bar
        self.status_var = tk.StringVar()
        self.status_var.set("Initializing...")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create Pages
        self.create_search_tab()
        self.create_path_tab()
        self.create_ranking_tab()
        self.create_team_tab()
        self.create_viz_tab()

        # Load Data after UI is ready
        self.root.after(100, self.init_data)

    def init_data(self):
        success, msg = self.backend.load_data()
        self.status_var.set(msg)
        if not success:
            messagebox.showerror("Error", msg)

    def create_search_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔍 Find Teammates")

        # Input Area
        input_frame = ttk.Frame(frame, padding=10)
        input_frame.pack(fill=tk.X)
        ttk.Label(input_frame, text="Driver Name (e.g., 'Schumacher'):").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(input_frame)
        self.search_entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.search_entry.bind('<Return>', lambda e: self.do_search_teammates())
        ttk.Button(input_frame, text="Search", command=self.do_search_teammates).pack(side=tk.LEFT)

        # Result Table
        cols = ("Name", "Races Together", "Years")
        self.search_tree = ttk.Treeview(frame, columns=cols, show='headings')
        self.search_tree.heading("Name", text="Teammate Name")
        self.search_tree.heading("Races Together", text="Races Together")
        self.search_tree.heading("Years", text="Years")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.search_tree.yview)
        self.search_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.search_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def do_search_teammates(self):
        name = self.search_entry.get()
        d_id = self.backend.find_id_by_name(name)
        
        # Clear table
        for i in self.search_tree.get_children():
            self.search_tree.delete(i)

        if not d_id:
            messagebox.showwarning("Not Found", "Driver not found, please try a different spelling.")
            return

        teammates = self.backend.get_teammates(d_id)
        driver_real_name = self.backend.drivers[d_id]
        self.status_var.set(f"Driver: {driver_real_name} - Found {len(teammates)} teammates")

        for tm in teammates:
            self.search_tree.insert("", tk.END, values=tm)

    def create_path_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔗 Shortest Path")

        input_frame = ttk.Frame(frame, padding=20)
        input_frame.pack(fill=tk.X)
        
        ttk.Label(input_frame, text="Driver A:").grid(row=0, column=0, padx=5, pady=5)
        self.path_entry1 = ttk.Entry(input_frame)
        self.path_entry1.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Driver B:").grid(row=1, column=0, padx=5, pady=5)
        self.path_entry2 = ttk.Entry(input_frame)
        self.path_entry2.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(input_frame, text="Calculate Path", command=self.do_find_path).grid(row=2, column=0, columnspan=2, pady=10)

        # Result Display
        self.path_text = tk.Text(frame, height=10, width=50, font=("Helvetica", 12))
        self.path_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def do_find_path(self):
        n1 = self.path_entry1.get()
        n2 = self.path_entry2.get()
        id1 = self.backend.find_id_by_name(n1)
        id2 = self.backend.find_id_by_name(n2)

        if not id1 or not id2:
            self.path_text.delete(1.0, tk.END)
            self.path_text.insert(tk.END, "Error: One or both drivers not found.")
            return

        path = self.backend.get_shortest_path(id1, id2)
        self.path_text.delete(1.0, tk.END)
        
        if path:
            result_str = f"Connection Path found ({len(path)-1} degrees of separation):\n\n"
            result_str += "  ⬇\n".join(path)
            self.path_text.insert(tk.END, result_str)
        else:
            self.path_text.insert(tk.END, "No social network connection between these two drivers.")

    def create_ranking_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏆 Top Networkers")

        btn_frame = ttk.Frame(frame, padding=10)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="Refresh Top 20", command=self.do_ranking).pack()

        cols = ("Rank", "Driver Name", "Unique Teammates")
        self.rank_tree = ttk.Treeview(frame, columns=cols, show='headings')
        self.rank_tree.heading("Rank", text="Rank")
        self.rank_tree.heading("Driver Name", text="Driver Name")
        self.rank_tree.heading("Unique Teammates", text="Unique Teammates")
        self.rank_tree.column("Rank", width=50, anchor='center')
        
        self.rank_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def do_ranking(self):
        for i in self.rank_tree.get_children():
            self.rank_tree.delete(i)
        
        top_list = self.backend.get_top_connected(limit=20)
        for idx, (name, count) in enumerate(top_list, 1):
            self.rank_tree.insert("", tk.END, values=(idx, name, count))

    def create_team_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🏎️ Team Filter")

        input_frame = ttk.Frame(frame, padding=10)
        input_frame.pack(fill=tk.X)
        ttk.Label(input_frame, text="Team Name (e.g., 'Ferrari'):").pack(side=tk.LEFT)
        self.team_entry = ttk.Entry(input_frame)
        self.team_entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)
        self.team_entry.bind('<Return>', lambda e: self.do_team_filter())
        ttk.Button(input_frame, text="Filter", command=self.do_team_filter).pack(side=tk.LEFT)

        # Listbox for results
        self.team_list = tk.Listbox(frame, font=("Helvetica", 11))
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.team_list.yview)
        self.team_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.team_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def do_team_filter(self):
        name = self.team_entry.get()
        c_id = self.backend.find_team_id_by_name(name)
        
        self.team_list.delete(0, tk.END)
        
        if not c_id:
            messagebox.showwarning("Not Found", "Team not found.")
            return
        
        drivers = self.backend.get_drivers_by_team(c_id)
        team_real_name = self.backend.constructors[c_id]
        self.status_var.set(f"Team: {team_real_name} - Found {len(drivers)} historical drivers")
        
        for d in drivers:
            self.team_list.insert(tk.END, d)

    def create_viz_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🕸️ Network Viz")

        ctrl_frame = ttk.Frame(frame, padding=10)
        ctrl_frame.pack(fill=tk.X)
        ttk.Label(ctrl_frame, text="Central Driver Name:").pack(side=tk.LEFT)
        self.viz_entry = ttk.Entry(ctrl_frame)
        self.viz_entry.pack(side=tk.LEFT, padx=10)
        self.viz_entry.bind('<Return>', lambda e: self.do_visualize())
        ttk.Button(ctrl_frame, text="Generate Graph", command=self.do_visualize).pack(side=tk.LEFT)

        # Plot area
        self.plot_frame = ttk.Frame(frame)
        self.plot_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = None

    def do_visualize(self):
        name = self.viz_entry.get()
        d_id = self.backend.find_id_by_name(name)
        
        if not d_id:
            messagebox.showwarning("Not Found", "Driver not found.")
            return

        # Clear previous plot
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        # Logic from visualize_ego
        neighbors = list(self.backend.graph.neighbors(d_id))
        if not neighbors:
            messagebox.showinfo("No Data", "This driver has no teammate records.")
            return

        nodes_to_draw = [d_id] + neighbors
        subgraph = self.backend.graph.subgraph(nodes_to_draw)
        
        # Create matplotlib figure
        fig = plt.figure(figsize=(6, 5), dpi=100)
        pos = nx.spring_layout(subgraph, k=0.5, seed=42)
        
        nx.draw_networkx_nodes(subgraph, pos, node_size=300, node_color='#add8e6')
        nx.draw_networkx_nodes(subgraph, pos, nodelist=[d_id], node_size=600, node_color='#ff6347')
        nx.draw_networkx_edges(subgraph, pos, alpha=0.3)
        
        # Extract labels
        labels = {n: self.backend.drivers[n] for n in nodes_to_draw}
        nx.draw_networkx_labels(subgraph, pos, labels=labels, font_size=8)
        
        plt.title(f"Network: {self.backend.drivers[d_id]}")
        plt.axis('off')

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        print(f"Error: Data directory not found at {DATA_DIR}")
        print("Please ensure this script is in the same folder as the 'Data' directory.")
    else:
        app = F1TeammateNetwork(DATA_DIR)
        root = tk.Tk()
        # Set icon if you have one, otherwise skip
        # root.iconbitmap('icon.ico') 
        gui = F1GUI(root, app)
        root.mainloop()