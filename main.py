import requests
from bs4 import BeautifulSoup as bs
import csv

from regex import regex

headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) '
                         'AppleWebKit/605.1.15 (KHTML, like Gecko) '
                         'Version/13.0.5 Safari/605.1.15'
           }

page_num = 0
base_url = 'https://hh.ru/search/vacancy?area=1&search_period=14&st=searchVacancy&text=python&page={page_num}'
template = ['python', 'Python']


def soup_content(url, hdr):
    session = requests.Session()
    request = session.get(url, headers=hdr)
    soup = bs(request.content, 'lxml')

    return soup


def hh_parse(burl, hdr):
    jobs = []
    urls = [burl]
    soup = soup_content(burl, hdr)

    pagination = soup.find_all('a', attrs={'data-qa': 'pager-page'})
    count = int(pagination[-1].text)
    for i in range(count):
        url = base_url.format(page_num=i)
        if url not in urls:
            urls.append(url)

    for url in urls:
        soup = soup_content(url, hdr)
        divs = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})

        for div in divs:
            location = ""
            salary = ""
            title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
            href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
            try:
                company = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
            except Exception as e:
                print(e)
            try:
                salary = div.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
            except Exception as e:
                print(e)
            try:
                location = div.find('spam', attrs={'class': 'metro-station'})
            except Exception as e:
                print(e)
            text1 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
            text2 = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
            content = text1 + ' ' + text2
            if regex.search(r"\L<words>", title, words=template):
                jobs.append({
                    'title': title,
                    'href': href,
                    'company': company,
                    'location': location,
                    'salary': salary,
                    'content': content
                })
                print("Найдено вакансий:", len(jobs))
    return jobs


def files_writer(jobs):
    with open('parsed_jobs.csv', 'w') as file:
        a_pen = csv.writer(file)
        a_pen.writerow(('Название вакансии', 'Оклад', 'URL', 'Название компании', 'Метро', 'Описание'))
        for job in jobs:
            a_pen.writerow((job['title'], job['salary'], job['href'], job['company'], job['location'], job['content']))


if __name__ == '__main__':
    files_writer(hh_parse(base_url, headers))
