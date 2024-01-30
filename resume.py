import pdfplumber, re
from transformers import pipeline
from typing import Dict, List
from io import BytesIO


class Resume:

    def __init__(self, file, model_path:str):
        """Initialize ner pipeline and read and clean resume text and plit in different headings.

        Args:
            file (str): resume file path.
            model_path (str): huggingface model name or local model path
        """        
        self.ner_pipe = pipeline("token-classification", model=model_path, aggregation_strategy= "simple")
        self.file = file
        self._splited_sections = self._split_section() 

    def _resume_text(self)-> str:
        """Read resume and concatenate string of all the pages and return a single string.

        Returns:
            str: Combined text of all pages of resume.
        """
        resume = "\n"
        content = self.file.read()
        with pdfplumber.open(BytesIO(content)) as pdf:
            text = ""
            for page in pdf.pages:
                text = text +"\n" + page.extract_text()
        return text       


    def _split_section(self)-> List[str]:
        """Read resume and concatenate string of all the pages and return a single string.
        Then split the resume on each headings.

        Returns:
            List[str]: List of resume sections and headings.
        """        
        spliter_expression = re.compile(r"(\n[A-Z ]{5,20}\n)", re.DOTALL)
        clean_resume = re.sub("(\n{2,4})", "\n", str(self._resume_text()))
        return spliter_expression.split(clean_resume)


    def _process_dict(self, ner_entities: List[Dict]) -> List[Dict]:
        """Remove less confident entities and add all the combine close adjacent entities.

        Args:
            ner_entities (List[Dict]): NER output.

        Returns:
            List[Dict]: clean ner output.
        """        
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
        """Select 2nd section most of the resume which mostly have contact details and location.
        then pass it to ner pipeline for getting location details.

        Returns:
            str: location of candidate.
        """        
        location = ""
        confident_entities = self._process_dict(self.ner_pipe("\n".join(self._splited_sections[2].splitlines()[:2])))
        for entity in confident_entities:
            if entity["entity_group"] =="LOC" and len(entity["word"])>2 and "#" not in entity["word"]:
                location = entity["word"]
        return location

    def _get_title(self)-> str:
        """Find EXPERIENCE heading of the resume which mostly have current job profile of candidate.
        And take first three lines of that experiece as job title most probably will reside in that section only.
        then pass it to ner pipeline for getting job title.

        Returns:
            str: Job title of candidate.
        """      
        title = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "EXPERIENCE" in self._splited_sections[resume_setions_index]:
                confident_entities = self._process_dict(self.ner_pipe("\n".join(self._splited_sections[resume_setions_index+1].splitlines()[:3])))
                for entity in confident_entities:
                    if entity["entity_group"] =="JOB_TITLE" and len(entity["word"])>2 and "#" not in entity["word"]:
                        title = entity["word"]
        return title

    def _get_education(self) -> str:
        """Find EDUCATION heading of the resume and select text of it which mostly have
           qualification of candidate.

        Returns:
            str: Education of candidate.
        """   
        education = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "EDUCATION" in self._splited_sections[resume_setions_index]:
                education = " ".join(self._splited_sections[resume_setions_index+1].splitlines()[:3])
        return education

    def _get_skills(self)-> str:
        """Find SKILL heading of the resume and select text of it which mostly have current
           skills of candidate.

        Returns:
            str: Skills of candidate.
        """  
        skills = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "SKILLS" in self._splited_sections[resume_setions_index]:
                skills = " ".join(self._splited_sections[resume_setions_index+1].splitlines()[:])
        return skills

    def _get_domain(self)-> str:
        """Find EXPERIENCE heading of the resume which mostly have current job profile of candidate.
        And take whole section that will most probably have all details regarding domain.

        Returns:
            str: Domain of candidate Job.
        """ 
        domain = ""
        for resume_setions_index in range(len(self._splited_sections)):
            if "EXPERIENCE" in self._splited_sections[resume_setions_index]:
                domain = " ".join(self._splited_sections[resume_setions_index+1].splitlines()[:])
        return domain
    
    def get_data(self)-> Dict[str,str]:
        """
        1-Find EXPERIENCE heading of the resume which mostly have current job profile of candidate.
        And take first three lines of that experiece as job title most probably will reside in that section only.
        then pass it to ner pipeline for getting job title.

        2-Select 2nd section most of the resume which mostly have contact details and location.
        then pass it to ner pipeline for getting location details.

        3-Find EXPERIENCE heading of the resume which mostly have current job profile of candidate.
        And take whole section that will most probably have all details regarding domain.

        4-Find EDUCATION heading of the resume and select text of it which mostly have
           qualification of candidate.

        5-Find SKILL heading of the resume and select text of it which mostly have current
           skills of candidate.

        Returns:
            Dict[str,str]: "Job title", "Location", "Industry/domain", "Education degree", "Technical skills" details of candidate.
        """        
        return{
            "Job title": self._get_title(),
            "Location": self._get_location(),
            "Industry/domain": self._get_domain(),
            "Education degree": self._get_education(),
            "Technical skills": self._get_skills()
                }