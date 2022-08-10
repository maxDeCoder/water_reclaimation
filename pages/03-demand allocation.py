import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

# DODO: Mininmum requirement selection
# DODO: Change from category to reuse purpose

exports = json.load(open("config.json"))

try:
    st.set_page_config(layout="wide")
except:
    pass

def load_tech():
    return (
        pd.read_csv("./dataframes/tech_coeff_pri.csv"), 
        pd.read_csv("./dataframes/tech_coeff_sec.csv"),
        pd.read_csv("./dataframes/tech_coeff_ter.csv"),
        pd.read_csv("./dataframes/reuse.csv"),
        pd.read_csv("./dataframes/tech_stack_coeff.csv")
        )

_, _, _, reuse_df, tech_stack_df = load_tech()

demand_formula = pd.read_csv("./dataframes/demand_formula.csv")
demand_formula["Formula"] = demand_formula["Formula"].apply(lambda x: x.replace("*", " * "))

reuse_to_category = pd.read_csv("./dataframes/reuse_to_category.csv")

st.markdown("# Reclaimed Water Demand Allocation & Pricing")
st.sidebar.markdown("# Reclaimed Water Demand Allocation & Pricing")

name_technology = [tech["Name"] for tech in exports]

st.sidebar.subheader("Technology Selection")
technology = st.sidebar.selectbox("Select technology", name_technology)
# select the element in exports where the 'Name' is equal to the technology selected
tech = [tech for tech in exports if tech["Name"] == technology][0]

st.sidebar.subheader("Price ratio for categories")
multiplier = {
    "Public Utility": st.sidebar.number_input("Public Utility", min_value=1, value=1),
    "Agriculture": st.sidebar.number_input("Agriculture", min_value=1, value=1),
    "Domestic": st.sidebar.number_input("Domestic", min_value=1, value=3),
    "Industrial": st.sidebar.number_input("Industrial", min_value=1, value=5),
    "Commercial": st.sidebar.number_input("Commercial", min_value=1, value=7),
}

st.sidebar.subheader("STP configuration and pricing:")

minimum_allocation = st.sidebar.number_input("Minimum allocation for prioritized reuse(%)", value=50, min_value=0, max_value=100)/100
capacity = st.sidebar.number_input("STP capacity(MLD)", min_value=1, value=120)
cost_per_kld = st.sidebar.number_input("Cost per KLD", min_value=1., value=8., step=0.1, format="%2.f")
inflation_rate = st.sidebar.number_input("Inflation Rate", value=5., step=0.1, format="%2.f")

num_reuse = int(st.number_input("Number of Reuse", value=1, min_value=1))

reuse_dict = {
    "Reuse": [],
    "Category": [],
    "Demand": [],
}

# create a tabular form with the input fields where the user can enter the type of reuse purpose and the amount of that purpose
for i in range(num_reuse):
    cols = st.columns(2)
    with cols[0]:
        selected = st.selectbox("Reuse Purpose", reuse_to_category["Reuse"], key=i)
        reuse_dict["Reuse"].append(selected)
        reuse_dict["Category"].append(reuse_to_category[reuse_to_category["Reuse"] == selected]["Category"].to_list()[0])
    with cols[1]:
        reuse_dict["Demand"].append(st.number_input("Demand", value=0, min_value=0, key=i))

df = pd.DataFrame(reuse_dict)
st.markdown(f"### Total demand: {df['Demand'].sum()} MLD")

if df["Demand"].sum() > capacity:
    st.warning("The total demand is greater than the STP capacity")
elif df["Demand"].sum() < capacity:
    st.warning("The total demand is less than capacity")

df["Final Allocation"] = df.apply(lambda x: 0 if x["Category"] == "Industrial" or x["Category"] == "Commercial" else x["Demand"]*minimum_allocation, axis=1)

remaining_capacity = capacity - df["Final Allocation"].sum()

# allocate the commercial and industrial categories to the remaining capacity
for i in range(len(df)):
    # check if the category is industrial or commercial
    if df["Category"].iloc[i] == "Industrial" or df["Category"].iloc[i] == "Commercial":
        # check if the demand for the category can be met by the remaining capacity
        if df["Demand"].iloc[i] > remaining_capacity:
            df["Final Allocation"].iloc[i] = remaining_capacity
            remaining_capacity = 0
        else:
            remaining_capacity -= df["Demand"].iloc[i]
            df["Final Allocation"].iloc[i] = df["Demand"].iloc[i]

remaining_capacity = capacity - df["Final Allocation"].sum()

if remaining_capacity > 0:
    # allocate the remaining capacity to non industrial and non commercial categories
    for i in range(len(df)):
        if df["Category"].iloc[i] != "Industrial" and df["Category"].iloc[i] != "Commercial":
            remaining_demand = df["Demand"].iloc[i] - df["Final Allocation"].iloc[i]
            if remaining_demand != 0:
                if remaining_demand > remaining_capacity:
                    df["Final Allocation"].iloc[i] += remaining_capacity
                    remaining_capacity = 0
                else:
                    remaining_capacity -= remaining_demand
                    df["Final Allocation"].iloc[i] += remaining_demand

remaining_capacity = capacity - df["Final Allocation"].sum()

df["Revenue Factor"] = df[["Final Allocation", "Category"]].apply(lambda x: x["Final Allocation"]*multiplier[x["Category"]], axis=1)

total_revenue = df["Revenue Factor"].sum()/capacity
x = cost_per_kld/(total_revenue)
# st.write(x)
price_for_reuse = {}
for key, value in multiplier.items():
    price_for_reuse[key] = f"{round((value * x), 2)} per KLD"
revenue_each_day = df["Revenue Factor"].sum() * x * 365/10000

temp = tech_stack_df[tech_stack_df["Tech Stack"] == tech["Tech Stack"]][["Capital Cost", "O&M Cost"]] * capacity/10
# temp = tech_stack_df[tech_stack_df["Tech Stack"] == "BIOFOR+WUHERMAN+None"][["Capital Cost", "O&M Cost"]] * capacity/10\
st.write(temp.rename(columns={"Capital Cost": "Capital Cost", "O&M Cost": "O&M Cost/year"}))
costs = {
    "Capital Cost": round(temp["Capital Cost"].to_list()[0], 2),
    "O&M Cost": round(temp["O&M Cost"].to_list()[0], 2)
}

# capital_cost = tech["Capital Cost"]
# cost_list = [capital_cost] * 15
# om_cost = tech["O&M Cost"]

capital_cost = costs["Capital Cost"]
cost_list = [capital_cost] * 15
om_cost = costs["O&M Cost"]

om_list, revenue_list, recovery_list = [], [], []
recovery, break_even = 0, 0
for year in range(15):
    om_cost *= (1+(inflation_rate)/100)
    revenue_each_day *= (1+(inflation_rate)/100)
    recovery += revenue_each_day - om_cost
    om_list.append(round(om_cost, 2))
    revenue_list.append(round(revenue_each_day, 2))
    recovery_list.append(round(recovery, 2))
    if recovery >= capital_cost and break_even == 0:
        break_even = year

st.subheader("Allocation for the given reuse purposes:")

st.write(df)

st.subheader("Price for reuse:")

st.write(pd.DataFrame({
    "Category": list(price_for_reuse.keys()),
    "Price": list(price_for_reuse.values()),
}))
temp_df = pd.DataFrame({"O&M Cost": om_list, "Revenue Factor": revenue_list, "Recovery": recovery_list, "Year": range(15), "Capital Cost": cost_list})

# name the x and y axis
figure = go.Figure(
        data=[
            go.Scatter(
                x=temp_df["Year"]+1,
                y=temp_df["Recovery"],
                name="Cumulative Recovery (cr)",
                mode="lines+markers",
                marker=dict(
                    color="green"
                )
            ),
            go.Scatter(
                x=temp_df["Year"]+1,
                y=temp_df["Capital Cost"],
                name=f"Capital Cost = {capital_cost} (cr)",
                mode="lines+markers",
                marker=dict(
                    color="red"
                )
            ),
        ]
    )

st.subheader(f"Break even point analysis for technology combination: {tech['Tech Stack'].replace('+None', '')}")

figure.update_layout(
    xaxis_title="Year",
    yaxis_title="Cost (cr)",
    font=dict(
        size=18,
        color="#7f7f7f"
    )
)

# x axis: no grid, tick spacing of 1
figure.update_xaxes(
    showgrid=False,
    tickfont=dict(
        size=18,
        color="#7f7f7f"
    ),
    ticks="outside",
    tick0=0,
    dtick=1
    )
st.plotly_chart(figure)
if break_even > 0:
    st.markdown(f"##### At average price of {round(cost_per_kld, 2)}, you can expect to achieve break even after {break_even+1} years and be profitable.")
else:
    st.warning("Break even cannot be achieved in 15 years, try changing the technology or the cost per KLD")

with st.expander("How to calculate demand?", False):
    # first reuse name, then the formula, then the legends, then a horizontal line
    for i in demand_formula.index:
        reuse = demand_formula.loc[i, "Reuse"]
        formula = demand_formula.loc[i, "Formula"]
        legend = demand_formula.loc[i, "Legends"]

        st.subheader(f"{reuse}")
        st.write(f"###### {formula}")
        st.write(f"{legend}")
        st.markdown("""---""")