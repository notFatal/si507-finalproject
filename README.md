# SI 507 Final Project: F1 Driver Teammate Network Analysis

This project analyzes the social and competitive connections between Formula 1 drivers using a graph-based network model.  
Nodes represent drivers, and edges represent teammate relationships (drivers racing for the same constructor in the same race).  
The application includes a multi-tab GUI and supports multiple interactive analysis modes.

---

##  Project Overview

This project builds a weighted, undirected graph of F1 drivers and their teammate histories across all recorded races in the dataset (1950–2024).

You can use the program to:

- Search for a driver and list all teammates they have raced with  
- Compute shortest paths between two drivers  
- Display rankings of "most connected" drivers  
- Filter drivers by constructor/team  
- Generate network visualizations (ego-graphs)

The project integrates **four real datasets** and performs multi-source data merging and graph analytics.

---

##  Network Structure

### **Nodes (Drivers)**
- Each node represents an F1 driver (`driverId`)
- Attributes:
  - Full name
  - Nationality

### **Edges (Teammate Relationships)**
- An undirected edge is created between two drivers if:
  - They raced in the *same race*  
  - For the *same constructor (team)*
- Edge weight = number of races spent as teammates
- Additional attributes stored:
  - `years`: set of years when they were teammates  
  - `teams`: set of constructors they shared

This representation allows exploration of:
- Driver connectivity
- Social clusters across eras
- Shortest teammate paths
- Ego networks

---

##  Data Sources

All data comes from the **Ergast Developer API** (through an official Kaggle archive):

Dataset link:  
https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020

### **Datasets Used**
| File | Description | Fields Used |
|------|-------------|-------------|
| `drivers.csv` | Driver identity and nationality | driverId, forename, surname, nationality |
| `constructors.csv` | Team information | constructorId, name |
| `races.csv` | Race schedule and year info | raceId, year |
| `results.csv` | Core dataset linking drivers to races and teams | raceId, driverId, constructorId |

---

## Data Processing Pipeline

1. Load CSV files with **pandas**
2. Merge `results.csv` with `races.csv` to attach year information
3. Group by `raceId` & `constructorId`  
4. For each group:
   - Generate all teammate pairs using `itertools.combinations`
   - Add/increment edge weight
   - Append year & team data to each edge

This results in a rich, weighted teammate network covering 70+ years of F1 history.

---

##  How to Run the Project

### **1. Install Requirements**
```bash
pip install pandas networkx matplotlib
```

### 1. Find Teammates

Search a driver's complete teammate history.

**How to use:**
- Enter the driver’s name in the input field.
- Click **Search**.
- The results table will display:
  - All teammates the driver has raced with
  - Number of races shared
  - Years of partnership

---

### 2. Shortest Path

Find the shortest teammate connection chain between two drivers.

**How to use:**
- Enter the first driver’s name.
- Enter the second driver’s name.
- Click **Calculate Path**.
- The output box will display:
  - The shortest connection path (e.g., *Hamilton → Alonso → Senna*), or
  - A message if no path exists.

---

### 3. Top Networkers

Display the drivers with the largest number of unique teammates (degree centrality).

**How to use:**
- Click **Show Top 20**.
- A ranked list will appear, showing:
  - Driver name
  - Number of unique teammates

This highlights historically well-connected drivers.

---

### 4. Team Filter

Find all drivers who raced for a specific constructor.

**How to use:**
- Enter a team/constructor name (e.g., *Ferrari*, *McLaren*, *Red Bull*).
- Click **Filter**.
- The results table will display all associated drivers.

---

### 5. Network Viz (Ego Graph Visualization)

Generate a visualization of a driver’s local teammate network.

**How to use:**
- Enter a driver’s name.
- Click **Generate Graph**.
- A pop-up window will display:
  - The selected driver (center node)
  - All teammates (neighbor nodes)
  - Edges representing shared races (weighted)

Close the graph window to return to the GUI.

