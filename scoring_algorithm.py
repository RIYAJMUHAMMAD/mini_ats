import streamlit as st
from resume import Resume
from desription import JobDescription
from matching_engine import MatchingAlgo

algorithm = MatchingAlgo('BAAI/bge-base-en-v1.5',256)
uploaded_file = st.file_uploader("Please upload CV Pdf.")

def score(resume_data, job_description_data):
    job_match = min(0.8,algorithm.section_score(resume_data["Job title"], job_description_data["Job title"]))
    location_match = min(0.8, algorithm.section_score(resume_data["Location"], job_description_data["Location"]))
    industry_match = min(0.8,algorithm.section_score(resume_data["Industry/domain"], job_description_data["Industry/domain"]))
    degree_match = min(0.8, algorithm.section_score(resume_data["Education degree"], job_description_data["Education degree"]))
    skills_match = min(0.8,algorithm.section_score(resume_data["Technical skills"], job_description_data["Technical skills"]))
    return 1.25*float(0.2 *job_match+ 0.2*location_match+ 0.15*industry_match+ 0.25*degree_match + 0.2*skills_match)

title = st.text_input('Job Description link', 'https://wellfound.com/jobs/2844964-lead-nlp-scientist')
st.write('Job link provided is', title)
st.button("Reset", type="primary")
if st.button('Compute eligibility score'):

    resume_data = Resume(uploaded_file,'itsmeboris/jobbert-base-cased-ner').get_data()
    job_description_data = JobDescription(title).get_data()
    st.write(f'{round(score(resume_data, job_description_data),4)*100}% Alignment find between job description & resume.')
