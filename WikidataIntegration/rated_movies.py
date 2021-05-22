import traceback
import pandas as pd
import requests

movies = pd.read_csv("../WikidataIntegration/wikidata_integration_small.csv", usecols=['movie_id', 'title', 'imdbId'])
movies = movies.set_index('movie_id')

rated_movies = pd.read_csv("./rated_movies.csv", usecols=['movie_id', 'rated'])
rated_movies = rated_movies.set_index('movie_id')

# api-endpoint
api_url = "http://www.omdbapi.com/"

for m in rated_movies.loc[rated_movies['rated'].isna() == True].index:
    try:
        movie_id = str(m)

        if (type(movies.loc[m, 'title']) is not str) and (movies.loc[m, 'imdbId'] is not str):
            movie_name = movies.loc[m, 'title'].values[0]
            imdb = movies.loc[m, 'imdbId'].values[0]
        else:
            movie_name = movies.loc[m, 'title']
            imdb = movies.loc[m, 'imdbId']

        # defining a params dict for the parameters to be sent to the API
        params = {'i': imdb,
                  'apikey': 'api_key'}

        # sending get request and saving the response as response object
        r = requests.get(url=api_url, params=params)

        # extracting data in json format
        data = r.json()

        rate = data['Rated']

        rated_movies.loc[m, 'rated'] = rate

        print("Movie \"" + movie_name + "\" is rated as : \"" + rate + "\" - id: " + movie_id)

    except KeyError:
        print(data['Error'])
        break

    except Exception as e:
        traceback.print_exc()
        break

rated_movies = rated_movies.reset_index(level='movie_id')
rated_movies.to_csv("./rated_movies.csv", mode='w', header=True, index=False)