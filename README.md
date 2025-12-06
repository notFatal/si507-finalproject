# SI 507 Final Project: F1 Driver Teammate Network Analysis

## Project Overview
This project explores the social history of Formula 1 racing by constructing a network graph of drivers. By modeling drivers as **nodes** and their teammate relationships as **edges**, this tool allows users to analyze how drivers are connected across different eras, teams, and seasons. The program calculates network statistics (like centrality), finds the shortest "social paths" between drivers, and visualizes individual driver networks.

---

## Network Structure
The project uses a graph data structure (implemented via the `networkx` library) to model the data:

* **Nodes**: Represent **F1 Drivers**.
    * Each node is identified by the `driverId`.
    * Attributes stored: Driver's full name and nationality.

* **Edges**: Represent a **Teammate Relationship**.
    * **Definition**: An edge is created between two nodes if they drove for the **same constructor** (team) in the **same race**.
    * **Weights**: The edge is **weighted**. The weight increases by 1 for every single race the pair spends as teammates.
    * **Attributes**: Each edge stores a set of `years` (e.g., {2007, 2008}) and `teams` (e.g., {"McLaren"}) to provide historical context for the connection.

---

## Data Sources
This project uses real-world Formula 1 historical data sourced from the **Ergast Developer API** database.

* **Data Archive**: The specific CSV files used were obtained via the Kaggle archive: [Formula 1 World Championship 1950-2024](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020?select=drivers.csv).
* **Data Format**: CSV (Comma Separated Values).

### Data Summary
The project integrates four distinct datasets to build the network:

1.  **`drivers.csv`**: Contains driver biographical info.
    * *Fields used*: `driverId`, `forename`, `surname`, `nationality`.
2.  **`constructors.csv`**: Contains team information.
    * *Fields used*: `constructorId`, `name` (team name).
3.  **`races.csv`**: Contains schedule information to link race IDs to years.
    * *Fields used*: `raceId`, `year`.
4.  **`results.csv`**: The core dataset linking drivers, races, and teams.
    * *Fields used*: `raceId`, `driverId`, `constructorId`.

### Data Access & Processing Technique
* **Loading**: The program uses the `pandas` library to read the CSV files into DataFrames.
* **Integration**: The `results.csv` data is merged with `races.csv` (using Pandas mapping) to associate every race result with a year.
* **Graph Construction**: The data is grouped by `raceId` and `constructorId`. The program then uses `itertools.combinations` to generate edges between all drivers in the same group, ensuring efficient processing of over 25,000 race results.

---

## How to Run the Project



### 1. Prerequisites
Ensure you have Python 3 installed. You will need to install the following libraries:

```bash
pip install pandas networkx matplotlib
```

### 2. Data Configuration
Before running the program, please verify the data path in `main.py`.
* Open `main.py` in your code editor.
* Check line 9: `DATA_DIR = r"..."`
* Ensure this path points to the folder containing your CSV files (`drivers.csv`, `constructors.csv`, etc.).

### 3. Execution
Run the script from your terminal:
```bash
python main.py
```
## User Interaction Guide

The program provides a main menu with 6 interactive options. Below is a guide on how to use each feature:

### 1. [Node Info] Find teammates and years for a specific driver
* **Description**: Search for a driver to see every teammate they have ever raced with. The results include the total number of races shared and the specific years of their partnership.
* **How to use**: Enter option `1`, then type the driver's name.
* **Example**:
    * Input: `Schumacher`
    * Output: Lists Michael Schumacher's teammates (e.g., Rubens Barrichello, Felipe Massa) with race counts and years.

### 2. [Path] Find shortest relationship chain between two drivers
* **Description**: Calculates the "degrees of separation" between two drivers. If they were never teammates, it finds the shortest chain of mutual teammates connecting them.
* **How to use**: Enter option `2`. You will be prompted to enter the **First Driver** and then the **Second Driver**.
* **Example**:
    * Input: `Hamilton` and `Senna`
    * Output: Shows the connection path: `Lewis Hamilton <--> Fernando Alonso <--> ... <--> Ayrton Senna`.

### 3. [Ranking] View drivers with the most connections
* **Description**: Displays a leaderboard of the Top 10 drivers who have had the highest number of unique teammates in F1 history (Degree Centrality).
* **How to use**: Enter option `3`.

### 4. [Filtering] View drivers who raced for a specific team
* **Description**: Filters the dataset to show a list of drivers associated with a specific constructor (team name).
* **How to use**: Enter option `4`, then type a team name (e.g., `Ferrari` or `McLaren`).
* **Output**: Lists drivers who drove for that team based on the dataset.

### 5. [Viz] Visualize driver's social circle
* **Description**: Generates a graphical network visualization of a specific driver and their direct teammates (Ego Graph).
* **How to use**: Enter option `5`, then type the driver's name.
* **Note**: A window will pop up showing the network graph. **You must close the window to return to the main menu.**

### 6. Exit
* **Description**: Closes the application.
* **How to use**: Enter option `6`.

