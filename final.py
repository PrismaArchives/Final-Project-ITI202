import requests
import json

#Final Project for IT OOP class searches NYT API for mentions of AI to do a frequency analysis
# Code done by Tobiah Powell, docstrings done by Jon Tam
url = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'

#NYT API has some really strict rate limiting of only 5 queries in a minute so we had a list for switching to finish grabbing data if one of our keys has reached max calls
#api_use_int keeps track of the number of queries made in order to change to a new key
api_use_int = 0
API_KEY_LIST = ['9cpGzQ5yf1pGrPZJwA9WYuFd6ZdLzJhA', 'vKDJnQie2GRZ8OlmOonLMhFG7VtrlkEO', 'NYkgk20A5TPWA49C4YsGk7p299pyXfig', '91GviwAkdi4zPAVaL8Uvk3bAyVGsiO9E', 'yCdlAURngorAMNwxrA3X2exb6bhm5Qs8']

#sets starting parameters
params = { 
    "fq": "",
    "q" : "",
    "api-key":API_KEY_LIST[0],
}

#fq and q are the strings used for querying the API
def set_params(fq, q):
    """
    Sets the query parameters used for API requests
    fq: A string for filter query parameter for the API request
    q: A string for query parameter for the API request
    """
    params['fq'] = fq
    params['q'] = q

#the list of terms and years we'll be searching for
search_term_list = ["A.I.","AI","Artificial Intelligence"]
years_list = [2023, 2013]

def api_key_selection():
    """
    Select the appropriate API key for use based on the number of queries made
    """
    global api_use_int
    selected_key = api_use_int // 5
    # this if/else will iterate through keys whenever a key reaches its request limit and loop back around after reaching the end of the list
    if (selected_key >= len(API_KEY_LIST)):
        api_use_int = 0
    else:
        params['api-key'] = API_KEY_LIST[selected_key]
        api_use_int += 1

#uses current parameters in order to get how many articles with that term AKA "hits"
def get_hits():
    """
    Makes an API request to get the number of "hits" for the current parameters
    Returns an integer for the number of hits from the API request
    """
    api_key_selection()
    response = requests.get(url, params)
    content = response.json()
    return content['response']['meta']['hits']

#error wrapper for the get_hits() function. If there would be a KeyError, instead tries the next API_KEY
def get_hits_error_wrapper():
    #depending on the amount of calls, keys will reach maximum requests. If that occurs the try except will catch it and move to the first attempt of the next key
    """
    Catch a key error if it occurs when making an API request for the number of hits
    Returns an integer representing the number of hits obtained from the API request
    """
    try:
        hits = get_hits()
    except KeyError:
        #tells user that too many requests were made
        print("Too many requests made with this API key, moving onto the next in the list")
        # calls the api_use_int and uses some math to move to the next api-key then retries the program
        global api_use_int
        api_use_int = (api_use_int//5)*5+4
        #retries the 
        hits = get_hits_error_wrapper()
    return hits

#searches for a variety of terms within the year specified and creates a nested dictionary of the year being searched, the terms, and the hits per term that is then converted into json
def search_terms_in_year(years, term_list: list):
    """
    Search for terms in the year given and makes a dictionary of the year, terms, and hits
    years: A list of integers representing the years to search for
    term_list: A list of strings representing the terms to search for
    """
    results_dict = {}
    results_dict["years"] = {}
    for year in years:
        results_dict["years"][year] = {}
        for index in term_list:
            set_params(f"pub_year: {year}", index)
            results_dict["years"][year][index] = get_hits_error_wrapper()

    with open("hits_data.json", "w") as file:
        json.dump(results_dict, file, indent = 4)


#will take two years from the hits_data.json file and compare the amount of hits they have.
def compare_years(first_year, second_year, term_list):
    #initialize new dictionary and sets it with a terms key for inputting the various term dictionaries used later
    """
    Compares the number of hits for a list of terms between two years.
    first_year: int
    second_year: int
    term_list: list of str
    Returns a dictionary containing the compared years, terms, and hits for each term in each year.
    """
    terms_dict = {}
    terms_dict["compared years"] = f"{first_year} & {second_year}"
    terms_dict["terms"] = {}
    #opens the file to read it for later data retrieval
    with open('hits_data.json') as openfile:
        hits_json_data = json.load(openfile)
        
    #iterates through each term being searched with
    for term in term_list:
        #initialization for the term used dict
        terms_dict["terms"][term] = {}
        #grabs the amount of hits the term in each year from file
        first_year_hits = hits_json_data['years'][str(first_year)][term]
        second_year_hits = hits_json_data['years'][str(second_year)][term]

        #finds the difference in hits between two years for the term in question
        hit_difference = first_year_hits - second_year_hits

        #finds which year has more hits for the term in question
        if(hit_difference > 0 ):
            terms_dict["terms"][term]["larger_year"] = first_year
        elif (hit_difference < 0):
            terms_dict["terms"][term]["larger_year"] = second_year
        else:
            terms_dict["terms"][term]["larger_year"] = "same"
        
        #since the file will tell which term is larger, uses abs of hit_difference and tells the difference between terms
        terms_dict["terms"][term]["hit_difference"] = abs(hit_difference)

    hits_json_data.update(terms_dict)
    with open('hits_data.json', 'w') as file:
        json.dump(hits_json_data, file, indent=4)
    
    print(hits_json_data['terms'])

#does the searches we need for the years wanted and then compares them
search_terms_in_year(years_list,search_term_list)
compare_years(2013,2023,search_term_list)
