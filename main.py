# import requests
# from bs4 import BeautifulSoup

# def get_navbar_links(soup):
#     # Assuming the navbar links are within <nav> tags or have a specific class/id
#     navbar_links = []
#     navbars = soup.find_all('h9Kv0')
#     for navbar in navbars:
#         links = navbar.find_all('a', href=True)
#         for link in links:
#             navbar_links.append(link['href'])
#     return navbar_links

# def get_information_links(soup, keywords):
#     # Filtering links that contain specific information based on keywords
#     information_links = []
#     links = soup.find_all('a', href=True)
#     for link in links:
#         if any(keyword in link.get_text().lower() for keyword in keywords):
#             information_links.append(link['href'])
#     return information_links

# def find_useful_links(url, keywords):
#     try:
#         # Fetch the website content
#         response = requests.get(url)
#         response.raise_for_status()
#         content = response.content
        
#         # Parse the HTML content
#         soup = BeautifulSoup(content, 'html.parser')
        
#         # Get navbar links
#         navbar_links = get_navbar_links(soup)
        
#         # Get information links
#         information_links = get_information_links(soup, keywords)
        
#         return navbar_links, information_links
#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching the URL: {e}")
#         return [], []

# # Example usage
# url = 'https://unsplash.com/'
# keywords = ['tutorial', 'guide', 'documentation']
# navbar_links, information_links = find_useful_links(url, keywords)

# print("Navbar Links:")
# for link in navbar_links:
#     print(link)

# print("\nInformation Links:")
# for link in information_links:
#     print(link)


import requests
from bs4 import BeautifulSoup

def get_navbar_links(soup):
    # Assuming the navbar links are within <nav> tags or have a specific class/id
    navbar_links = []
    navbars = soup.find_all('nav')  # Adjust the tag/class as needed
    print(f"Found {len(navbars)} navbar elements.")
    for navbar in navbars:
        links = navbar.find_all('a', href=True)
        for link in links:
            navbar_links.append(link['href'])
    return navbar_links

def get_information_links(soup, keywords):
    # Filtering links that contain specific information based on keywords
    information_links = []
    links = soup.find_all('a', href=True)
    print(f"Found {len(links)} total links.")
    for link in links:
        if any(keyword in link.get_text().lower() for keyword in keywords):
            information_links.append(link['href'])
    return information_links

def find_useful_links(url, keywords):
    try:
        # Fetch the website content
        response = requests.get(url)
        response.raise_for_status()
        content = response.content
        
        # Parse the HTML content
        soup = BeautifulSoup(content, 'html.parser')
        
        # Get navbar links
        navbar_links = get_navbar_links(soup)
        
        # Get information links
        information_links = get_information_links(soup, keywords)
        
        return navbar_links, information_links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return [], []

def save_links_to_file(navbar_links, information_links, filename):
    with open(filename, 'w') as file:
        file.write("Navbar Links:\n")
        for link in navbar_links:
            file.write(f"{link}\n")
        
        file.write("\nInformation Links:\n")
        for link in information_links:
            file.write(f"{link}\n")

# Example usage
url = 'https://www.quicsolv.com/'
keywords = ['tutorial', 'guide', 'documentation']
navbar_links, information_links = find_useful_links(url, keywords)

# Debug prints
print(f"Navbar Links: {navbar_links}")
print(f"Information Links: {information_links}")

save_links_to_file(navbar_links, information_links, 'output.txt')

print("Links have been saved to output.txt")
