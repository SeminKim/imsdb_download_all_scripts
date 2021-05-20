import os
from urllib.parse import quote
from progress.bar import ChargingBar

from bs4 import BeautifulSoup
import requests

BASE_URL = 'http://www.imsdb.com'
SCRIPTS_DIR = 'scripts'


def clean_script(text):
    text = text.replace('Back to IMSDb', '')
    text = text.replace('''<b><!--
</b>if (window!= top)
top.location.href=location.href
<b>// -->
</b>
''', '')
    text = text.replace('''          Scanned by http://freemoviescripts.com
          Formatting by http://simplyscripts.home.att.net
''', '')
    return text.replace(r'\r', '')


def get_script(relative_link):
    tail = relative_link.split('/')[-1]
    #print('fetching %s' % tail)
    script_front_url = BASE_URL + quote(relative_link)
    front_page_response = requests.get(script_front_url)
    front_soup = BeautifulSoup(front_page_response.text, "html.parser")

    try:
        script_link = front_soup.find_all('p', align="center")[0].a['href']
    except IndexError:
        #print('%s has no script :(' % tail)
        return ('%s has no script :(' % tail), None

    if script_link.endswith('.html'):
        title = script_link.split('/')[-1].split(' Script')[0]
        script_url = BASE_URL + script_link
        script_soup = BeautifulSoup(requests.get(script_url).text, "html.parser")
        script_text = script_soup.find_all('td', {'class': "scrtext"})[0].get_text()
        script_text = clean_script(script_text)
        return title, script_text
    else:
        # print('%s is a pdf :(' % tail)
        return ('%s is a pdf :(' % tail), None


if __name__ == "__main__":
    response = requests.get('http://www.imsdb.com/all-scripts.html')
    html = response.text

    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all('p')
    errors = []

    bar = ChargingBar('Downloading', max=len(paragraphs))
    for p in paragraphs:
        relative_link = p.a['href']
        title, script = get_script(relative_link)
        bar.next()
        if not script:
            errors.append(title)
            continue

        with open(os.path.join(SCRIPTS_DIR, title.strip('.html') + '.txt'), 'w', -1, 'utf-8') as outfile:
            outfile.write(script)
    bar.finish()
    for err in errors:
        print(err)
