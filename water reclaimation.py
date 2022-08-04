import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

def calc_score(s1, s2, r, c):
    return (s1*s2) + r + c

@st.cache
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
    "Population of vulnarable group",
    "STP density and performance",
    "Infrastucture Resilience"
]

prep_items = [
    "Adoption of water harvesting techniques",
    "Social Acceptance",
    "Policy and Regulations",
    "Water Reuse Infrastructure",
    "Demand for Reclaimed Water",
    "Water pricing Initiative",
    "Expansion for post-distribution network",
    "Power Avaliblity",
    "Land Avaliblity",
    "Fund Avaliblity",
    "Decentralized STPs",
    "Upgradiblity of current STPs Technology",
    "STP connectivity cover"
]

def make_ranged_dict(labels, _range):
    d = {}
    for k, v in zip(labels, _range):
        d[k] = v

    return d

@st.cache
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
        "Significance for Water Sufficiency": S2_index,
        "Implact Reversibility": R_index,
        "Impact Cumulativeness": C_index
    }


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

color_map = {
    -11
}

def color_mapper(scores):
    pass

def bar_chart(df, x_col, y_col, title="", x_axis_title=""):
    fig = px.bar(
        df,
        x=x_col,
        y=y_col,
        color=y_col,
        title=title,
        color_continuous_scale="bluered"
    )

    fig.update_layout(
        autosize=False,
        height=600,
        width=1000
    )

    fig.update_xaxes(
        title=x_axis_title,
    )

    fig.update_yaxes(
        title="Count",
        showgrid=False,
    )

    return fig.update_traces(
        hoverinfo="text",
        insidetextfont=dict(
            color="white"
        ),
    )


st.markdown("# Water Reclaimation")
st.sidebar.markdown("# Water Reclaimation")

st.write("\n")
st.subheader("Vulnablity Assessment")
st.write("\n")

indexes = get_indexes()
comments = load_descriptions()

vuln_scores = []
keys = ["Existing State", "Significance for Water Sufficiency", "Implact Reversibility", "Impact Cumulativeness"]
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
    
vuln_value = sum_score(vuln_scores)
a = comments["vuln"]["Lower"] <= vuln_value
b = comments["vuln"]["Higher"] >= vuln_value
c = a*b
vuln_comment = comments["vuln"][c]["Comment"].to_list()[0]


st.markdown(f"##### Vulnarablity Score: {vuln_value}")
st.markdown(f"##### Comment: {vuln_comment}")

st.write("\n")
st.subheader("Preparedness Assessment")
st.write("\n")

prep_scores = []
keys = ["Implementation/Planning State", "Significance for Water Sufficiency", "Implact Reversibility", "Impact Cumulativeness"]
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

prep_value = sum_score(prep_scores)
a = comments["prep"]["Lower"] <= prep_value
b = comments["prep"]["Higher"] >= prep_value
c = a*b
prep_comment = comments["prep"][c]["Comment"].to_list()[0]


st.markdown(f"##### Preparedness Score: {prep_value}")
st.markdown(f"##### Comment: {prep_comment}")

st.write("\n")
st.markdown(f"### Total Score: {vuln_value+prep_value}")

st.plotly_chart(bar_chart(
    pd.DataFrame({
        "Parameter": vuln_items + prep_items,
        "Score": to_list(vuln_scores) + to_list(prep_scores)
    }), "Parameter", "Score",
    title="Score for each parameter",
    x_axis_title="Parameter"
))
