import streamlit as st
from .resume import Resume
from .job_desription import JobDescription
from .matching_engine import MatchingAlgo


class ScoreEngine:
    def __init__(self, matching_algo_model, ner_model):

        self.algorithm = MatchingAlgo(matching_algo_model, 384)
        self.resume = Resume(ner_model)
        self.job_description = JobDescription()

    def score(self, resume_data, job_description_data):
        job_match = min(0.8, self.algorithm.section_score(resume_data["Job title"], job_description_data["Job title"]))
        location_match = min(0.8, self.algorithm.section_score(resume_data["Location"], job_description_data["Location"]))
        industry_match = min(0.8, self.algorithm.section_score(resume_data["Industry/domain"], job_description_data["Industry/domain"]))
        degree_match = min(0.8, self.algorithm.section_score(resume_data["Education degree"], job_description_data["Education degree"]))
        skills_match = min(0.8, self.algorithm.section_score(resume_data["Technical skills"], job_description_data["Technical skills"]))
        return 1.25*float(0.2 *job_match+ 0.2*location_match+ 0.15*industry_match+ 0.25*degree_match + 0.2*skills_match)

    def calculate_score(self, uploaded_file, url):
        resume_data = self.resume.get_data(uploaded_file)
        job_description_data = self.job_description.get_data(url)
        return self.score(resume_data, job_description_data)

