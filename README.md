SI 507 Final Project: F1 Driver Teammate Network Analysis

------------------------------------------------------------
Project Overview
------------------------------------------------------------

This project explores the social history of Formula 1 racing by constructing a network graph of drivers. 
By modeling drivers as nodes and their teammate relationships as edges, this tool allows users to analyze 
how drivers are connected across different eras, teams, and seasons.

The program:

- Builds a graph of F1 drivers and their teammate relationships.
- Computes network statistics such as degree centrality.
- Finds the shortest "social paths" between drivers.
- Provides multiple interactive ways for users to explore the network.
- Visualizes the local network around a chosen driver using a graphical interface.

------------------------------------------------------------
Network Structure
------------------------------------------------------------

The project uses a graph data structure (implemented via the networkx library) to model the data:

Nodes:
- Each node represents an F1 driver.
- Each node is identified by the driverId.
- Node attributes include:
  - Full name (forename + surname)
  - Nationality

Edges:
- Each edge represents a teammate relationship.
- Definition: An undirected edge is created between two drivers if they drove for the same constructor 
  (team) in the same race.
- Weight: The edge is weighted by the number of races in which the two drivers were teammates. The weight 
  increases by 1 for every race they share as teammates.
- Edge attributes include:
  - years: a set of years in which the drivers were teammates (e.g., {2007, 2008})
  - teams: a set of team names for which they were teammates (e.g., {"McLaren"})

This graph representation makes it possible to:
- Analyze how "well-connected" drivers are.
- Compute the shortest path between any two drivers.
- Look at the ego-network (local neighborhood) of a specific driver.
- Study the structure of F1 teammate relationships over time.

------------------------------------------------------------
Data Sources
------------------------------------------------------------

This project uses real-world Formula 1 historical data sourced from the Ergast Developer API database.

Data archive:
- The specific CSV files used were obtained via the Kaggle archive:
  "Formula 1 World Championship 1950–2024"
  URL: https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020

Data format:
- All data files are in CSV (Comma Separated Values) format.

------------------------------------------------------------
Data Summary
------------------------------------------------------------

The project integrates four distinct datasets to build the network:

1. drivers.csv
   - Description: Contains driver biographical information.
   - Fields used:
     - driverId
     - forename
     - surname
     - nationality

2. constructors.csv
   - Description: Contains team (constructor) information.
   - Fields used:
     - constructorId
     - name (team name)

3. races.csv
   - Description: Contains schedule information that links race IDs to years.
   - Fields used:
     - raceId
     - year

4. results.csv
   - Description: The core dataset linking drivers, races, and teams.
   - Fields used:
     - raceId
     - driverId
     - constructorId

Together, these datasets allow the program to determine:
- Which drivers raced in which races.
- Which teams they drove for.
- Which drivers were teammates in each race.
- In which years and for which teams teammate relationships occurred.

------------------------------------------------------------
Data Access and Processing Technique
------------------------------------------------------------

Loading:
- The program uses the pandas library to read each CSV file into a DataFrame.

Integration:
- The results.csv data is merged with races.csv (using raceId) to associate every race result with a year.
- Constructors and drivers are linked through their IDs (constructorId and driverId) when constructing
  the graph and when displaying user-facing information.

Graph construction:
- The merged results are grouped by raceId and constructorId.
- For each group (representing a single team in a single race), all drivers in that group are considered
  teammates for that race.
- The program uses itertools.combinations to create edges between every pair of drivers within the group.
- For each pair:
  - The edge weight is incremented by 1 for that race.
  - The race year is added to the edge’s years set.
  - The team name is added to the edge’s teams set.

This approach allows efficient processing of over 25,000 race results while building a rich, weighted
network of F1 teammate relationships.

------------------------------------------------------------
How to Run the Project
------------------------------------------------------------

1. Prerequisites

- Python 3.x installed on your system.
- Required Python libraries:
  - pandas
  - networkx
  - matplotlib
  - (optionally) any GUI toolkit used by gui_app.py, if applicable

You can install the main required libraries with:

    pip install pandas networkx matplotlib

2. Data Configuration

- Ensure that the data folder containing the CSV files (drivers.csv, constructors.csv, races.csv, results.csv, etc.) 
  is located in the same directory as the Python scripts or in the directory referenced by the code.
- If necessary, update the DATA_DIR variable (or equivalent) in the code to point to the correct folder path
  where the CSV files are stored.

3. Execution

- From a terminal or command prompt, navigate to the project directory and run:

    python gui_app.py

- This will launch the graphical user interface (GUI) for the application.

------------------------------------------------------------
User Interaction Guide
------------------------------------------------------------

The application provides a GUI with 5 main tabs. Each tab offers a different way to explore the F1 driver
teammate network.

------------------------------------------------------------
1. Tab: Find Teammates (Search)
------------------------------------------------------------

Description:
- Search for a driver to see every teammate they have ever raced with.
- For each teammate, the program shows the total number of races they shared and the specific years of
  their partnership.

How to use:
1. Go to the "Find Teammates" tab.
2. Enter the driver’s name (for example, "Schumacher") in the input box.
3. Click the "Search" button (or press Enter, if supported).

Output:
- A table or list showing:
  - All teammates of the selected driver.
  - The number of races shared with each teammate.
  - The years in which they were teammates.

------------------------------------------------------------
2. Tab: Shortest Path
------------------------------------------------------------

Description:
- Calculates the "degrees of separation" between two drivers.
- If they were never direct teammates, the program finds the shortest chain of mutual teammates connecting them.

How to use:
1. Go to the "Shortest Path" tab.
2. Enter the name of Driver A.
3. Enter the name of Driver B.
4. Click the "Calculate Path" button.

Output:
- A text display showing the connection path, for example:
  Lewis Hamilton -> Fernando Alonso -> ... -> Ayrton Senna
- If no path is found, the program will display an appropriate message.

------------------------------------------------------------
3. Tab: Top Networkers (Ranking)
------------------------------------------------------------

Description:
- Displays a leaderboard of the top drivers with the highest number of unique teammates in F1 history.
- This effectively measures degree centrality in the driver network.

How to use:
1. Go to the "Top Networkers" tab.
2. Click the button (for example, "Refresh Top 20") to compute and display the ranking.

Output:
- A table showing at least:
  - Rank
  - Driver name
  - Count of unique teammates

------------------------------------------------------------
4. Tab: Team Filter
------------------------------------------------------------

Description:
- Filters the dataset to show a list of drivers associated with a specific constructor (team name).

How to use:
1. Go to the "Team Filter" tab.
2. Enter a team name, such as "Ferrari" or "McLaren", in the input box.
3. Click the "Filter" button.

Output:
- A scrollable list or table of all drivers who have driven for that team in the dataset.

------------------------------------------------------------
5. Tab: Network Viz (Visualization)
------------------------------------------------------------

Description:
- Generates a graphical network visualization (ego graph) of a specific driver and their direct teammates.

How to use:
1. Go to the "Network Viz" tab.
2. Enter the central driver’s name.
3. Click the "Generate Graph" button.

Output:
- A network graph drawn in a window or inside the GUI.
- The central driver is highlighted (for example, in a different color), and their teammates are shown
  as connected nodes around them.
- This visualization helps the user see the local structure of the teammate network.

------------------------------------------------------------
Notes
------------------------------------------------------------

- This project is intended to showcase the use of graph data structures, real-world data integration,
  and interactive exploration in Python.
- It uses multiple datasets and several distinct modes of interaction to meet the SI 507 final project
  requirements.
