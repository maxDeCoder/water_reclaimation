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

reuse_to_category = pd.read_csv("./dataframes/reuse_to_category.csv")

st.markdown("# Reclaimed Water Demand Allocation & Pricing")
st.sidebar.markdown("# Reclaimed Water Demand Allocation & Pricing")

name_technology = [tech["Name"] for tech in exports]

technology = st.sidebar.selectbox("Select technology", name_technology)
# select the element in exports where the 'Name' is equal to the technology selected
tech = [tech for tech in exports if tech["Name"] == technology][0]

minimum_allocation = st.sidebar.number_input("Minimum Allocation", value=50, min_value=0, max_value=100)/100

capacity = st.sidebar.number_input("STP capacity(MLD)", min_value=1, value=120)
cost_per_kld = st.sidebar.number_input("Cost per KLD", min_value=1., value=8., step=0.1, format="%2.f")
inflation_rate = st.sidebar.number_input("Inflation Rate", value=5., step=0.1, format="%2.f")

multiplier = {
    "Public Utility": 1,
    "Agriculture": 1,
    "Toilet Flushing": 3,
    "Industrial": 5,
    "Commercial": 7
}

num_reuse = int(st.number_input("Number of Reuse", value=1, min_value=1))

reuse_dict = {
    "Category": [],
    "Demand": []
}

# create a tabular form with the input fields where the user can enter the type of reuse purpose and the amount of that purpose
for i in range(num_reuse):
    cols = st.columns(2)
    with cols[0]:
        reuse_dict["Category"].append(reuse_to_category[reuse_to_category["Reuse"] == st.selectbox("Reuse Purpose", reuse_to_category["Reuse"], key=i)]["Category"].to_list()[0])
    with cols[1]:
        reuse_dict["Demand"].append(st.number_input("Demand", value=0, min_value=0, key=i))

df = pd.DataFrame(reuse_dict)
st.markdown(f"### Total demand: {df['Demand'].sum()} MLD")
if df["Demand"].sum() < capacity:
    st.error("Total demand does not meet STP capacity")
else:
    df["final allocation"] = df.apply(lambda x: x["Demand"] if x["Category"] == "Industrial" or x["Category"] == "Commercial" else x["Demand"]*minimum_allocation, axis=1)
    df["revenue"] = df[["final allocation", "Category"]].apply(lambda x: x["final allocation"]*multiplier[x["Category"]], axis=1)

    total_revenue = df["revenue"].sum()/capacity
    x = cost_per_kld/(total_revenue)
    price_for_reuse = {}
    for key, value in multiplier.items():
        price_for_reuse[key] = f"{round((value * x), 3)} per KLD"
    revenue_each_day = df['revenue'].sum() * x * 365/10000

    temp = tech_stack_df[tech_stack_df["Tech Stack"] == tech["Tech Stack"]][["Capital Cost", "O&M Cost"]] * capacity/10
    # temp = tech_stack_df[tech_stack_df["Tech Stack"] == "BIOFOR+WUHERMAN+None"][["Capital Cost", "O&M Cost"]] * capacity/10\
    st.write(temp)
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

    st.write("Price for reuse:")
    st.write(pd.DataFrame({
        "Category": list(price_for_reuse.keys()),
        "Price": list(price_for_reuse.values())
    }))
    temp_df = pd.DataFrame({"O&M Cost": om_list, "Revenue": revenue_list, "Recovery": recovery_list, "Year": range(15), "Capital Cost": cost_list})

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

    figure.update_layout(
        title=f"Recovery and Capital Cost for tech stack: {tech['Tech Stack'].replace('+None', '')}",
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
        st.markdown(f"### Break even year: {break_even+1}")
    else:
        st.warning("Break even cannot be achieved in 15 years, try changing the technology or the cost per KLD")
    