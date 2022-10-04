import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

try:
    st.set_page_config(layout="wide")
except:
    pass

st.markdown("# Appropriate Treatment Technology Selection")
st.sidebar.markdown("# Appropriate Treatment Technology Selection")

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
def match_for_config(df, targets, max_land, max_power, upgrade):
    s = []

    desired_reuse_array = np.array([[v for k, v in targets.items()] for _ in range(len(df))])

    waste_values = df[waste_labels].to_numpy()
    land_power = df[["Land", "Power"]].to_numpy()
    land_power_max = np.array([max_land, max_power])

    a = np.all(waste_values < desired_reuse_array, axis=-1)
    b = np.all(land_power < land_power_max, axis=1)

    if upgrade:
        return a
    else:
        return np.all(np.array([a,b]).T, axis=-1)


def build_scatter(df):
    df["after treatment"] = df[waste_labels].apply(lambda x: ",\n".join([f"{label}:{round(x[label], 2)}" for label in x.index]), axis=1)
    max_size = df["Land"].max()
    df["size"] = df["Land"].apply(lambda x: round(x*50/max_size, 2))
    df["Land"] = df["Land"].apply(lambda x: str(x) + " ha")
    df["Power"] = df["Power"].apply(lambda x: str(x) + " kWh")

    fig = px.scatter(
        df,
        x="Capital Cost weighted",
        y="O&M Cost weighted",
        size="size",
        color="Power weighted",
        hover_data=["after treatment", "Land", "Power"],
        text="Name",
        )

    fig.update_traces(textposition='top center')

    fig.update_xaxes(showgrid=False)

    fig.update_yaxes(showgrid=False)
    return fig


# load the dataframes
tech_primary, tech_secondary, tech_tertiary, reuse_df, tech_stack_df = load_tech()
st.write("\n")

st.markdown("### Raw Waste Water Parameters")

raw_waste_inputs = dict.fromkeys(waste_labels)

for col, label in zip(st.columns(5), waste_labels):
    with col:
        raw_waste_inputs[label] = st.number_input(label, step=1., format="%2.f")

st.write("\n")

# STP parameters
# put a horizontal line here
st.sidebar.write("\n")
st.sidebar.markdown("### STP Parameters")
stp_capacity = st.sidebar.number_input("STP capacity(MLD)", 0)
raw_waste_inputs["cap_for_land"] = stp_capacity
raw_waste_inputs["cap_for_power"] = stp_capacity
raw_waste_inputs["cap_for_capital"] = stp_capacity
raw_waste_inputs["cap_for_om"] = stp_capacity

max_land = st.sidebar.number_input("Land upper limit(ha)", 0)

max_power = st.sidebar.number_input("Power upper limit(KWh)/day", 0)

# costs
st.sidebar.write("\n")
st.sidebar.markdown("### Costs")
land_cost = st.sidebar.number_input("Land Cost (Rupees per Ha)", 0)
eletricity_cost = st.sidebar.number_input("Eletricity cost (Rupees per kWh)", 0)

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

if len(set(weights.values())) != 4:
    _continue = False
    st.error("Please select unique weight values for the parameters")
else:
    _continue = True

st.write("\n")
st.markdown("### Required Reuse purposes")

desired_reuse_selection = st.multiselect("Select your reuse purpose", reuse_df["Reuse"])
desired_reuse = dict.fromkeys(waste_labels)
required_demand = reuse_df[reuse_df["Reuse"].isin(desired_reuse_selection)].reset_index().drop(columns=["index"])

if len(required_demand) != 0 and _continue:
    _text = []
    for label in waste_labels:
        _value = min(required_demand[label])
        desired_reuse[label] = _value
        _text += [f"Minimum {label}: {_value}"]

    _ = [st.markdown(t) for t in _text]

    st.write("\n")
    upgrade = st.checkbox("Is there an already installed STP?")
    if upgrade:
        current_tech = st.selectbox("Select your technology", tech_primary["Tech"])
        LPCO = tech_primary[tech_primary["Tech"] == current_tech][dev_labels].to_numpy()
        # st.write(LPCO)
        LPCO *= stp_capacity
        # st.write(LPCO)
        LPCO = list(LPCO)
    raw_waste_array = np.array([[v for k, v in raw_waste_inputs.items()] for _ in range(len(tech_stack_df))])
    after_treatment = tech_stack_df[waste_labels + dev_labels] * raw_waste_array
    temp = after_treatment.copy()
    temp["Tech Stack"] = tech_stack_df["Tech Stack"]
    temp["Capital Cost"] = (temp["Capital Cost"]).map(lambda x: round(x, 2))
    temp["O&M Cost"] = (temp["O&M Cost"]).map(lambda x: round(x, 2))

    if upgrade:
        temp_no_upgrade = temp.copy()
        temp = temp[temp["Tech Stack"].map(lambda x: x.split("+")[0]==current_tech)].reset_index(drop=True)
        # after_treatment = temp[waste_labels + dev_labels]

        new_values = np.array([temp[waste_labels].iloc[0].to_numpy() for _ in range(len(tech_stack_df))])

        # st.write(new_values)
        after_treatment[waste_labels] = new_values * tech_stack_df[waste_labels]
        # temp_no_upgrade.loc[waste_labels + dev_labels] = after_treatment
        # st.write(after_treatment)
        # st.write(temp_no_upgrade.columns)
        temp_no_upgrade[waste_labels]=after_treatment[waste_labels]
        # st.write(temp_no_upgrade)
        # st.write(temp)

    
    # st.write(desired_reuse)
    temp = temp[match_for_config(temp, desired_reuse, max_land, max_power, upgrade)]
    # st.write("non-supplementary")
    # st.write(temp)

    if upgrade:
        temp_no_upgrade = temp_no_upgrade[match_for_config(after_treatment, desired_reuse, max_land, max_power, False)]
        # st.write("supplementary")
        # st.write(temp_no_upgrade)

    try:
        if len(temp) != 0 or len(temp_no_upgrade) != 0:
            temp["Land weighted"] = (temp["Land"] * land_cost * weights["Land"]).map(int)
            temp["Power weighted"] = (temp["Power"] * eletricity_cost * weights["Power"]).map(int)
            temp["Capital Cost weighted"] = (temp["Capital Cost"] * 1000000 * weights["Capital Cost"]).map(int)
            temp["O&M Cost weighted"] = (temp["O&M Cost"] * 1000000 * weights["O&M Cost"]).map(int)
            temp["Total Cost weighted"] = temp["Land weighted"] + temp["Power weighted"] + temp["Capital Cost weighted"] + temp["O&M Cost weighted"]
            
            show_in_graph = []
            top_n = 5
            names = []

            if upgrade:
                temp_no_upgrade["Land weighted"] = (temp_no_upgrade["Land"] * land_cost * weights["Land"]).map(int)
                temp_no_upgrade["Power weighted"] = (temp_no_upgrade["Power"] * eletricity_cost * weights["Power"]).map(int)
                temp_no_upgrade["Capital Cost weighted"] = (temp_no_upgrade["Capital Cost"] * 1000000 * weights["Capital Cost"]).map(int)
                temp_no_upgrade["O&M Cost weighted"] = (temp_no_upgrade["O&M Cost"] * 1000000 * weights["O&M Cost"]).map(int)
                temp_no_upgrade["Total Cost weighted"] = temp_no_upgrade["Land weighted"] + temp_no_upgrade["Power weighted"] + temp_no_upgrade["Capital Cost weighted"] + temp_no_upgrade["O&M Cost weighted"]

                cols = temp_no_upgrade.columns.to_list()
                cols = cols[-1:]+cols[:-1]
                temp_no_upgrade = temp_no_upgrade[cols]

                temp_no_upgrade.sort_values(by="Total Cost weighted", inplace=True)
                temp_no_upgrade.reset_index(drop=True, inplace=True)
                if len(temp) > 0:

                    LPCO = np.array(LPCO * len(temp))
                    # st.write(temp)
                    new_values = temp[dev_labels].to_numpy() - LPCO
                    temp[dev_labels] = new_values
                    # st.write(new_values)  

            cols = temp.columns.tolist()
            cols = cols[-1:] + cols[:-1]
            temp = temp[cols]

            temp.sort_values("Total Cost weighted", inplace=True)
            temp.reset_index(drop=True, inplace=True)
            # try:
            
            if upgrade:
                st.warning('Since you have opted for an upgrade, the land and power upper limit with not be considered')
                st.subheader("Upgrade options:")
            else:
                st.subheader("Available options:")
            for i in temp.index[:10]:
                with st.expander(f"{i+1} - {temp.loc[i, 'Tech Stack'].replace('+None', '').replace('+', ' + ')}"):
                    primary, secondary, tertiary = temp['Tech Stack'].to_list()[i].split("+")
                    
                    show_in_graph.append(st.checkbox(f"show in plot and save for next step", value=True if i <= top_n-1 else False, key=i))
                    
                    st.dataframe({
                        "Secondary Tech": [primary], 
                        "Emerging Tech": [secondary], 
                        "Tertiary Tech": [tertiary],
                        "Land (ha)": [temp.loc[i, "Land"]],
                        "Power (KWh)": [temp.loc[i, "Power"]],
                        "Capital Cost (cr Rupees)": [temp.loc[i, "Capital Cost"]/10],
                        "O&M Cost/year (cr Rupees)": [temp.loc[i, "O&M Cost"]/10],
                        })

                    names.append(f"{temp.loc[i, 'Tech Stack'].replace('+None', '').replace('+', ' + ')}")

            if upgrade:
                st.subheader("Supplementing with secondary technologies:")
                for i in temp_no_upgrade.index[:10]:
                    with st.expander(f"{i+1} - {temp_no_upgrade.loc[i, 'Tech Stack'].replace('+None', '').replace('+', ' + ')}"):
                        primary, secondary, tertiary = temp_no_upgrade['Tech Stack'].to_list()[i].split("+")
                        show_in_graph.append(st.checkbox(f"show in plot and save for next step", value=True if i <= top_n-1 else False, key=i+50))
                        st.dataframe({
                            "Secondary Tech": [primary], 
                            "Emerging Tech": [secondary], 
                            "Tertiary Tech": [tertiary],
                            "Land (ha)": [temp_no_upgrade.loc[i, "Land"]],
                            "Power (KWh)": [temp_no_upgrade.loc[i, "Power"]],
                            "Capital Cost (cr Rupees)": [temp_no_upgrade.loc[i, "Capital Cost"]/10],
                            "O&M Cost/year (cr Rupees)": [temp_no_upgrade.loc[i, "O&M Cost"]/10],
                            })

                        names.append(f"{temp_no_upgrade.loc[i, 'Tech Stack'].replace('+None', '').replace('+', ' + ')}")
                temp = temp.append(temp_no_upgrade)

            temp["Name"] = names
            temp = temp[show_in_graph]

            st.write("\n")
            st.plotly_chart(build_scatter(temp))

            dump_data = [temp.iloc[i].to_dict() for i in range(len(temp))]

            json.dump(dump_data, open("config.json", "w"))
            # except:
            #     st.write("No matching technology found")

        else:
            st.error("Projected land/power requirements exceed defined upper limits. Increase upper limits for obtaining suggestions.")
    
    except NameError as error:
        pass