import json, requests, re
from bs4 import BeautifulSoup
from typing import Dict, List
from io import BytesIO


class JobDescription:

    def __init__(self, url):
        """Intialization for creating and cleaning and processing the data.

        Args:
            url (str): job profile link 
        """        
        self.url =url
        self._processed_data = self._process_data()
    
    def _get_data(self)-> requests.Response:
        """Get job description page from welllfound.

        Returns:
            requests.Response: Job jescription page
        """        
        return requests.get(self.url)

    def _process_data(self)-> Dict:
        """Request page and find the script section of job description page.
        Then catch dictionary string and convert it into a json.

        Returns:
            Dict: Dictionary of diffrent job description sections.
        """        
        page = self._get_data()
        soup = BeautifulSoup(page.content, "html.parser")
        required_data = soup.find_all('script', type='application/ld+json')[0]
        json_expression = re.compile(r"({.*})", re.DOTALL)
        matches = json_expression.search(str(required_data))
        return json.loads(matches.group(1))

    def _get_jobtitle(self)-> str:
        """Select Job title section of processed data of job description. and return 
        Job title of published vacancy.

        Returns:
            str: Job title string.
        """        
        return self._processed_data["title"]

    def _get_industry(self)-> str:
        """Select industry section of processed data of job description. and return 
        industry of published vacancy.

        Returns:
            str: Industry of job string.
        """
        return self._processed_data["industry"]

    def _get_location(self)-> str:
        """Select location section of processed data of job description. and return 
        job location of published vacancy.

        Returns:
            str: Location of job string.
        """
        return self._processed_data["jobLocation"]["address"]["addressLocality"] + ", " +self._processed_data["jobLocation"]["address"]["addressCountry"]

    def _get_education_and_skills(self)-> List[str]:
        """Select job specifications and requirements of job description then
        filter education and skills and return them as string.

        Returns:
            List[str]: list of education, skills.
        """        
        soup = BeautifulSoup(self._processed_data["description"], "html.parser")
        job_description_lines = soup.find_all("li")
        skills= []
        education = []
        for line in job_description_lines:
            if any(degree in line.text for degree in ["Bachelor", "bachelors","MS" ,"M.S." , "Ph D", "PhD", "Ph.D"]):
                education.append(line.text)
            else:
                skills.append(line.text)
        return [" ".join(education), " ".join(skills)]

    def get_data(self)-> Dict[str, str]:
        """
        1-Select Job title section of processed data of job description. and return 
        Job title of published vacancy.

        2-Select location section of processed data of job description. and return 
        job location of published vacancy.

        3-Select industry section of processed data of job description. and return 
        industry of published vacancy.

        4-Select job specifications and requirements of job description then
        filter education and skills and return them as string.

        Returns:
            Dict[str, str]: "Job title", "Location", "Industry/domain", "Education degree", "Technical skills" details of required candidate.
        """        
        return{
            "Job title": self._get_jobtitle(),
            "Location": self._get_location(),
            "Industry/domain": self._get_industry(),
            "Education degree": self._get_education_and_skills()[0],
            "Technical skills": self._get_education_and_skills()[1]
                }