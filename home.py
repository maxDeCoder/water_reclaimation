import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

content = pd.read_csv("./dataframes/content_tech.csv")

st.subheader("Welcome to Decision Support System for Appropriate Wastewater Treatment Technology Selection")
st.write("Water scarcity has been regarded as a global risk with potentially devastating impacts. Climate change, exploding population, and industrialization are the main drivers behind such an imbalance in safe water availability. India is predicted to get most severely impacted by water scarcity owing to its high urban population. To tackle this imbalance between water demand and its safe availability, wastewater reclamation can be seen as a potential source of water, which if treated, can boost water availability as well as prevent environmental degradation. When treated wastewater is reutilized after treatment, it is referred to as wastewater reclamation. Municipal wastewater is considered a limitless source of water due to its high biodegradability and low toxicity profile. Globally, 80% of the wastewater generated is disposed of in the environment, causing hazardous impacts on the receiving water bodies. The burden of environmental degradation and water scarcity can be significantly reduced by utilizing treated wastewater as a water source. Several industrial and domestic activities do not require reliance on high-quality potable water but can utilize reclaimed water to obscure the issue of water scarcity. By observing the trend of water demand and the definition of relevant quality criteria, raw wastewater can be treated to produce a secondary water source.")
st.write("\n")
st.write("A technology that satisfies the demand of users with optimum resource utilization is appropriate. The concept of appropriate technology was given by economist Schumacher in his book “Small is Beautiful”. Appropriate technology has the potential to serve the desired purpose with no social, economic, or environmental ramifications. It is people-centric, local condition-specific, cost-efficient, and sustainable in nature.")

st.subheader("Secondary Treatment Technologies")
st.write("These sewage treatment technologies depend on biological processes for the decomposition of suspended and dissolved organic matter present in wastewater. They employ cultured micro-organisms to decompose organic matter and aid reproduction. Therefore, more populations of microbes become available for carrying out the biological decomposition of organic matter and obtaining treated wastewater. The oxygen required by microorganisms to carry out this process is referred to as Biochemical Oxygen Demand (BOD). These treatment processes can take place in the presence or absence of oxygen, known as, aerobic decomposition and anaerobic decomposition respectively. The associated microorganisms are also categorized as aerobic and anaerobic bacteria respectively. The aerobic process is suitable for the treatment of low strength wastewater (bCOD<1000mg/l) while the anaerobic process is considered suitable for high strength wastewater (bCOD>4000 mg/l). Various treatment technologies considered in this tool, are discussed in this section.")
data = content[content["Type"] == "Secondary Treatment Technologies"]

for i in data.index:
    name = data.loc[i, "Name"]
    desc = data.loc[i, "Content"]
    with st.expander(name):
        st.write(desc)

st.subheader("Emerging Technologies")
st.write("The main objective behind sewage treatment plants’ installation is to improve the effluent quality for safe disposal or reuse. Production of reclaimed water satisfying the desired quality criteria is the recent trend in the wastewater treatment industry and hence to deal with the problem of nutrient concentration in wastewater, several emerging treatment technologies are employed, which are discussed in the following paragraphs.")
data = content[content["Type"] == "Emerging Technologies"]

for i in data.index:
    name = data.loc[i, "Name"]
    desc = data.loc[i, "Content"]
    with st.expander(name):
        st.write(desc)

st.subheader("Tertiary Treatment Technologies")
st.write("Tertiary treatment technologies are utilised as polishing technologies, to further reduce the concentration of minute or very low concentration quality parameters.")
data = content[content["Type"] == "Tertiary Treatment Technologies"]

for i in data.index:
    name = data.loc[i, "Name"]
    desc = data.loc[i, "Content"]
    with st.expander(name):
        st.write(desc)