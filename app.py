import streamlit as st
from src.scoring_algorithm import ScoreEngine
import torch
torch.manual_seed(2)

engine = ScoreEngine("BAAI/bge-base-en-v1.5", "itsmeboris/jobbert-base-cased-ner")
uploaded_file = st.file_uploader("Please upload CV Pdf.")

title = st.text_input('Job Description link', 'https://wellfound.com/jobs/2844964-lead-nlp-scientist')
st.write('Job link provided is', title)
st.button("Reset", type="primary")
if st.button('Compute eligibility score'):
    score = round(engine.calculate_score(uploaded_file, title),4)

    st.write(f'{score*100}% Alignment find between job description & resume.')
