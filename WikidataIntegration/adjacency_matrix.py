import numpy as np
import pandas as pd


def movie_props_list(movie_id: int, all_movies_props: pd.DataFrame):
    """
    Get the movies properties from the data frame all_movie_props
    :param all_movies_props: data frame to extract movie properties from
    :param movie_id: id of the movie to extract the properties
    :return: a list of tuples with all of the movie properties
    """

    try:
        movie_props = all_movies_props.loc[movie_id]

        # when movie_props size is two, it means that there is only one line of return
        # and the command on line 63 wont work
        if len(movie_props) > 2:
            movie_tuples = [tuple(x) for x in movie_props.to_numpy()]
        else:
            movie_tuples = [(movie_props[0], movie_props[1])]

    except KeyError:
        movie_tuples = []

    return movie_tuples


def movie_to_movie_adj_matrix(full_graph: pd.DataFrame):
    movies = full_graph.index.unique().sort_values()

    # create empty dataFrame with  movie id as column and index
    adj_matrix = pd.DataFrame(index=movies, columns=movies)
    adj_matrix = adj_matrix.fillna(0)

    # for all movies fill the adjacency matrix, with the weight of the edge as the number of equal properties on the
    # graph
    for i in range(0, len(movies)):
        movie1 = movies[i]
        movie1_props = movie_props_list(movie1, full_prop_graph)

        for j in range(i, len(movies)):
            movie2 = movies[j]

            if movie1 != movie2:
                movie2_props = movie_props_list(movie2, full_prop_graph)

                intersection = pd.Series(list(set(movie1_props).intersection(set(movie2_props))), dtype=str)
                if len(intersection) > 0:
                    n = len(intersection)
                    adj_matrix.at[movie1, movie2] = n
                    adj_matrix.at[movie2, movie1] = n
                    print("movie1: " + str(movie1) + " movie2: " + str(movie2) + " adj: " + str(n))
                else:
                    adj_matrix.at[movie1, movie2] = 0
                    adj_matrix.at[movie2, movie1] = 0
                    print("movie1: " + str(movie1) + " movie2: " + str(movie2) + " adj: 0")

            else:
                adj_matrix.at[movie1, movie2] = 0
                adj_matrix.at[movie2, movie1] = 0
                print("movie1: " + str(movie1) + " movie2: " + str(movie2) + " adj: 0")

    # save matrix
    adj_matrix.to_csv("./movie_to_movie_adj_matrix.csv", mode='w', header=False, index=False)


def movie_user_prop_adj_matrix(full_graph: pd.DataFrame, movie_rattings: pd.DataFrame):
    # create empty dataFrame with  movie id as column and index
    edgelist = pd.DataFrame(columns=['origin', 'destination'])

    movie_rattings['origin'] = 'U' + movie_rattings['user_id'].astype(str)
    movie_rattings['destination'] = 'M' + movie_rattings['movie_id'].astype(str)
    edgelist = pd.concat([edgelist, movie_rattings[['origin', 'destination']]])

    copy = full_graph.copy()
    copy['origin'] = 'M' + copy.index.astype(str)
    copy['destination'] = copy['obj_code']
    copy['weight'] = 1
    edgelist = pd.concat([edgelist, copy[['origin', 'destination']]])

    # save matrix
    edgelist.to_csv("./movie_user_prop_adj_matrix.csv", mode='w', header=True, index=False)


# read full property graph and set index to movie id
full_prop_graph = pd.read_csv("../WikidataIntegration/wikidata_integration_small.csv",
                              usecols=['movie_id', 'prop', 'obj', 'obj_code'])
full_prop_graph = full_prop_graph.set_index('movie_id')

ratings = pd.read_csv("../dataset/1851_movies_ratings.txt", sep='\t', header=None)
ratings.columns = ['user_id', 'movie_id', 'rating']

movie_user_prop_adj_matrix(full_prop_graph, ratings)




