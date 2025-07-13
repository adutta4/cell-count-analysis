import pandas as pd
import sqlite3

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
                condition TEXT,
                treatment TEXT,
                FOREIGN KEY (prj_id) REFERENCES projects (prj_id)
            );
            ''')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS samples (
                sample_id TEXT PRIMARY KEY,
                subj_id TEXT,
                prj_id TEXT,
                time_from_treatment INTEGER,
                sample_type TEXT,
                b_cell_count INTEGER,
                cd8_t_cell_count INTEGER,
                cd4_t_cell_count INTEGER,
                nk_cell_count INTEGER,
                monocyte_count INTEGER,
                FOREIGN KEY (subj_id) REFERENCES subject (subj_id),
                FOREIGN KEY (prj_id) REFERENCES projects (prj_id)
            );
            ''')
        df = pd.read_csv(fileName)
        for index, row in df.iterrows():
                cursor.execute(
                    "INSERT OR IGNORE INTO projects (prj_id) VALUES (?)",
                    (row["project"],)
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO subjects (subj_id, prj_id, age, condition, treatment) VALUES (?,?, ?, ?, ?)",
                    (row["subject"],row["project"], row["age"], row["condition"], row["treatment"])
                )
                cursor.execute(
                    "INSERT OR IGNORE INTO samples (sample_id, subj_id, prj_id, time_from_treatment, sample_type, b_cell_count, cd8_t_cell_count, cd4_t_cell_count, nk_cell_count, monocyte_count) VALUES (?,?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (row["sample"], row["subject"], row["project"], row["time_from_treatment_start"], row["sample_type"], row["b_cell"], row["cd8_t_cell"], row["cd4_t_cell"], row["nk_cell"], row["monocyte"])
                )

    except sqlite3.OperationalError as error:
        print("Failed to connect:", error)
    
    conn.commit()
    conn.close()

def create_summary():
    output = []
    database = "database.db"
    pops = ["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"]
    try:
        with sqlite3.connect(database) as conn:
            cur = conn.cursor()
            cur.execute('SELECT sample_id, b_cell_count, cd8_t_cell_count, cd4_t_cell_count, nk_cell_count, monocyte_count FROM samples')
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

def main():
    create_db("cell-count.csv")
    summary_table = create_summary()
    print(summary_table)

if __name__ == "__main__":
    main()