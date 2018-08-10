import urllib
from bs4 import BeautifulSoup
import requests
import webbrowser

text = "'Use Redirection Operators to Save a Command's Results to a File. ... Many Command Prompt commands, and DOS commands for that matter, are executed not just to do something, but to provide you with information.'"
text = urllib.parse.quote_plus(text)

url = 'https://google.com/search?q=' + text

response = requests.get(url)

#with open('output.html', 'wb') as f:
#    f.write(response.content)
#webbrowser.open('output.html')
links = []
soup = BeautifulSoup(response.text, 'html.parser')
link = soup.find('h3', attrs={'class' : 'r'})
links.append(link.a['href'][7:])


print(links)