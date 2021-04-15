import numpy as np
import pandas as pd
from scipy.stats import entropy
from random import seed
from random import randint


def tf_idf(sub_graph: pd.DataFrame, full_graph: pd.DataFrame, prop: str, obj: str):
    """
    Function that returns the tf-idf of property and value tuple
    :param full_graph: full graph with all movies properties from wikidata
    :param prop: property to value tf-idf
    :param obj: value to value tf-idf
    :return: float tf-idf of the property (e.g. Woody Allen as a director)
    """
    tf = len(sub_graph.loc[(sub_graph['prop'] == prop) & (sub_graph['obj'] == obj)])
    n = len(full_graph.index.unique())
    idf = np.log((n/tf))

    tfidf = tf * idf

    return tfidf


def prop_most_pop(sub_graph: pd.DataFrame, prop: str):
    """
    Function that returns the most popular values for property prop
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param prop: property the user is looking for
    :return: list of the ten most popular values of property
    """
    return sub_graph[(sub_graph['prop'] == prop)]['obj'].value_counts().index.values[:10]


def calculate_entropy(sub_graph: pd.DataFrame):
    """
    Function that calculates the entropy for all properties
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :return: entropies of properties on dictionary
    """
    entropies = {}
    for prop in sub_graph['prop'].unique():
        values = sub_graph[(sub_graph['prop'] == prop)]['obj'].unique()
        denom = len(sub_graph[(sub_graph['prop'] == prop)]['obj'])
        prob = []
        for value in values:
            num = len(sub_graph.loc[(sub_graph['prop'] == prop) & (sub_graph['obj'] == value)])
            prob.append(num/denom)

        entropies[prop] = entropy(prob, base=2)

    return entropies


def shrink_graph(sub_graph: pd.DataFrame, prop: str, obj: str):
    """
    Function that shrinks the graph to a sub graph based on the property and value passed on the parameters.
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param prop: property the user is looking for
    :param obj: value of property the user is looking for
    :return: shirked graph of the one passed as parameter
    """
    shrinked = sub_graph.loc[(sub_graph['prop'] == prop) & (sub_graph['obj'] == obj)]

    for movie_id in shrinked.index.unique():
        shrinked = pd.concat([shrinked, sub_graph.loc[movie_id]])

    shrinked = shrinked.loc[(shrinked['prop'] != prop) & (shrinked['obj'] != obj)]
    return shrinked.sort_index()


def order_movies(sub_graph: pd.DataFrame, ratings: pd.DataFrame):
    """
    Function that order the movies based on its' popularity
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param ratings: ratings dataset in the format user_id, movie_id, rating
    :return: ordered movies on a DataFrame
    """
    ordered_movies = pd.DataFrame(index=sub_graph.index.unique(), columns=['value'])
    for m in sub_graph.index.unique():
        ordered_movies.loc[m] = len(ratings[(ratings['movie_id'] == m)])

    return ordered_movies.sort_values(by=['value'], ascending=False)


def order_props(sub_graph: pd.DataFrame,  full_graph: pd.DataFrame):
    """
    Function that order the properties based on the entropy of the property and the relevance of the value
    measured by the tf-idf metric
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param full_graph: full graph with all movies properties from wikidata
    :return: ordered properties on a DataFrame
    """
    ordered_properties = sub_graph.loc[(sub_graph['prop'] != 'director') & (sub_graph['obj'] != 'Woody Allen')][['prop', 'obj']]
    ordered_properties['entropy'] = np.nan
    ordered_properties['tf_idf'] = np.nan
    ordered_properties['value'] = np.nan

    entrs = calculate_entropy(sub_graph)
    for index, row in ordered_properties.iterrows():
        prop = row[0]
        obj = row[1]
        h = entrs[prop]
        rel = tf_idf(sub_graph, full_graph, prop, obj)
        ordered_properties.loc[(ordered_properties.index == index) & (ordered_properties['prop'] == prop) &
                               (ordered_properties['obj'] == obj), 'entropy'] = h
        ordered_properties.loc[(ordered_properties.index == index) & (ordered_properties['prop'] == prop) &
                               (ordered_properties['obj'] == obj), 'tf_idf'] = rel
        ordered_properties.loc[(ordered_properties.index == index) & (ordered_properties['prop'] == prop) &
                               (ordered_properties['obj'] == obj), 'value'] = rel * h

    return ordered_properties.sort_values(by=['value'], ascending=False)


def order_props_and_movies(sub_graph: pd.DataFrame, full_graph: pd.DataFrame, ratings: pd.DataFrame):
    """
    Function that orders properties and movies based on user choices
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param full_graph: full graph with all movies properties from wikidata
    :param ratings: ratings dataset in the format user_id, movie_id, rating
    :return: the ordered movies and properties DataFrames
    """
    ordered_movies = order_movies(sub_graph, ratings)
    ordered_props = order_props(sub_graph, full_graph)

    return ordered_movies, ordered_props


# import database and import of the ratings
prop_df = pd.read_csv("../WikidataIntegration/wikidata_integration_small.csv")
prop_df = prop_df.set_index('movie_id')

ratings = pd.read_csv("../dataset/1851_movies_ratings.txt", sep='\t', header=None)
ratings.columns = ['user_id', 'movie_id', 'rating']

# copy original property graph to shrink it
sub_graph = prop_df.copy()

# start conversation
print("Hello, I'm here to help you choose a movie. We have these characteristics: \n")
print(*sub_graph['prop'].unique(), sep="\n", end="\n\n")
print("From which one are you interested in exploring today?")

# set end conversation to false to end the talk when movie rec is accepted
end_conversation = False

# ask user for fav prop and value and then shrink graph
p_chosen = str(input())
print("These are the favorites along the characteristic:")
print(*prop_most_pop(sub_graph, p_chosen),sep="\n", end="\n\n")
print("Which one are you looking for in one of these?")
o_chosen = str(input())

watched = []
seed(42)
# start the loop until the recommendation is accepted or there are no movies based on users' filters
while not end_conversation:

    # get subgraph based on property chosen and order properties
    sub_graph = shrink_graph(sub_graph, p_chosen, o_chosen)
    top_m, top_p = order_props_and_movies(sub_graph, prop_df, ratings)

    resp = "no"

    # while user did not like recommendation or property suggestion do not shrink graph again
    # or if sub graph is empty there are no entries or there are no movies, recommendation fails
    while resp == "no" or resp == "watched":
        # choose action and ask if user liked it
        ask = randint(0, 10) % 2

        # if ask == 0 suggest new property
        if ask == 0:
            # show most relevant property
            p_chosen = str(top_p.iloc[0]['prop'])
            o_chosen = str(top_p.iloc[0]['obj'])
            print("Do you like or not the " + p_chosen + " " + o_chosen + "? (yes/no)")

            # hear answer
            resp = str(input())

            if resp == "no":
                movies_with_prop = sub_graph.loc[(sub_graph['prop'] == p_chosen) & (sub_graph['obj'] == o_chosen)].index
                top_m = top_m.drop(movies_with_prop)
                top_p = top_p.drop(movies_with_prop)
                sub_graph = sub_graph.drop(movies_with_prop)

        # if ask != 0 recommend movie
        else:
            print("Based on your current preferences, this movie may be suited for you: ")

            # case if all movies with properties were recommended but no movies were accepted by user
            if len(top_m.index) == 0:
                print("You have already watched all the movies with the properties you liked :(")
                end_conversation = True
                break

            # show recommendation
            print(prop_df.loc[top_m.index[0]]['title'].unique()[0])
            print("Did you like the recommendation, didn't like the recommendation or have you "
                  "already watched the movie? (yes/no/watched)")

            # hear answer
            resp = str(input())

            # if liked the recommendation end conversation
            if resp == "yes":
                print("Have a good time watching the movie " + prop_df.loc[top_m.index[0]]['title'].unique()[0] +
                      ". Please come again!")
                end_conversation = True
            else:
                m_id = top_m.index[0]
                top_m = top_m.drop(m_id)
                top_p = top_p.drop(m_id)
                sub_graph = sub_graph.drop(m_id)

        if len(sub_graph) == 0 or len(top_m) == 0 or len(top_p) == 0:
            print("There are no movies that corresponds to your preferences on our database "
                  "or you already watched them all")
            end_conversation = True
            break
