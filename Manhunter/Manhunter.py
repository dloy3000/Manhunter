import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions
import time

CHROME_PATH = os.path.dirname(os.path.realpath(__file__)) + "//chromedriver.exe"

USER = "***"
PASS = "***"

def main():
    driver = webdriver.Chrome(CHROME_PATH)  # Get driver
    driver.implicitly_wait(0)
    initial = True

    nameQuery = getQuery()  # Get list of names

    # Begin process of finding and logging LinkedIn info

    for name in nameQuery:
        print("Now scanning for {}...".format(name))
        hrefQuery = linkedInSearch(driver, name.replace('\n', ''), initial)
        initial = False

        profile = scanProfile(driver, hrefQuery[2]) #Take the first search result
    driver.close()

    print("The process is now complete.")

def linkedInSearch(driver, target, initial):
    """
    Accesses LinkedIN, enters in login info, and searches for the target, returning the link to that profile so that
    their information can be procesed.
    :param driver: The driver object.
    :param target: The name to be searched.
    :return: Returns the link in string form.
    """
    if initial:
        print("Logging in...")
        driver.get("https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin")

        # Use keys to Login
        uLogin = driver.find_element_by_id("username")
        uLogin.send_keys(USER)

        pLogin = driver.find_element_by_id("password")
        pLogin.send_keys(PASS)

        bLogin = driver.find_element_by_class_name("login__form_action_container ")
        bLogin.submit()
        print("Login complete.")

    # Catch a re-captcha
    if (checkCaptcha(driver)):
        print("Manhunter has run into a re-captcha.")
        print("Manhunter is not designed to solve these. It requires human input.")
        input("Please solve and press enter when you are ready to proceed.")

    # Find the searchbar and start search
    print("Searching up names...")
    time.sleep(1)  # To prevent crashing upon loading

    search = driver.find_element_by_tag_name("input")
    search.click()
    search.send_keys(target, Keys.ENTER)

    print("Names found.")
    print("Loading top profiles...")

    # Get the links of the targets
    time.sleep(3)  # Gives time for page to load
    hrefElem = driver.find_elements_by_tag_name('a')
    hrefQuery = []

    for i in range(len(hrefElem)):
        item = hrefElem[i].get_attribute('href')
        if "/in/" in item:
            hrefQuery.append(item)

    print("The list of targets is: ")
    print(hrefQuery)
    print("LinkedIn search complete.")

    return hrefQuery

def scanProfile(driver, href):
    """
    Scrapes the information off the target's LinkedIn page.
    :param driver: The driver object.
    :param href: String of the hyperlink to target's LinkedIn.
    """
    driver.get(href)

    #Get basic info
    profElem = driver.find_element_by_id("ember5")
    profile = profElem.find_elements_by_tag_name("li")

    job = profElem.find_elements_by_tag_name("h2")[0].text

    index = 4
    while profile[index].text == "":
        index+=1
    name = profile[index].text

    index = 7
    while profile[index].text == "":
        index+=1
    location = profile[index].text

    #Get experience and education
    expElem = driver.find_element_by_id("oc-background-section")
    expList = expElem.find_elements_by_tag_name('li')
    experience = []

    for position in expList:
        experience.append(position.text)

    print("Now recording {}'s data...".format(name))
    createRecord(name, job, location, experience)

def checkCaptcha(driver):
    """
    Checks if the program has run into a re-captcha.
    :param driver: The driver object.
    :return: Returns True or False.
    """
    if "checkpoint/challenge" in driver.current_url:
        return True
    else:
        return False

def getQuery():
    """
    Gets the list of names from the query file.
    :return: Returns a list of strings.
    """
    queryFile = open("query.txt", "r")
    query = []

    for name in queryFile.readlines():
        query.append(name)

    queryFile.close()
    return query

def createRecord(target, currentPosition, location, experiences):
    """
    Creates a document with the target's information.
    :param target: String name of the target.
    :param currentPosition: String name of target's position.
    :param location: String name of target's city of residence.
    :param experiences: List of Strings containing experiences.
    :param education: List of Strings containing education.
    """
    record = open("{}.txt".format(target.lower().replace(' ', '')), "w+")

    record.write("Name:\n")
    record.write(target + "\n\n")

    record.write("Current Position:\n")
    record.write(currentPosition + "\n\n")

    record.write("Location:\n")
    record.write(location + "\n\n")

    record.write("Experiences/Education:\n")
    for item in experiences:
        record.write(item + "\n\n")

    record.close()

    print("Recording is now complete!")

main()
