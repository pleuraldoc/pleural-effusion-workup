
"""
Pleural Effusion Work-up Assistant · v2
Adds pseudo‑exudate gradient checks, urinothorax, hemothorax,
CSF-leak detection, and more.
"""

import streamlit as st
import pandas as pd

st.set_page_config(page_title='Pleural Effusion Work-up Assistant v2', layout='wide')

st.title('Pleural Effusion Work-up Assistant — v2')

# ----------------------- 1. Data Input ------------------------------------
st.header('1. Patient & Laboratory Data')

with st.expander('Patient demographics & vitals'):
    age = st.number_input('Age (years)', 0, 120, 65)
    sex = st.radio('Sex at birth', ['Male', 'Female', 'Other'])
    symptomatic = st.multiselect('Symptoms',
                                 ['Dyspnoea', 'Chest pain', 'Fever', 'Weight loss', 'Cough'])
    immunocompromised = st.checkbox('Immunocompromised / Post-transplant')

with st.expander('Serum values'):
    serum_protein = st.number_input('Serum protein (g/dL)', 0.0, 10.0, 6.5, step=0.1)
    serum_albumin = st.number_input('Serum albumin (g/dL)', 0.0, 6.0, 3.8, step=0.1)
    serum_ldh = st.number_input('Serum LDH (U/L)', 0, 3000, 200, step=10)
    serum_ldh_uln = st.number_input('Upper limit of normal (ULN) for serum LDH', 100, 1000, 250, step=5)
    serum_creatinine = st.number_input('Serum creatinine (mg/dL)', 0.3, 15.0, 1.0, step=0.1)
    serum_hematocrit = st.number_input('Serum hematocrit (%)', 0, 60, 40, step=1)

st.markdown('### Pleural Fluid Values')
col1, col2, col3 = st.columns(3)
with col1:
    pf_protein = st.number_input('PF protein (g/dL)', 0.0, 10.0, 3.2, step=0.1)
    pf_albumin = st.number_input('PF albumin (g/dL)', 0.0, 6.0, 2.4, step=0.1)
    pf_ldh = st.number_input('PF LDH (U/L)', 0, 5000, 300, step=10)
    pf_creatinine = st.number_input('PF creatinine (mg/dL)', 0.0, 15.0, 1.0, step=0.1)
with col2:
    pf_ph = st.number_input('PF pH', 6.5, 8.5, 7.35, step=0.01)
    pf_glucose = st.number_input('PF glucose (mg/dL)', 0, 500, 85, step=5)
    pf_trig = st.number_input('PF triglycerides (mg/dL)', 0, 1000, 50, step=5)
    pf_cholesterol = st.number_input('PF cholesterol (mg/dL)', 0, 300, 45, step=5)
with col3:
    pf_ada = st.number_input('PF ADA (U/L)', 0, 200, 15, step=1)
    beta2 = st.selectbox('PF beta‑2 transferrin (CSF marker)', ['Negative', 'Positive'])
    pf_hematocrit = st.number_input('PF hematocrit (%)', 0, 60, 2, step=1)

# ----------------------- 2. Classification ---------------------------------
st.header('2. Automated Classification')

def light_exudate(pf_protein, serum_protein, pf_ldh, serum_ldh, serum_ldh_uln):
    return ((pf_protein/serum_protein) > 0.5) or                ((pf_ldh/serum_ldh) > 0.6) or                (pf_ldh > 2 * serum_ldh_uln)

exudate_flag = light_exudate(pf_protein, serum_protein, pf_ldh, serum_ldh, serum_ldh_uln)
st.subheader('Light’s Criteria verdict')
st.info('**Exudate**' if exudate_flag else '**Transudate**')

# Pseudo‑exudate check
pseudo_exudate = False
spag = serum_albumin - pf_albumin
spg = serum_protein - pf_protein
if exudate_flag and ((spag > 1.2) or (spg > 3.1)):
    pseudo_exudate = True
    st.warning('Pattern suggests **pseudo‑exudate** (diuretic‑treated transudate).')

# Special aetiology flags
alerts = []
if pf_ph < 7.20: alerts.append('Low pH — consider chest tube for complicated effusion')
if pf_glucose < 60: alerts.append('Low glucose — possible empyema, rheumatoid, malignancy')
if pf_trig > 110: alerts.append('High triglycerides — suspect chylothorax')
if pf_cholesterol > 60: alerts.append('PF cholesterol >60 — supports true exudate')
if pf_ada > 40: alerts.append('ADA >40 — consider tuberculous pleuritis')
if (pf_creatinine / serum_creatinine) > 1.0: alerts.append('PF/serum creatinine >1 — **urinothorax**')
if beta2 == 'Positive': alerts.append('β2‑transferrin positive — CSF leak into pleura')
if (pf_hematocrit / serum_hematocrit) > 0.5: alerts.append('PF hematocrit >50% of blood — **hemothorax**')

if alerts:
    st.warning('**Red / special flags:**\n' + '\n'.join(f'• {a}' for a in alerts))

# ----------------------- 3. RAPID Score ------------------------------------
st.header('3. RAPID Score (Pleural infection)')

with st.expander('Calculate RAPID'):
    renal = st.selectbox('Renal (urea > 7 mmol/L)?', ['No', 'Yes'])
    age_gt70 = st.selectbox('Age > 70?', ['No', 'Yes'])
    purulence = st.selectbox('Purulence?', ['No', 'Yes'])
    infection_source = st.selectbox('Hospital‑acquired?', ['No', 'Yes'])
    dietary = st.selectbox('Serum albumin < 30 g/L?', ['No', 'Yes'])
    rapid_score = sum([renal=='Yes', age_gt70=='Yes', purulence=='Yes',
                       infection_source=='Yes', dietary=='Yes'])
    st.write(f'**RAPID score = {rapid_score}** (0‑1 Low, 2‑3 Medium, 4‑5 High risk)')

# ----------------------- 4. Recommendations --------------------------------
st.header('4. Guideline‑linked Recommendations')
recs = []

if pseudo_exudate:
    recs.append('Pseudo‑exudate pattern — treat underlying heart/renal/hepatic disease; repeat tap after diuretics withheld if uncertain.')
else:
    if not exudate_flag:
        recs.append('Likely transudate — optimise systemic condition (heart failure, cirrhosis, nephrotic).')
    else:
        recs.append('Exudate — pursue aetiology work‑up per BTS 2023.')
for a in alerts:
    if 'urinothorax' in a:
        recs.append('Confirm with CT urogram; address urinary obstruction; place chest drain if large.')
    if 'hemothorax' in a:
        recs.append('Urgent thoracic surgery consult; consider VATS evacuation if clotting.')
    if 'CSF leak' in a:
        recs.append('Brain/spine imaging ± neurosurgery consult for dural defect.')
    if 'chylothorax' in a:
        recs.append('Add PF cholesterol & lipoprotein electrophoresis; start low‑fat MCT diet.')
    if 'tuberculous' in a:
        recs.append('Order PF TB PCR and/or pleural biopsy; start therapy if high pre‑test probability.')

if rapid_score >= 4:
    recs.append('High RAPID — early thoracic surgery review.')

st.markdown('#### Suggested next steps')
for r in recs:
    st.write('•', r)

# ----------------------- 5. Report download --------------------------------
if st.button('Generate CSV Report'):
    report_dict = {
        'Exudate?': exudate_flag,
        'Pseudo‑exudate?': pseudo_exudate,
        'SPAG': spag,
        'SPG': spg,
        'RAPID score': rapid_score,
        'Alerts': '\n'.join(alerts),
        'Recommendations': '\n'.join(recs)
    }
    report = pd.DataFrame(list(report_dict.items()), columns=['Parameter', 'Value'])
    st.download_button('Download report', report.to_csv(index=False),
                       file_name='pleural_workup_report.csv')

st.caption('For educational use only. Verify all recommendations with current guidelines.')
