# Cytometry Data Analysis for Loblaw Bio


## Instructions to reproduce outputs
The outputs can be reproduced by running `python3 analysis.py`. The required Python packages are pandas, sqlite3, matplotlib, and scipy. 

## Database Schema
The relational database was organized into three tables for projects, subjects, and samples: 

|Projects|     |
| ------ | ----- | 
| prj_id | TEXT | 

| Subjects      | |
| ----------- | ---- |
| subj_id  (PK)    | TEXT |
| prj_id  (FK)    | TEXT |
| age    | INTEGER |
| sex   | CHAR(1) |
| condition    | TEXT |
| treatment   | TEXT |
|response| TEXT |

| Samples      |  |
| ----------- | ---|
| sample (PK)    | TEXT |
| subj_id (FK)    | TEXT |
| time_from_treatment_start    | INTEGER | 
| sample_type   | TEXT |
| b_cell_count    | INTEGER |
| cd8_t_cell_count    | INTEGER |
| cd4_t_cell_count   | INTEGER |
| nk_cell_count    | INTEGER |
| monocyte_count   | INTEGER|


This structure makes the assumption that subject IDs are unique across projects (ie. the same patient will not be a part of several projects). This design was chosen because it logically follows the structure of a clinical trial, in keeping separate information about different projects, patients, and samples, all of which may need to be accessed in separate situations. In addition, this structure reduces redundancy, and promotes scalability in keeping the data easy to understand as the quantity of data grows. 

## Code Structure
Based on the structure of the assignment, all Python code is contained in the file `analysis.py`. The main function follows the logical order from parts 1-4, and several subfunctions with the following functions were created:

- **create_db(fileName)**: builds and populates an SQLite database from the provided CSV file. 

- **create_summary()**: creates the summary table described in part 1

- **get_data_with_condition(conditionDict)**: queries the database using the provided conditions (used in parts 3 and 4)

- **statistical_comparison(summary_table, filtered_data)**: performs the Mann-Whitney U Test and creates box plots for responders and non-responders from the provided data

- **box_plot(responders, nonresponders, cell_type)**: creates box plots to compare response types

- **def subset_analysis(query, name)**: returns queries for project, gender, and responder differences

The code is structured in this way both to provide clean, readable code, and in order to provide general useful functions that can be reused, or modified further for potential future applications. For example, while the statistical analysis for part 3 is contained in the `statistical_comparison` function and currently only runs the Mann-Whitney U Test, it can relatively easily be modified to accommodate different tests. Other functions, like `box_plot` and `get_data_with_condition` are also used multiple times.

## Dashboard 

Link to dashboard: https://cytometry-data-analysis.streamlit.app/

The dashboard is written using Streamlit in Python, due to the relatively simple queries and display requirements. However, for a more advanced UI, I would have written an app in React for better performance and more customization. Currently, the script also saves images to a file before display, which requires analysis to be performed beforehand, and images to be bundled with the dashboard code. For further enhancement and scalability, this could be improved to dynamically generate images to the UI. 