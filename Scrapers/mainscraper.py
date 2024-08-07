from typing import List, Tuple
from bs4 import BeautifulSoup
import requests

def setup_bs(url: str) -> BeautifulSoup:
    '''Set up BeautifulSoup with the url'''
    url_page = requests.get(url)
    url_soup = BeautifulSoup(url_page.text, 'lxml')
    return url_soup

def get_section(soup: BeautifulSoup) -> str:
    '''Gets the span where all the requirements are listed, then returns all the content as a string of all the requirements'''
    # Get the main section element
    main_section = soup.find('span', id='ctl00_contentMain_lblContent')

    # The three html tags the site uses
    html_tags = ["ul", "ol", "p"]

    # Look for each in order of most common to least
    for tag in html_tags:
        if (tag != "p"):
            lines = main_section.find_all(tag, recursive=False)
            if len(lines) > 0:
                return lines[0].get_text()
        else:
            # Special case for "p" because sites with <p> is just a lot of yap
            lines = main_section.find_all(tag, recursive=True)
            tmp = []
            for line in lines:
                tmp.append(line.get_text())
            return tmp
        
    return None

def requirement_dict(lines: str) -> dict:
    '''Takes the string of requirements and turns it into a dictionary with the headers as keys and courses as values'''
    organized_data = {}
    valid_keys = ["One ", "Two ", "Three ", "Four ", "Five ", "Six ", "All ", "Elective", "Any", "following", 
                  "minimum", "academic standing", "courses", "offers"] # All of the potential headers (Don't mind that last one, CPA wants to be special)
    count = 1 # Keep track of the numbers
    key = None
    string = ""
    for letter in lines:
        if letter == '\r' or letter == '\n':
            string = string.strip()
            if string:
                if any(valid_key in string for valid_key in valid_keys):
                    key = f'{count}. {string}'
                    count += 1
                    organized_data[key] = []
                elif (key): # If a key is not found, just append it into the dictionary as a value
                    organized_data[key].append(string)
                else:
                    organized_data[f"{count}."] = string
                    count += 1
            string = ""
        elif(letter == "\'"):
            continue
        else:
            string += letter
    
    if string.strip():
        key = f"{count}. {string}"
        organized_data[key] = []
    return organized_data

def get_majors(year: int) -> list[str]:
    """Returns all the availiable majors for a year"""
    # Set up URL
    url_for_list = "https://academic-calendar-archive.uwaterloo.ca/undergraduate-studies/" + year + "/page/MATH-List-of-Academic-Programs-or-Plans.html"

    # Get all the names
    major_names = setup_bs(url_for_list)
    major_names = major_names.find_all('a')

    # Remove everything before "Amendments"
    i = 0
    for name in major_names:
        if "Amendments" in name.get_text():
            break
        i += 1
    major_names = major_names[i + 1:]
    
    return major_names

def get_minors(year: int) -> list[str]:
    """Returns all availiable Minors/Certifications/Options/Diplomas for a year"""
    # Set up URL
    url_for_list = "https://academic-calendar-archive.uwaterloo.ca/undergraduate-studies/" + year + "/page/Minors-Options-Diplomas-Certificates.html"

    # Set up BeautifulSoup
    minor_names = setup_bs(url_for_list)
    minor_names = minor_names.find_all('a')

    # Get rid of everything before admendments and a few others
    i = 0
    for name in minor_names:
        if "Amendments" in name.get_text():
            break
        i += 1
    minor_names = minor_names[i + 5:]

    # __repr(minor_names)
    return minor_names

def get_math_minors(year: str) -> list[str]:
    url_for_list = "https://academic-calendar-archive.uwaterloo.ca/undergraduate-studies/" + year + "/page/Minors-Options-Diplomas-Certificates.html"

    minor_names = setup_bs(url_for_list)
    minor_names = minor_names.find_all('a')

    # Remove everything other than the math minors
    i = 0
    for name in minor_names:
        if ("Actuarial Science" in name.get_text()):
            break
        i += 1
    
    # Nine math minors
    minor_names = minor_names[i : i + 9]

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
    
    print("N: " + name)
    print("C: " + code)
    print("D: " + desc)
    print("Note: " + note)
    print("Pre: " + prereq)
    print("Co: " + coreq)
    print("Anti: " + antireq)
    print("\n")

    return code, name, desc, note, prereq, coreq, antireq

if __name__ == "__main__":
    soup = setup_bs("https://academic-calendar-archive.uwaterloo.ca/undergraduate-studies/2023-2024/page/MATH-Chart-Prof-Accounting-Finance-Spec-Coop.html")
    lines = get_section(soup)
    # print(lines)
    if lines:
        organized_data = requirement_dict(lines)
    else:
        organized_data = "No courses"
    #print(organized_data)
    # for k, v in organized_data.items():
    #     print(f"{k} {v}")
    #     print(type(k))
    print(str(organized_data))
    