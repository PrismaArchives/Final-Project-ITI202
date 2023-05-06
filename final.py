import requests
import json

#Final Project for IT OOP class searches NYT API for mentions of AI to do a frequency analysis

url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'

API_KEY = "9cpGzQ5yf1pGrPZJwA9WYuFd6ZdLzJhA"

#NYT API has some really strict rate limiting of only 5 queries in a minute so halfway through switch to the second to finish grabbing data"
SECOND_API_KEY = "vKDJnQie2GRZ8OlmOonLMhFG7VtrlkEO"

params = { 
    "fq": "",
    "q" : "",
    "api-key":API_KEY,
}

#fq and q are the strings used for querying the API
def set_params(fq, q):
    params['fq'] = fq
    params['q'] = q

#defines the year we'll be searching

#uses current parameters in order to get how many articles with that term there are "hits"
def get_article_count():
    response = requests.get(url, params)
    content = response.json()
    hits = content['response']['meta']['hits']
    return hits



#the list of terms we'll be searching for
search_term_list = ["A.I.","AI","Artificial Intelligence"]

#searches for a variety of terms within the year specified and creates a nested dictionary of the year being searched, the terms, and the hits per term that is then converted into json
def search_terms_in_year(year, term_list: list):
    results_dict = {}
    results_dict[year] = {}
    for index in term_list:
        set_params(f"pub_year: {year}", index)
        results_dict[year][index] = get_article_count()
    json_formatted = json.dumps(results_dict, indent=4)
    #print(json_formatted)
    with open(f"{year}_hits.json", "w") as file:
        file.write(json_formatted)


#will take created json files and compare the hits for each term 
def compare_years(first_year, second_year, term_list):
    with open(f'{first_year}_hits.json') as openfile:
        first_year_json = json.load(openfile)
    with open(f'{second_year}_hits.json') as openfile:
        second_year_json = json.load(openfile)
    print(first_year_json)
    print(second_year_json)

search_terms_in_year(2023,search_term_list)
params["api-key"] = SECOND_API_KEY
search_terms_in_year(2013,search_term_list)
compare_years(2013,2023,search_term_list)
