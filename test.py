import streamlit as st
import pandas as pd
from random import randint

@st.cache
def load_tech():
    return (
        pd.read_csv("./dataframes/tech_coeff_pri.csv"), 
        pd.read_csv("./dataframes/tech_coeff_sec.csv"),
        pd.read_csv("./dataframes/tech_coeff_ter.csv"),
        pd.read_csv("./dataframes/reuse.csv"),
        pd.read_csv("./dataframes/tech_stack_coeff.csv")
        )

@st.cache(allow_output_mutation=True)
def load_extras():
    demand_formula = pd.read_csv("./dataframes/demand_formula.csv")
    demand_formula["Formula"] = demand_formula["Formula"].apply(lambda x: x.replace("*", " * "))

    return (
        demand_formula,
        pd.read_csv("./dataframes/reuse_to_category.csv")
    )
_, _, _, reuse_df, tech_stack_df = load_tech()
demand_formula, reuse_to_category = load_extras()

reuse_dict = {
    "Reuse": [],
    "Category": [],
    "Demand": [],
}

num_reuse = int(st.number_input("Number of Reuse", value=1, min_value=1))

# create a tabular form with the input fields where the user can enter the type of reuse purpose and the amount of that purpose
for i in range(num_reuse):
    cols = st.columns(2)
    with cols[0]:
        selected = st.selectbox("Reuse Purpose", reuse_to_category["Reuse"], key=i+randint(0,1000))
        reuse_dict["Reuse"].append(selected)
        reuse_dict["Category"].append(reuse_to_category[reuse_to_category["Reuse"] == selected]["Category"].to_list()[0])
    with cols[1]:
        reuse_dict["Demand"].append(st.number_input("Demand (MLD)", value=0, min_value=0, key=i+randint(0,1000)))

df = pd.DataFrame(reuse_dict)    

# irrelevant code from here