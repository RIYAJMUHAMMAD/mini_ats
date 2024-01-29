import pdfplumber, re
from transformers import pipeline
from typing import Dict, List


class Resume:

    def __init__(self, file_path, model_path):
        self.ner_pipe = pipeline("token-classification", model=model_path, aggregation_strategy= "simple")
        self.file_path = file_path
        self._splited_sections = self._split_section() 

    def _resume_text(self)-> str:
        resume = "\n"
        with pdfplumber.open(self.file_path) as pdf:
            totalpages = len(pdf.pages)
            for page_index in range(0 ,totalpages):
                page1= pdf.pages[page_index]
                resume = resume + "\n" +page1.extract_text()
        return resume

    def _split_section(self)-> List[str]:
        spliter_expression = re.compile(r"(\n[A-Z ]{5,20}\n)", re.DOTALL)
        clean_resume = re.sub("(\n{2,4})", "\n", str(self._resume_text()))
        return spliter_expression.split(clean_resume)


    def _process_dict(self, ner_entities: List[Dict]) -> List[Dict]:
        confident_entities = []
        for entity in ner_entities:
            if entity["entity_group"]=="JOB_TITLE" or entity["entity_group"]=="LOC":
                if entity['score']>0.85:
                    confident_entities.append(entity)
        for entity_index in range(len(confident_entities)-1,0,-1):
            if confident_entities[entity_index]["entity_group"]== confident_entities[entity_index-1]["entity_group"]:
                if confident_entities[entity_index-1]["end"]==confident_entities[entity_index]["start"]:
                    confident_entities[entity_index-1]["word"]= confident_entities[entity_index-1]["word"]+confident_entities[entity_index]["word"]
                    confident_entities.pop(entity_index)
                elif confident_entities[entity_index-1]["end"]+1==confident_entities[entity_index]["start"]:
                    confident_entities[entity_index-1]["word"]= confident_entities[entity_index-1]["word"]+" "+confident_entities[entity_index]["word"]
                    confident_entities.pop(entity_index)
                else:
                    pass
        return confident_entities

    def _get_location(self)-> str:
        location = ""
        confident_entities = self._process_dict(self.ner_pipe("\n".join(self._splited_sections[2].splitlines()[:2])))
        for entity in confident_entities:
            if entity["entity_group"] =="LOC" and len(entity["word"])>2 and "#" not in entity["word"]:
                location = entity["word"]
        return location

    def _get_title(self)-> str:
        title = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "EXPERIENCE" in self._splited_sections[resume_setions_index]:
                confident_entities = self._process_dict(self.ner_pipe("\n".join(self._splited_sections[resume_setions_index+1].splitlines()[:3])))
                for entity in confident_entities:
                    if entity["entity_group"] =="JOB_TITLE" and len(entity["word"])>2 and "#" not in entity["word"]:
                        title = entity["word"]
        return title

    def _get_education(self) -> str:
        education = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "EDUCATION" in self._splited_sections[resume_setions_index]:
                education = " ".join(self._splited_sections[resume_setions_index+1].splitlines()[:3])
        return education

    def _get_skills(self)-> str:
        skills = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "SKILLS" in self._splited_sections[resume_setions_index]:
                skills = " ".join(self._splited_sections[resume_setions_index+1].splitlines()[:])
        return skills

    def _get_domain(self)-> str:
        domain = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "EXPERIENCE" in self._splited_sections[resume_setions_index]:
                domain = " ".join(self._splited_sections[resume_setions_index+1].splitlines()[:])
        return domain
    
    def get_data(self)-> Dict[str,str]:
        return{
            "Job title": self._get_title(),
            "Location": self._get_location(),
            "Industry/domain": self._get_domain(),
            "Education degree": self._get_education(),
            "Technical skills": self._get_skills()
                }

    

