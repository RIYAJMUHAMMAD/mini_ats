import json, requests, re
from bs4 import BeautifulSoup
from typing import Dict, List
from io import BytesIO


class JobDescription:

    def __init__(self):
        pass
    
    def _get_data(self, url: str)-> requests.Response:
        """Get job description page from welllfound.

        Args:
            url (str): job profile link 

        Returns:
            requests.Response: Job jescription page
        """        
        return requests.get(url)

    def _process_data(self, url: str)-> Dict:
        """Request page and find the script section of job description page.
        Then catch dictionary string and convert it into a json.

        Args:
            url (str): job profile link

        Returns:
            Dict: Dictionary of diffrent job description sections.
        """        
        page = self._get_data(url)
        soup = BeautifulSoup(page.content, "html.parser")
        required_data = soup.find_all('script', type='application/ld+json')[0]
        json_expression = re.compile(r"({.*})", re.DOTALL)
        matches = json_expression.search(str(required_data))
        return json.loads(matches.group(1))

    def _get_jobtitle(self , job_description_data: Dict)-> str:  
        """Select Job title section of processed data of job description. and return 
        Job title of published vacancy.

        Args:
            job_description_data(Dict): Dictionary of diffrent job description sections.

        Returns:
            str: Job title string.
        """        
        return job_description_data["title"]

    def _get_industry(self, job_description_data: Dict)-> str:
        """Select industry section of processed data of job description. and return 
        industry of published vacancy.

        Args:
            job_description_data(Dict): Dictionary of diffrent job description sections.

        Returns:
            str: Industry of job string.
        """
        return job_description_data["industry"]

    def _get_location(self, job_description_data: Dict)-> str:
        """Select location section of processed data of job description. and return 
        job location of published vacancy.

        Args:
            job_description_data(Dict): Dictionary of diffrent job description sections.

        Returns:
            str: Location of job string.
        """
        return job_description_data["jobLocation"]["address"]["addressLocality"] + ", " +job_description_data["jobLocation"]["address"]["addressCountry"]

    def _get_education_and_skills(self, job_description_data: Dict)-> List[str]:
        """Select job specifications and requirements of job description then
        filter education and skills and return them as string.

        Args:
            job_description_data(Dict): Dictionary of diffrent job description sections.
        
        Returns:
            List[str]: list of education, skills.
        """        
        soup = BeautifulSoup(job_description_data["description"], "html.parser")
        job_description_lines = soup.find_all("li")
        skills= []
        education = []
        for line in job_description_lines:
            if any(degree in line.text for degree in ["Bachelor", "bachelors","MS" ,"M.S." , "Ph D", "PhD", "Ph.D"]):
                education.append(line.text)
            else:
                skills.append(line.text)
        return [" ".join(education), " ".join(skills)]

    def get_data(self, url: Dict)-> Dict[str, str]:
        """
        1-Select Job title section of processed data of job description. and return 
        Job title of published vacancy.

        2-Select location section of processed data of job description. and return 
        job location of published vacancy.

        3-Select industry section of processed data of job description. and return 
        industry of published vacancy.

        4-Select job specifications and requirements of job description then
        filter education and skills and return them as string.

        Args:
            job_description_data(Dict): Dictionary of diffrent job description sections.
        Returns:
            Dict[str, str]: "Job title", "Location", "Industry/domain", "Education degree", "Technical skills" details of required candidate.
        """
        job_description_data = self._process_data(url)
        return{
            "Job title": self._get_jobtitle(job_description_data),
            "Location": self._get_location(job_description_data),
            "Industry/domain": self._get_industry(job_description_data),
            "Education degree": self._get_education_and_skills(job_description_data)[0],
            "Technical skills": self._get_education_and_skills(job_description_data)[1]
                }