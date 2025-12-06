import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
import os
import sys

# Automatically find the Data directory relative to the current script
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")

class F1TeammateNetwork:
    """
    F1 Driver Teammate Network Analysis Class.
    Responsible for loading CSV data, building the network graph, and providing user interaction interfaces.
    """
    
    def __init__(self, data_path):
        self.data_path = data_path
        self.graph = nx.Graph()
        # Data mapping dictionaries
        self.drivers = {}        # ID -> Name
        self.driver_names = {}   # Name (lowercase) -> ID
        self.constructors = {}   # ID -> TeamName
        self.constructor_names = {} # TeamName (lowercase) -> ID
        self.races = {}          # raceId -> Year
        
        # Core dataframe
        self.results_df = None

    def _get_path(self, filename):
        """Helper function: Construct full file path"""
        return os.path.join(self.data_path, filename)

    def load_data(self):
        """
        Read and clean all necessary CSV files.
        Integrate Drivers, Constructors, Races, and Results datasets.
        """
        print(f"Loading data from {self.data_path}...")

        # 1. Load Drivers (Nodes)
        try:
            drivers_path = self._get_path('drivers.csv')
            drivers_df = pd.read_csv(drivers_path, encoding='utf-8')
            drivers_df['full_name'] = drivers_df['forename'] + " " + drivers_df['surname']
            
            for _, row in drivers_df.iterrows():
                d_id = row['driverId']
                name = row['full_name']
                self.drivers[d_id] = name
                self.driver_names[name.lower()] = d_id
                # Add node, including nationality as an attribute
                self.graph.add_node(d_id, label=name, nationality=row['nationality'])
        except Exception as e:
            print(f"Error: Unable to load drivers.csv - {e}")
            sys.exit(1)

        # 2. Load Constructors (Used to define relationship context)
        try:
            const_path = self._get_path('constructors.csv')
            const_df = pd.read_csv(const_path, encoding='utf-8')
            for _, row in const_df.iterrows():
                c_id = row['constructorId']
                name = row['name']
                self.constructors[c_id] = name
                self.constructor_names[name.lower()] = c_id
        except Exception as e:
            print(f"Warning: Unable to load constructors.csv - {e}")

        # 3. Load Schedule (Used to retrieve years)
        try:
            races_path = self._get_path('races.csv')
            races_df = pd.read_csv(races_path, encoding='utf-8')
            # Create raceId -> Year mapping
            self.races = pd.Series(races_df.year.values, index=races_df.raceId).to_dict()
        except Exception as e:
            print(f"Warning: Unable to load races.csv - {e}")

        # 4. Load Results (Source of Edges)
        try:
            results_path = self._get_path('results.csv')
            # Read only necessary columns to optimize performance
            self.results_df = pd.read_csv(results_path, usecols=['raceId', 'driverId', 'constructorId'])
            print("Basic data loading complete, building graph network...")
            self.build_graph()
        except Exception as e:
            print(f"Error: Unable to load results.csv - {e}")
            sys.exit(1)

    def build_graph(self):
        """
        Build graph structure based on race results.
        Logic: If drivers raced for the same team (constructorId) in the same race (raceId), they are considered teammates.
        """
        # Merge year information into results
        self.results_df['year'] = self.results_df['raceId'].map(self.races)

        # Group by Race (raceId) and Team (constructorId)
        grouped = self.results_df.groupby(['raceId', 'constructorId'])
        
        edge_batch = []
        
        # Iterate through every team roster for every race
        for (race_id, const_id), group in grouped:
            driver_ids = group['driverId'].tolist()
            year = self.races.get(race_id, "Unknown")

            # If a team has more than 1 driver in this race, create pairwise connections
            if len(driver_ids) > 1:
                for d1, d2 in combinations(driver_ids, 2):
                    edge_batch.append((d1, d2, year))

        print(f"Processed {len(edge_batch)} partnership records, merging weights...")

        # Update graph edges
        for d1, d2, year in edge_batch:
            if self.graph.has_edge(d1, d2):
                self.graph[d1][d2]['weight'] += 1
                self.graph[d1][d2]['years'].add(year) # Record set of years raced together
            else:
                self.graph.add_edge(d1, d2, weight=1, years={year})

        print(f"Network built successfully! Contains {self.graph.number_of_nodes()} drivers and {self.graph.number_of_edges()} teammate relationships.")

    # --- Interaction Implementation ---

    def _find_id_by_name(self, name, lookup_dict):
        """Simple fuzzy search helper function"""
        query = name.lower().strip()
        # 1. Exact match
        if query in lookup_dict:
            return lookup_dict[query]
        # 2. Partial match
        matches = [k for k in lookup_dict.keys() if query in k]
        if len(matches) == 1:
            return lookup_dict[matches[0]]
        elif len(matches) > 1:
            print(f"Multiple matches found: {', '.join(matches[:5])}...")
            return None
        return None

    def find_driver_teammates(self):
        """Interaction Mode 1: Query all teammates of a specific driver"""
        query = input("\nEnter driver name (e.g., 'Schumacher'): ")
        d_id = self._find_id_by_name(query, self.driver_names)
        
        if d_id:
            driver_name = self.drivers[d_id]
            print(f"\nFinding teammates for {driver_name}...")
            
            if d_id not in self.graph:
                print("This driver has no teammate records in the network.")
                return

            teammates = []
            for neighbor in self.graph.neighbors(d_id):
                data = self.graph[d_id][neighbor]
                t_name = self.drivers[neighbor]
                count = data['weight']
                years = sorted(list(data['years']))
                year_str = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0])
                teammates.append((t_name, count, year_str))
            
            # Sort by number of races together (descending)
            teammates.sort(key=lambda x: x[1], reverse=True)
            
            print(f"{'Teammate Name':<25} | {'Count':<5} | {'Years'}")
            print("-" * 50)
            for t_name, count, yr in teammates:
                print(f"{t_name:<25} | {count:<5} | {yr}")
        else:
            print("Driver not found.")

    def find_shortest_path(self):
        """Interaction Mode 2: Find the shortest path between two drivers"""
        n1 = input("\nEnter first driver: ")
        id1 = self._find_id_by_name(n1, self.driver_names)
        if not id1: return

        n2 = input("Enter second driver: ")
        id2 = self._find_id_by_name(n2, self.driver_names)
        if not id2: return

        try:
            path = nx.shortest_path(self.graph, source=id1, target=id2)
            names = [self.drivers[uid] for uid in path]
            print(f"\nConnection Path ({len(path)-1} degrees of separation):")
            print(" -> ".join(names))
        except nx.NetworkXNoPath:
            print("No path connection between these two drivers.")

    def show_top_connected(self):
        """Interaction Mode 3: Network Centrality Analysis"""
        print("\nCalculating the most connected drivers in the network...")
        # Use Degree Centrality
        centrality = nx.degree_centrality(self.graph)
        top_10 = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("\n--- F1 Social Hub TOP 10 (Most Teammates) ---")
        for i, (d_id, score) in enumerate(top_10, 1):
            degree = self.graph.degree(d_id)
            print(f"#{i} {self.drivers[d_id]} ({degree} distinct teammates)")

    def filter_by_team(self):
        """Interaction Mode 4: Filter by Team (Show drivers who raced for this team)"""
        # Note: This feature requires querying raw data because the graph only stores 'teammate' relations, not 'team' attributes on edges
        # For demonstration, we dynamically query results_df
        t_query = input("\nEnter team name (e.g., 'Ferrari', 'McLaren'): ")
        c_id = self._find_id_by_name(t_query, self.constructor_names)
        
        if c_id:
            team_name = self.constructors[c_id]
            print(f"\nFinding drivers who raced for {team_name}...")
            
            # Filter
            drivers_in_team = self.results_df[self.results_df['constructorId'] == c_id]['driverId'].unique()
            
            print(f"Found {len(drivers_in_team)} drivers. Top 20:")
            names = [self.drivers[d] for d in drivers_in_team if d in self.drivers]
            print(", ".join(names[:20]))
            if len(names) > 20: print("...")
        else:
            print("Team not found.")

    def visualize_ego(self):
        """Interaction Mode 5: Visualization"""
        query = input("\nEnter central driver to visualize: ")
        d_id = self._find_id_by_name(query, self.driver_names)
        
        if d_id:
            # Extract subgraph
            neighbors = list(self.graph.neighbors(d_id))
            if not neighbors:
                print("This driver has no teammates, cannot plot.")
                return
            
            nodes_to_draw = [d_id] + neighbors
            subgraph = self.graph.subgraph(nodes_to_draw)
            
            plt.figure(figsize=(12, 10))
            # Layout algorithm
            pos = nx.spring_layout(subgraph, k=0.5, seed=42)
            
            # Draw
            nx.draw_networkx_nodes(subgraph, pos, node_size=300, node_color='#add8e6')
            nx.draw_networkx_nodes(subgraph, pos, nodelist=[d_id], node_size=600, node_color='#ff6347') # Highlight protagonist in red
            
            nx.draw_networkx_edges(subgraph, pos, alpha=0.3)
            nx.draw_networkx_labels(subgraph, pos, labels={n: self.drivers[n] for n in nodes_to_draw}, font_size=8)
            
            plt.title(f"Network of {self.drivers[d_id]}")
            plt.axis('off')
            print("Displaying chart... Please close the chart window to continue.")
            plt.show()

    def run(self):
        """Main program loop"""
        self.load_data()
        
        while True:
            print("\n" + "="*40)
            print("F1 Teammate Network Analysis Tool (Final Project)")
            print("="*40)
            print("1. [Node Info] Find teammates and years for a specific driver")
            print("2. [Path] Find shortest relationship chain between two drivers")
            print("3. [Ranking] View drivers with the most connections")
            print("4. [Filtering] View drivers who raced for a specific team")
            print("5. [Viz] Visualize driver's social circle")
            print("6. Exit")
            
            choice = input("\nPlease select an option (1-6): ")
            
            if choice == '1': self.find_driver_teammates()
            elif choice == '2': self.find_shortest_path()
            elif choice == '3': self.show_top_connected()
            elif choice == '4': self.filter_by_team()
            elif choice == '5': self.visualize_ego()
            elif choice == '6': break
            else: print("Invalid input")

if __name__ == "__main__":
    # Instantiate and run
    # Ensure DATA_DIR variable points to the folder containing your CSV files
    app = F1TeammateNetwork(DATA_DIR)
    app.run()