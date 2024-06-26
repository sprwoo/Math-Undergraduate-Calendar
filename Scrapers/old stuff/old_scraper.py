from bs4 import BeautifulSoup
import requests
import re
from typing import Dict, Tuple

def is_valid_course(course_code: str) -> bool:
    """Checks if a given string is a valid course code"""
    pattern = r'^[A-Za-z]{2,}\s\d{3}[A-Za-z]?$'
    return re.match(pattern, course_code, re.IGNORECASE) is not None

def get_bs(url: str, find: str) -> list[str]:
    """Sets up BeautifulSoup and returns the content we are looking for"""
    url_page = requests.get(url)
    url_soup = BeautifulSoup(url_page.text, 'lxml')
    url_courses = url_soup.find_all(find)
    return url_courses

def __repr(names: list) -> None:
    """Prints out the list of majors/minors/courses"""
    for name in names:
        print(name.get_text())
        print(name.get('href'))

def print_if_exists(check: str) -> None:
    """Prints a string if it is not empty"""
    if check:
        print(check)

def get_majors(year: int) -> list[str]:
    """Returns all the availiable majors for a year"""
    # Set up URL
    url_for_list = "https://academic-calendar-archive.uwaterloo.ca/undergraduate-studies/" + year + "/page/MATH-List-of-Academic-Programs-or-Plans.html"
    #print(url_for_list)

    # Get all the names
    major_names = get_bs(url_for_list, 'a')

    # Remove everything before "Amendments"
    i = 0
    for name in major_names:
        if "Amendments" in name.get_text():
            break
        i += 1
    major_names = major_names[i + 1:]
    # __repr(major_names)

    return major_names

def get_courses(degree: str) -> Dict[str,str]:
    """Returns the course requirements for a specific degree"""
    # Set up URL
    link_header = "https://academic-calendar-archive.uwaterloo.ca"
    choice_url = link_header + degree.get('href')

    # Set up BeautifulSoup
    choice_courses = get_bs(choice_url, 'a')

    # Filter out invalid courses
    tmp = []
    for course in choice_courses:
        if is_valid_course(course.get_text()):
            tmp.append(course.get_text())
    choice_courses = tmp

    # __repr(choice_courses)
    return choice_courses

def get_minors(year: int) -> list[str]:
    """Returns all availiable Minors/Certifications/Options/Diplomas for a year"""
    # Set up URL
    minor_url = "https://academic-calendar-archive.uwaterloo.ca/undergraduate-studies/" + year + "/page/Minors-Options-Diplomas-Certificates.html"

    # Set up BeautifulSoup
    minor_names = get_bs(minor_url, 'a')

    # Get rid of everything before admendments and a few others
    i = 0
    for name in minor_names:
        if "Amendments" in name.get_text():
            break
        i += 1
    minor_names = minor_names[i + 5:]

    # __repr(minor_names)
    return minor_names

def get_info(req: str) -> Tuple[str, str, str, str, str, str, str]:
    """Returns a list of all the info of a type of course"""
    code = req.find('a').get('name')

    name = req.find_all(class_='divTableCell colspan-2')
    desc = name[1].get_text()
    desc = desc.replace("\n", "").replace("\r", "").replace("\"", "").replace("\'", "")

    name = name[0].get_text()
    
    info = req.find_all('em')
    
    note = info[0].get_text().strip().replace("\n", "").replace("\r", "").replace("\"", "").replace("\'", "") # Python is great

    prereq = ''
    coreq = ''
    antireq = ''
    for tag in info:
        text = tag.get_text().strip()
        tmp = ''
        for letter in text:
            if letter == "\n" or letter == "\r" or letter == "\'" or letter == "\"":
                continue;
            else:
                tmp += letter
        text = tmp.strip()
        
        if ("Prereq" in tag.get_text()):
            prereq = text
        if ("Coreq" in tag.get_text()):
            coreq = text
        if ("Antireq" in tag.get_text()):
            antireq = text
    
    """
    print("N: " + name)
    print("C: " + code)
    print("D: " + desc)
    print_if_exists("Note: " + note)
    print_if_exists("Pre: " + prereq)
    print_if_exists("Co: " + coreq)
    print_if_exists("Anti: " + antireq)
    print("\n")
    """

    return code, name, desc, note, prereq, coreq, antireq