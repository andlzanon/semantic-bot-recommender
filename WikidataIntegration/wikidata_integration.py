import pandas as pd
import time
from SPARQLWrapper import SPARQLWrapper, JSON


def get_movie_data_from_wikidata(slice_movie_set: pd.DataFrame):
    """
    Function that consults the wikidata KG for a slice of the movies set
    :param slice_movie_set: slice of the movie data set with movie id as index and imdbId, Title, year and imdbUrl
    as columns
    :return: JSON with the results of the query
    """
    imdbIdList = slice_movie_set['full_imdbId'].to_list()

    imdbs = ""
    for i in range(0, len(imdbIdList)):
        imdbId = imdbIdList[i]
        imdbs += " ""\"""" + imdbId + """\" """

    endpoint_url = "https://query.wikidata.org/sparql"

    query = """
    SELECT DISTINCT
          ?itemLabel
          ?propertyItemLabel
          ?valueLabel ?value ?imdbId
        WHERE 
        {
          ?item wdt:P345 ?imdbId .
          ?item ?propertyRel ?value.
          VALUES ?imdbId {""" + imdbs + """} .
          ?propertyItem wikibase:directClaim ?propertyRel .
          SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } .
          FILTER( 
            ?propertyRel = wdt:P179 || 
            ?propertyRel = wdt:P136 || ?propertyRel = wdt:P170 || 
            ?propertyRel = wdt:P57 || ?propertyRel = wdt:P58 || ?propertyRel = wdt:P161 ||
            ?propertyRel = wdt:P725 ||  ?propertyRel = wdt:P1040 ||
            ?propertyRel = wdt:P86 || ?propertyRel = wdt:P162 ||  ?propertyRel = wdt:P272 || 
            ?propertyRel = wdt:P344 || ?propertyRel = wdt:P166 || ?propertyRel = wdt:P1411 || 
            ?propertyRel = wdt:P2515 ||
            ?propertyRel = wdt:P921 || ?propertyRel = wdt:P175
          )  
        }
        ORDER BY ?imdbId"""

    user_agent = "WikidatabotIntegration/1.0 intermidia) " \
                 "wiki-bot-integration/1.0"

    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    results_dic = results_to_dict(slice_movie_set, results)
    return results_dic


def results_to_dict(slice_movie_set: pd.DataFrame, props_movie: dict):
    """
    Function that returns vector of dictionaries with the results from the dbpedia to insert into data frame of all
    movie properties
    :param slice_movie_set: slice of the movie data set with movie id as index and imdbId, Title, year and imdbUrl
    as columns
    :param props_movie: results of the returned result from the wikidata query
    :return: vector of dictionaries of the results of the wikidata query that can be appendable to a pandas df
    """

    # change the index to the imdbId in order to add the movie_id based on the imdb latter
    slice_movie_set.reset_index(level=0, inplace=True)
    slice_movie_set = slice_movie_set.set_index("full_imdbId")

    filter_props = []
    for line in props_movie["results"]["bindings"]:
        m_title = line["itemLabel"]["value"]
        m_prop = line["propertyItemLabel"]["value"]
        m_obj = line["valueLabel"]["value"]
        m_obj_code = line["value"]["value"].split("/")[-1]
        m_imdb = line["imdbId"]["value"]

        dict_props = {"movie_id": slice_movie_set.loc[m_imdb, 'movie_id'], "title": m_title, "prop": m_prop,
                      "obj": m_obj, "obj_code": m_obj_code,"imdbId": m_imdb,}
        filter_props.append(dict_props)

    return filter_props


# read movies set dataset, remove moives with nan imdbLink, set index to movie id and sort by the
# full imdbid that matches with the wikidata format "ttXXXXXXX"
movies_set = pd.read_csv("../dataset/Items - hetrec_after_2000.dat", "\t",
                         header=None)
s_all_movies = len(movies_set)
movies_set.columns = ['movie_id', 'imdbId', 'title', 'year', 'imdbLink']
movies_set = movies_set[movies_set['imdbLink'].notnull()]
movies_set = movies_set.set_index('movie_id')
movies_set['full_imdbId'] = movies_set['imdbLink'].apply(lambda x: x.split("/")[-2])
movies_set = movies_set.sort_values(by=['full_imdbId'])

# create output, final dataframe with all properties of movies
all_movie_props = pd.DataFrame(columns=['movie_id', 'title', 'prop', 'obj', 'obj_code', 'imdbId'])

# obtaind properties of movies in 300 movies batches
begin = 0
end = 350
total = len(movies_set)

print("Start obtaining movie data")
while end <= total:
    results = get_movie_data_from_wikidata(movies_set.iloc[begin:end])
    all_movie_props = all_movie_props.append(results)
    print("From " + str(begin) + " to " + str(end-1) + " obtained from Wikidata")
    begin = end
    end = end + 300
print("End obtaining movie data")

# save output
all_movie_props.to_csv("./wikidata_integration_small.csv", mode='w', header=True, index=False)
print("Coverage: " + str(len(all_movie_props['movie_id'].unique())) + " obtained of " + str(s_all_movies)
      + ". Percentage: " + str(len(all_movie_props['movie_id'].unique())/s_all_movies))
print('Output file generated')