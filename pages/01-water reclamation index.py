import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    st.set_page_config(layout="wide")
except:
    pass
def calc_score(s1, s2, r, c):
    return (s1*s2) + r + c

# @st.cache
def load_descriptions():
    return {
        "wr": pd.read_csv("./dataframes/wr_score.csv"),
        "vuln": pd.read_csv("./dataframes/vuln_score.csv"),
        "prep": pd.read_csv("./dataframes/prep_score.csv")
    }
vuln_items = [
    "Quality of existing water source",
    "Flowrate of existing water source",
    "Level of groundwater table",
    "Demand and supply gap",
    "Proneness to drought",
    "Population of vulnerable group",
    "STP density and performance",
    "Infrastructure Resilience"
]

prep_items = [
    "Adoption of water harvesting techniques",
    "Social Acceptance",
    "Policy and Regulations",
    "Water Reuse Infrastructure",
    "Demand for Reclaimed Water",
    "Water pricing Initiative",
    "Expansion for post-distribution network",
    "Power Availability",
    "Land Availability",
    "Fund Availability",
    "Decentralized STPs",
    "Upgradability of current STPs Technology",
    "STP connectivity cover"
]

def make_ranged_dict(labels, _range):
    d = {}
    for k, v in zip(labels, _range):
        d[k] = v

    return d

# @st.cache
def get_indexes():
    S1_V_labels = ["Severe", "Poor", "Bad", "Low", "Average", "Good", "Excellent"]
    S1_V_index = make_ranged_dict(S1_V_labels, range(-3, 4))

    S1_P_labels = ["No Planning", "Planned but not implemented", "Implementation Planned", "1-20% Implementation in-progress", "30% Implemented", "60% Implemented", "More than 90% Implemented"]
    S1_P_index = make_ranged_dict(S1_P_labels, range(-3, 4))

    S2_labels = ["High", "Medium", "Low", "Nill"]
    S2_index = make_ranged_dict(S2_labels, range(3, -1, -1))

    R_labels = ["Reversible", "Irreversible"]
    R_index = make_ranged_dict(R_labels, [1, -1])

    C_labels = ["Non-Cumulative", "Cumulative"]
    C_index = make_ranged_dict(C_labels, [1, -1])

    return {
        "Existing State": S1_V_index,
        "Implementation/Planning State": S1_P_index,
        "Significance": S2_index,
        "Impact Reversibility": R_index,
        "Impact Cumulativeness": C_index
    }

interventions = pd.read_csv("./dataframes/interventions.csv")

class score:
    def __init__(self, data: int):
        self.data = data

key_id = 0

def sum_score(scores):
    _sum = 0
    for item in scores:
        _sum += item.data
    
    return _sum

def to_list(scores):
    return [item.data for item in scores]

def bar_chart(df, x_col, y_col, colors=None, title="", x_axis_title=""):
    # fig = go.Figure(data=[go.Bar(x=df[x_col], y=df[y_col])])

    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        title=title,
        text=y_col,
    )
    

    # set marker color
    fig.update_traces(marker_color=colors)

    fig.update_layout(
        autosize=False,
        height=600,
        width=1000
    )

    fig.update_xaxes(
        title=x_axis_title,
    )

    fig.update_yaxes(
        title="Score",
        showgrid=False,
    )

    fig.update_traces(
        hoverinfo="text",
        insidetextfont=dict(
            color="white"
        ),
    )

    return fig


st.markdown("# Water Reclamation Index")
st.sidebar.markdown("# Water Reclamation Index")

st.write("\n")
st.subheader("Vulnerability Assessment")
st.write("\n")

indexes = get_indexes()
comments = load_descriptions()

vuln_scores = []
keys = ["Existing State", "Significance", "Impact Reversibility", "Impact Cumulativeness"]
for label in vuln_items:
    with st.expander(label, True):
        columns = st.columns(4)
        x = score(0)
        with columns[0]:
            key = keys[0]
            x.data = indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1
        
        with columns[1]:
            key = keys[1]
            x.data *= indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1
        
        with columns[2]:
            key = keys[2]
            x.data += indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1
        
        with columns[3]:
            key = keys[3]
            x.data += indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1

        vuln_scores.append(x)

vuln_value = sum_score(vuln_scores) * (0.5/8)
a = comments["vuln"]["Lower"] <= vuln_value
b = comments["vuln"]["Higher"] >= vuln_value
c = a*b
vuln_comment = comments["vuln"][c]["Comment"].to_list()[0]

temp_df_vuln = comments["wr"]
color_vuln = []
for item in vuln_scores:
    a = temp_df_vuln["Lower"] <= item.data
    b = temp_df_vuln["Higher"] >= item.data
    c = a*b
    color_vuln.append(temp_df_vuln[c]["Color"].to_list()[0])

st.markdown(f"##### Vulnerability Score: {vuln_value}")
st.markdown(f"##### Comment: {vuln_comment}")

with st.expander("Vulnerability Interventions", False):
    for item in interventions["V"]:
        # bullet point
        if item != "None":
            st.markdown(f"* {item}")

with st.expander("VI calculation formula", False):
    st.markdown("##### VI = Σ(Existing State * Significance + Impact Reversibility + Impact Cumulativeness)")

st.write("\n")
st.subheader("Preparedness Assessment")
st.write("\n")

prep_scores = []
keys = ["Implementation/Planning State", "Significance", "Impact Reversibility", "Impact Cumulativeness"]
for label in prep_items:
    with st.expander(label, True):
        columns = st.columns(4)
        x = score(0)
        with columns[0]:
            key = keys[0]
            x.data = indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1
        
        with columns[1]:
            key = keys[1]
            x.data *= indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1
        
        with columns[2]:
            key = keys[2]
            x.data += indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1
        
        with columns[3]:
            key = keys[3]
            x.data += indexes[key][st.selectbox(key, list(indexes[key].keys()), key=key_id)]
            key_id+=1

        prep_scores.append(x)

prep_value = sum_score(prep_scores)*(0.5/13)
a = comments["prep"]["Lower"] <= prep_value
b = comments["prep"]["Higher"] >= prep_value
c = a*b
prep_comment = comments["prep"][c]["Comment"].to_list()[0]

color_prep = []
for item in prep_scores:
    a = temp_df_vuln["Lower"] <= item.data
    b = temp_df_vuln["Higher"] >= item.data
    c = a*b
    color_prep.append(temp_df_vuln[c]["Color"].to_list()[0])

colors = color_vuln + color_prep

st.markdown(f"##### Preparedness Score: {prep_value}")
st.markdown(f"##### Comment: {prep_comment}")
with st.expander("Preparedness Interventions", False):
    for item in interventions["P"]:
        # bullet point
        if item != "None":
            st.markdown(f"* {item}")

with st.expander("PI calculation formula", False):
    st.markdown("##### PI = Σ (Implementation/Planning State * Significance + Impact Reversibility + Impact Cumulativeness)")

st.write("\n")
st.markdown(f"### Total Score: {round(vuln_value+prep_value, 2)}")

with st.expander("Total Score calculation formula", False):
    st.markdown("##### Total Score = VI * (0.5/8) + PI * (0.5/13)")

# st.write(colors)
st.markdown("🟥 - Very Poor  🟧 - Poor  🟨 - Bad  🟦 - Satisfactory  🟩 - Good")
st.plotly_chart(bar_chart(
    pd.DataFrame({
        "Parameter": vuln_items + prep_items,
        "Score": to_list(vuln_scores) + to_list(prep_scores),
        "Color": colors
    }), "Parameter", "Score",
    title="Score for each parameter",
    x_axis_title="Parameter",
    colors=colors
))