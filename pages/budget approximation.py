import re
from flask import after_this_request
import streamlit as st
import pandas as pd
from itertools import product
import numpy as np

try:
    st.set_page_config(layout="wide")
except:
    pass

st.markdown("# Budget Approximation")
st.sidebar.markdown("# Budget Approximation")

# input for raw waste water
waste_labels = ["BOD(mg/l)", "COD(mg/l)", "TSS(mg/l)", "TN(mg/l)", "FC(MPN/l)"]
dev_labels = ['Land', 'Power', 'Capital Cost', 'O&M Cost']

# this function will load the all the csv files which are preprocessed
def load_tech():
    return (
        pd.read_csv("./dataframes/tech_coeff_pri.csv"), 
        pd.read_csv("./dataframes/tech_coeff_sec.csv"),
        pd.read_csv("./dataframes/tech_coeff_ter.csv"),
        pd.read_csv("./dataframes/reuse.csv"),
        pd.read_csv("./dataframes/tech_stack_coeff.csv")
        )


# this function will return a pandas.Series with boolean values where the  dataframe matches the desired target along with max land and max power requirements
def match_for_config(df, targets, max_land, max_power):
    s = []

    desired_reuse_array = np.array([[v for k, v in targets.items()] for _ in range(len(df))])

    waste_values = after_treatment[waste_labels].to_numpy()
    land_power = after_treatment[["Land", "Power"]].to_numpy()
    land_power_max = np.array([max_land, max_power])

    for i in range(len(df)):
        s.append(np.all(waste_values[i] < desired_reuse_array[i]) and np.all(land_power[i] < land_power_max))

    return pd.Series(s)


# load the dataframes
tech_primary, tech_secondary, tech_tertiary, reuse_df, tech_stack_df = load_tech()

st.write(pd.concat([tech_primary, tech_secondary, tech_tertiary]))
st.write(tech_stack_df)

st.write("\n")

st.markdown("### Raw Waste Water Parameters")

raw_waste_inputs = dict.fromkeys(waste_labels)

for col, label in zip(st.columns(5), waste_labels):
    with col:
        raw_waste_inputs[label] = st.number_input(label, step=1., format="%2.f")

st.write("\n")

# STP parameters
cols = st.columns(3)
with cols[0]:
    stp_capacity = st.number_input("STP capacity(MLD)", 0)
    raw_waste_inputs["cap_for_land"] = stp_capacity
    raw_waste_inputs["cap_for_power"] = stp_capacity
    raw_waste_inputs["cap_for_capital"] = stp_capacity
    raw_waste_inputs["cap_for_om"] = stp_capacity

with cols[1]:
    max_land = st.number_input("Land upper limit(ha)", 0)

with cols[2]:
    max_power = st.number_input("Power upper limit(KWh)", 0)

# weightage
cols = st.columns(4)
weights_coeff = {
    1: 0.48,
    2: 0.24,
    3: 0.16,
    4: 0.12
}

reference = ["None"] + list(weights_coeff.keys())
avaliable_weights = reference
weights = dict.fromkeys(dev_labels, "None")

# 'Land', 'Power', 'Capital Cost', 'O&M Cost'
with cols[0]:
    weights["Land"] = st.selectbox("Land weightage", avaliable_weights)
with cols[1]:
    weights["Power"] = st.selectbox("Power weightage", avaliable_weights)
with cols[2]:
    weights["Capital Cost"] = st.selectbox("Capital cost weightage", avaliable_weights)
with cols[3]:
    weights['O&M Cost'] = st.selectbox("O&M cost weightage", avaliable_weights)

st.write(weights)
st.write(raw_waste_inputs)

st.write("\n")
st.markdown("### Required Reuse purposes")

desired_reuse_selection = st.multiselect("Select your reuse purpose", reuse_df["Reuse"])
desired_reuse = dict.fromkeys(waste_labels)
required_demand = reuse_df[reuse_df["Reuse"].isin(desired_reuse_selection)].reset_index().drop(columns=["index"])

if len(required_demand) != 0:
    _text = []
    for label in waste_labels:
        _value = min(required_demand[label])
        desired_reuse[label] = _value
        _text += [f"Minimum {label}: {_value}"]

    _ = [st.markdown(t) for t in _text]

    st.write("\n")

    raw_waste_array = np.array([[v for k, v in raw_waste_inputs.items()] for _ in range(len(tech_stack_df))])
    after_treatment = tech_stack_df[waste_labels + dev_labels] * raw_waste_array

    temp = after_treatment.copy()
    temp["Tech Stack"] = tech_stack_df["Tech Stack"]

    temp = temp[match_for_config(after_treatment, desired_reuse, max_land, max_power)]
    cols = temp.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    temp = temp[cols]

    temp.sort_values("Capital Cost", inplace=True)
    temp.reset_index(drop=True, inplace=True)

    after_treatment["Tech Stack"] = tech_stack_df["Tech Stack"]

    st.write(after_treatment)
    st.write(temp)
    st.write("\n")

