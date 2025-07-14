import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from scipy.stats import mannwhitneyu

# Build SQLite database from CSV file, with samples, projects, and subjects tables
def create_db(fileName):
    try:
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                prj_id TEXT PRIMARY KEY
            );
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                subj_id TEXT PRIMARY KEY,
                prj_id TEXT,
                age INTEGER,
                sex CHAR(1),
                condition TEXT,
                treatment TEXT,
                response TEXT,
                FOREIGN KEY (prj_id) REFERENCES projects (prj_id)
            );
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS samples (
                sample TEXT PRIMARY KEY,
                subj_id TEXT,
                time_from_treatment INTEGER,
                sample_type TEXT,
                b_cell_count INTEGER,
                cd8_t_cell_count INTEGER,
                cd4_t_cell_count INTEGER,
                nk_cell_count INTEGER,
                monocyte_count INTEGER,
                FOREIGN KEY (subj_id) REFERENCES subject (subj_id)
            );
            ''')

        # Add data from CSV file to the database
        df = pd.read_csv(fileName)
        for index, row in df.iterrows():
                cursor.execute(
                    "INSERT OR IGNORE INTO projects (prj_id) VALUES (?)",
                    (row["project"],)
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO subjects (subj_id, prj_id, age, sex, condition, response, treatment) VALUES (?,?, ?, ?, ?, ?, ?)",
                    (row["subject"],row["project"], row["age"], row['sex'], row["condition"], row["response"], row["treatment"])
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO samples (sample, subj_id, time_from_treatment, sample_type, b_cell_count, cd8_t_cell_count, cd4_t_cell_count, nk_cell_count, monocyte_count) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?)",
                    (row["sample"], row["subject"], row["time_from_treatment_start"], row["sample_type"], row["b_cell"], row["cd8_t_cell"], row["cd4_t_cell"], row["nk_cell"], row["monocyte"])
                )

    except sqlite3.OperationalError as error:
        print("Failed to connect:", error)
    
    conn.commit()
    conn.close()

# Build summary table for cell counts. Returns a DataFrame, and outputs to CSV.
def create_summary():
    output = []
    database = "database.db"
    pops = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    try:
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT sample, b_cell_count, cd8_t_cell_count, cd4_t_cell_count, nk_cell_count, monocyte_count FROM samples')
            rows = cur.fetchall()
            for row in rows:
                totalCells = sum(row[1:]) 
                for i in range(0,len(row) - 1):
                    output.append({
                        "sample": row[0],
                        "total_count": totalCells,
                        "population": pops[i],
                        "count": row[i + 1],
                        "percentage": (row[i + 1] / totalCells) * 100 if totalCells > 0 else 0
                    })

        output_df = pd.DataFrame(output)
        output_df.to_csv("summary.csv", index=False)
        return output_df
    except sqlite3.Error as e:
        print(e)

# Retrieve data from the database based on provided conditions. Returns a DataFrame.
def get_data_with_condition(conditionDict):
    try:
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            sql_joined = """SELECT subjects.subj_id, prj_id, age, sex, condition, treatment, response, sample_type, sample, time_from_treatment
                        FROM subjects
                        INNER JOIN samples on subjects.subj_id = samples.subj_id
                        WHERE """
            
            # Add conditions to the SQL query
            condition_sql = []
            for c in conditionDict:
                sql_joined += f"{c} = ? AND "
                condition_sql.append(conditionDict[c])
            sql_joined = sql_joined[:-4]
            cur.execute(sql_joined, condition_sql)
            rows = cur.fetchall()

            df = pd.DataFrame(rows, columns=['subj_id', 'prj_id', 'age', 'sex', 'condition', 'treatment', 'response', 'sample_type', 'sample', 'time_from_treatment'])
            return df

    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
        return None, e
    
# Perform statistical comparison between responders and non-responders for each cell type
def statistical_comparison(summary_table, filtered_data):
    df_merged = summary_table.merge(
    filtered_data[['sample', 'response']],
    on='sample',
    how='inner')

    responders = df_merged[df_merged['response'] == 'yes']
    nonresponders = df_merged[df_merged['response'] == 'no']

    test_results = []

    cell_types = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
    for cell_type in cell_types:
        responders_filtered = responders[responders['population'] == cell_type]
        nonresponders_filtered = nonresponders[nonresponders['population'] == cell_type]
        box_plot(responders_filtered, nonresponders_filtered, cell_type)

        statistic, p_value = mannwhitneyu(responders_filtered['percentage'], nonresponders_filtered['percentage'], alternative='two-sided')
        test_results.append({
            'cell_type': cell_type,
            'statistic': statistic,
            'p_value': p_value
        })
    
    test_results_df = pd.DataFrame(test_results)
    test_results_df.to_csv("statistical_comparison_results.csv", index=False)
    return test_results_df

# Create box plots and save as PNG files
def box_plot(responders, nonresponders, cell_type):
    plt.figure(figsize=(10, 6))
    plt.boxplot([responders['percentage'], nonresponders['percentage']], labels=['Responders', 'Non-responders'])
    plt.title(f'Responder vs. Non-responder Relative Frequency')
    plt.ylabel('Relative Frequency (%)')
    plt.xlabel(cell_type)
    plt.grid(True)
    plt.savefig(cell_type+'_boxplot.png')

# Subset analysis for part 4 
def subset_analysis(query, name):
    query.to_csv(name+".csv", index=False)

    subset_results = {
        'by_project': query.groupby('prj_id').size().to_dict(),
        'by_response': query.groupby('response').size().to_dict(),
        'by_gender': query.groupby('sex').size().to_dict()
    }

    return subset_results

def main():
    # DB setup and summary table creation (Part 1 and 2)
    create_db("cell-count.csv")
    summary_table = create_summary()
    print("Part 2: Summary Table\n", summary_table, "\n")

    # Part 3 - melanoma miraclib patient responses
    melanoma_miraclib_patients = get_data_with_condition({"condition": "melanoma", "treatment": "miraclib", "sample_type": "PBMC"})
    stat_results = statistical_comparison(summary_table, melanoma_miraclib_patients)
    print("Part 3: Statistical Comparison Results\n", stat_results, "\n")

    # Part 4 - melanoma PBMC baseline from patients treated with miraclib
    query = get_data_with_condition({"condition": "melanoma", "treatment": "miraclib", "sample_type": "PBMC", "time_from_treatment": "0"})
    print("Part 4: Data Subset\n", query, "\n")
    results = subset_analysis(query, "melanoma_miraclib_baseline")
    print(results)


if __name__ == "__main__":
    main()