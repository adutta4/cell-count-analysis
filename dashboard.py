import streamlit as st
import pandas as pd
import analysis

summary_table = analysis.create_summary()

def Data_Overview():
    st.title("Initial Analysis - Frequency Summary")
    st.write("The table below provides a summary for the cell counts, and the relative frequencies of each cell type in the dataset. " \
    "")
    st.write(summary_table)

def Statistical_Analysis():
    stats = analysis.statistical_comparison(summary_table, analysis.get_data_with_condition({"condition": "melanoma", "treatment": "miraclib", "sample_type": "PBMC"}))
    st.title("Statistical Analysis - Responders vs Non-responders")
    st.write("Please select a cell type to view the box plot and statistical test results for comparison in patients with melanoma receiving miraclib." \
    " The Mann-Whitney U test is used to compare the relative frequencies of each cell type between responders and non-responders." \
    " This is because the data is not normally distributed, and the test is suitable for comparing two independent samples." )

    # Dropdown - see results by cell type
    option = st.selectbox(
    "Choose a cell type for statistical analysis:",
    ("B Cell", "CD4 T Cell", "CD8 T Cell", "NK Cell", "Monocyte"),
    index = None,
    placeholder="Select a cell type..."
    )

    cell_info = {
    "B Cell": ("b_cell", "b_cell_boxplot.png"),
    "CD4 T Cell": ("cd4_t_cell", "cd4_t_cell_boxplot.png"),
    "CD8 T Cell": ("cd8_t_cell", "cd8_t_cell_boxplot.png"),
    "NK Cell": ("nk_cell", "nk_cell_boxplot.png"),
    "Monocyte": ("monocyte", "monocyte_boxplot.png")
    }
    
    # Selected option shows boxplot, Mann-Whitney U test results, and p-value interpretation
    if option in cell_info:
        cell_type, image_file = cell_info[option]
        
        st.image(image_file, caption=f"{option} Box Plot")
        st.write("Mann-Whitney U test results:\n")
        
        cell_stats = stats[stats["cell_type"] == cell_type]
        st.write(cell_stats)
        
        # P-value interpretation (assuming a significance threshold of 0.05)
        p_value = cell_stats["p_value"].values[0]
        if p_value < 0.05:
            st.markdown(
                f"Since the p-value is **{p_value:.4f}**, which is less than 0.05, we reject the null hypothesis. "
                f"This suggests a **statistically significant difference** in the relative frequencies of {option}s "
                f"between responders and non-responders."
            )
        else:
            st.markdown(
                f"Since the p-value is **{p_value:.4f}**, which is greater than 0.05, we fail to reject the null hypothesis. "
                f"This indicates that there is **no statistically significant difference** in the relative frequencies of {option}s "
                f"between responders and non-responders."
            )

def Data_Subset_Analysis():
    subset = analysis.get_data_with_condition({"condition": "melanoma", "treatment": "miraclib", "sample_type": "PBMC", "time_from_treatment": "0"})
    st.title("Data Subset Analysis")
    st.write("#### Part 1 - Data Subset for Baseline Melanoma Patients Treated with Miraclib at Baseline")
    st.write(subset)
    st.write("#### Part 2 - Further Subset Analysis")
    st.write(analysis.subset_analysis(subset, "melanoma_miraclib_baseline"))

pg = st.navigation([Data_Overview, Statistical_Analysis, Data_Subset_Analysis], position="top")

pg.run()

