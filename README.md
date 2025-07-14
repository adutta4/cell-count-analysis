# Cytometry Data Analysis for Loblaw Bio


## Instructions to reproduce outputs
The outputs can be reproduced by running `python3 analysis.py`. The required Python packages are pandas, sqlite3, matplotlib, and scipy. 

## Database Schema
The relational database was organized into three tables for projects, subjects, and samples: 

| Projects      | 
| ----------- | 
| prj_id  (PK)    | 

| Subjects      | 
| ----------- | 
| subj_id  (PK)    | 
| prj_id  (FK)    | 
| age    | 
| sex   | 
| condition    | 
| treatment   | 
|response|

| Samples      | 
| ----------- | 
| sample (PK)    | 
| subj_id (FK)    | 
| time_from_treatment_start    | 
| sample_type   | 
| b_cell_count    | 
| cd8_t_cell_count    | 
| cd4_t_cell_count   | 
| nk_cell_count    | 
| monocyte_count   | 

This structure makes the assumption that subject IDs are unique across projects (ie. the same patient will not be a part of several projects). This design was chosen because it logically follows the structure of a clinical trial, in keeping separate information about different projects, patients, and samples, all of which may need to be accessed in separate situations. In addition, this structure reduces redundancy, and promotes scalability in keeping the data easy to understand as the quantity of data grows. 

## Code Structure
Based on the structure of the assignment, all Python code is contained in the file `analysis.py`. The main function follows the logical order from parts 1-4, and several subfunctions with the following functions were created:

- **create_db(fileName)**: builds and populates an SQLite database from the provided CSV file. 

- **create_summary()**: creates the summary table described in part 1

- **get_data_with_condition(conditionDict)**: queries the database using the provided conditions (used in parts 3 and 4)

- **statistical_comparison(summary_table, filtered_data)**: performs the Mann-Whitney U Test and creates box plots for responders and non-responders from the provided data

- **box_plot(responders, nonresponders, cell_type)**: creates box plots to compare response types

The code is structured in this way both to provide clean, readable code, and in order to provide general useful functions that can be reused, or modified further for potential future applications. For example, while the statistical analysis for part 3 is contained in the `statistical_comparison` function and currently only runs the Mann-Whitney U Test, it can relatively easily be modified to accommodate different tests. Other functions, like `box_plot` and `get_data_with_condition` are also used multiple times.