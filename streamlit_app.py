
"""
Pleural Effusion Work‑up Assistant · v3
— blank defaults & inline PubMed references —
"""
import streamlit as st
import pandas as pd

st.set_page_config(page_title='Pleural Effusion Work-up Assistant v3', layout='wide')
st.title('Pleural Effusion Work‑up Assistant  v3')

def fnum(val):
    """convert string to float or None"""
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

# ---------------- 1. Data entry ----------------
st.header('1. Patient & Laboratory Data')

with st.expander('Patient demographics'):
    age = st.text_input('Age (years)')
    sex = st.radio('Sex at birth', ['Male', 'Female', 'Other'], index=0)
    immunocompromised = st.checkbox('Immunocompromised / Post‑transplant')

with st.expander('Serum values (same draw)', expanded=False):
    s_protein = st.text_input('Serum protein (g/dL)')
    s_albumin = st.text_input('Serum albumin (g/dL)')
    s_ldh = st.text_input('Serum LDH (U/L)')
    s_ldh_uln = st.text_input('ULN for serum LDH (U/L)')
    s_creat = st.text_input('Serum creatinine (mg/dL)')
    s_crit  = st.text_input('Serum haematocrit (%)')

st.subheader('Pleural fluid values')
col1, col2, col3 = st.columns(3)

with col1:
    pf_protein = st.text_input('PF protein (g/dL)')
    pf_albumin = st.text_input('PF albumin (g/dL)')
    pf_ldh = st.text_input('PF LDH (U/L)')
    pf_creat = st.text_input('PF creatinine (mg/dL)')
with col2:
    pf_ph = st.text_input('PF pH')
    pf_glucose = st.text_input('PF glucose (mg/dL)')
    pf_trig = st.text_input('PF triglycerides (mg/dL)')
    pf_chol = st.text_input('PF cholesterol (mg/dL)')
with col3:
    pf_ada = st.text_input('PF ADA (U/L)')
    beta2 = st.selectbox('β‑2 transferrin (CSF marker)', ['Unknown','Negative','Positive'], index=0)
    pf_crit = st.text_input('PF haematocrit (%)')

# helper floats
s_protein_f, s_albumin_f, s_ldh_f, s_ldh_uln_f = map(fnum,[s_protein,s_albumin,s_ldh,s_ldh_uln])
s_creat_f, s_crit_f = map(fnum,[s_creat,s_crit])
pf_protein_f, pf_albumin_f, pf_ldh_f, pf_creat_f = map(fnum,[pf_protein,pf_albumin,pf_ldh,pf_creat])
pf_ph_f, pf_glucose_f, pf_trig_f, pf_chol_f = map(fnum,[pf_ph,pf_glucose,pf_trig,pf_chol])
pf_ada_f, pf_crit_f = map(fnum,[pf_ada,pf_crit])

# ---------------- 2. Classification ----------------
st.header('2. Automated Classification')

lights_ready = all(v is not None for v in [pf_protein_f, s_protein_f, pf_ldh_f, s_ldh_f, s_ldh_uln_f])
if lights_ready:
    exudate = ((pf_protein_f/s_protein_f) > 0.5) or                   ((pf_ldh_f/s_ldh_f) > 0.6) or                   (pf_ldh_f > 2*s_ldh_uln_f)
    st.info('**Exudate**' if exudate else '**Transudate**')
else:
    st.warning('Enter protein & LDH values to apply **Light’s criteria**')
    exudate = None
st.caption('[Light RW 1972 – Ann Intern Med](https://pubmed.ncbi.nlm.nih.gov/4642731/)')

# pseudo‑exudate
pseudo = False
if exudate and s_albumin_f is not None and pf_albumin_f is not None:
    if (s_albumin_f - pf_albumin_f) > 1.2:
        pseudo = True
        st.warning('Albumin gradient > 1.2 g/dL → likely **pseudo‑exudate** (diuretic effect).')
if pseudo:
    st.caption('[Roth et al. 1990 – Chest](https://pubmed.ncbi.nlm.nih.gov/2152757/)')

# special aetiology alerts
alerts = []
if pf_ph_f is not None and pf_ph_f < 7.20: alerts.append('Low pH – complicated parapneumonic.')
if pf_glucose_f is not None and pf_glucose_f < 60: alerts.append('Low glucose – consider empyema / RA / malignancy.')
if pf_trig_f is not None and pf_trig_f > 110: alerts.append('Triglycerides >110 → chylothorax.')
if pf_chol_f is not None and pf_chol_f > 60: alerts.append('Cholesterol >60 supports exudate.')
if pf_ada_f is not None and pf_ada_f > 40: alerts.append('ADA >40 – TB pleuritis likely.')
if pf_creat_f and s_creat_f and pf_creat_f/s_creat_f > 1: alerts.append('PF/serum creatinine >1 → urinothorax.')
if beta2 == 'Positive': alerts.append('β‑2 transferrin positive → CSF leak.')
if pf_crit_f and s_crit_f and pf_crit_f/s_crit_f > 0.5: alerts.append('PF haematocrit >50 % blood → haemothorax.')

if alerts:
    st.warning('\n'.join(alerts))

# ---------------- 3. RAPID ----------------
st.header('3. RAPID Score')
with st.expander('Enter components'):
    renal = st.selectbox('Renal (urea >7 mmol/L)?', ['No','Yes'])
    age70 = st.selectbox('Age >70?', ['No','Yes'])
    purulence = st.selectbox('Gross pus?' , ['No','Yes'])
    hosp = st.selectbox('Hospital‑acquired?', ['No','Yes'])
    lowAlb = st.selectbox('Serum albumin <30 g/L?', ['No','Yes'])
rapid = sum([renal=='Yes', age70=='Yes', purulence=='Yes', hosp=='Yes', lowAlb=='Yes'])
st.write(f'**RAPID = {rapid}** (0‑1 low, 2‑3 mid, 4‑5 high)')
st.caption('[Rahman NM 2014 – Thorax](https://pubmed.ncbi.nlm.nih.gov/24264558/)')

# ---------------- 4. Recommendations ----------------
st.header('4. Guideline‑linked Recommendations')
recs=[]
if exudate is False:
    recs.append('Likely transudate – optimise systemic disease (CHF, cirrhosis, nephrotic).')
if exudate and not pseudo:
    recs.append('Exudate – follow BTS 2023 pleural guideline for further work‑up.')
if pseudo:
    recs.append('Pseudo‑exudate – treat underlying heart/renal disease, repeat tap off diuretics.')
if rapid >=4:
    recs.append('High RAPID – early thoracic‑surgery review advised.')
for a in alerts:
    recs.append(a)
for r in recs:
    st.write('•', r)
st.caption('[BTS Pleural Guideline 2023](https://pubmed.ncbi.nlm.nih.gov/37553157/)')

# ---------------- 5. Export ----------------
if st.button('Download CSV report'):
    report = pd.DataFrame({'Parameter': ['Exudate', 'Pseudo‑exudate', 'RAPID', 'Alerts', 'Recommendations'],
                           'Value': [exudate, pseudo, rapid, '\n'.join(alerts), '\n'.join(recs)]})
    st.download_button('Save report', report.to_csv(index=False), file_name='pleural_report.csv')

st.caption('Educational prototype – verify with clinical judgement.')
