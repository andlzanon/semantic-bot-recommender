import numpy as np
import pandas as pd
import networkx as nx
from scipy.stats import entropy
from random import seed
from random import randint


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
    for prop in sub_graph['prop'].value_counts().index:
        o_values = sub_graph[(sub_graph['prop'] == prop)]['obj'].value_counts()
        denom = sum(o_values.values)
        prob = []
        for value in o_values.index:
            num = o_values[value]
            prob.append(num / denom)

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
    shrinked = sub_graph[(sub_graph['prop'] == prop) & (sub_graph['obj'] == obj)]

    for movie_id in shrinked.index.unique():
        shrinked = pd.concat([shrinked, sub_graph.loc[movie_id]])

    return shrinked.sort_index()


def order_movies_by_pagerank(sub_graph: pd.DataFrame, edgelist: pd.DataFrame,  watched: list, objects: list,
                             weight_vec: list, use_objs=False):
    """
    Function that order the movies based on its' pagerank on the graph. The adj matrix is created on the
    WikidataIntegration project, in the adjacency_matrix.py
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param edgelist: edge list of users and movies from the dataset. The dataframe has two columns, the origin of the
        edge and the destination
    :param watched: movies that the user watched
    :param objects: objects (e.g. Martin Scorsese, Leonardo Di Caprio, Bred Pitt, Disney, etc) on the graph that
        the user liked
    :param weight_vec: list with size two and sum equal to one with the weights of the personalization to the watched
    movies and the rest of the nodes
    :param use_objs: boolean value to use on the pagerank or not the objects list that the user liked
    :return: ordered movies on a DataFrame
    """

    # append edgelist that only hast movies and user edges and add the movies to values on the wikidata edges
    copy = sub_graph.copy()
    copy['origin'] = ['M' + x for x in copy.index.astype(str)]
    copy['destination'] = copy['obj_code']
    full_edgelist = pd.concat([edgelist, copy[['origin', 'destination']]])

    # create graph
    G = nx.from_pandas_edgelist(full_edgelist, 'origin', 'destination')

    # get movie codes for the watched movies
    movie_codes = ['M' + str(x) for x in watched]

    # if user did not watched any movies and dont want to use the prop values on the personalized PR
    # then personalization is none
    # else create personalization and assign weights on personalization dict
    preferences = movie_codes
    personalization = {}
    if not use_objs and (len(preferences) == 0):
        personalization = None
    elif use_objs:
        preferences = preferences + objects

    if personalization is not None:
        value_watched = weight_vec[0] / len(preferences)
        value_all = weight_vec[1] / (G.number_of_nodes() - len(preferences))

        for node in G.nodes:
            if node in preferences:
                personalization[node] = value_watched
            else:
                personalization[node] = value_all

    # calculate pagerank
    pr_np = nx.pagerank_scipy(G, personalization=personalization, max_iter=1000)

    # order movies
    ordered_movies = pd.DataFrame(index=sub_graph.index.unique(), columns=['value'])
    for m in sub_graph.index.unique():
        movie_code = 'M' + str(m)
        ordered_movies.at[m] = pr_np[movie_code]

    return ordered_movies.sort_values(by=['value'], ascending=False)


def order_movies_by_pop(sub_graph: pd.DataFrame, ratings: pd.DataFrame):
    """
    Function that order the movies based on its' popularity
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param ratings: ratings dataset in the format user_id, movie_id, rating
    :return: ordered movies on a DataFrame
    """
    ordered_movies = pd.DataFrame(index=sub_graph.index.unique(), columns=['value'])
    for m in sub_graph.index.unique():
        ordered_movies.at[m] = len(ratings[(ratings['movie_id'] == m)])

    return ordered_movies.sort_values(by=['value'], ascending=False)


def order_props(sub_graph: pd.DataFrame, global_zscore: dict, properties: list, weight_vec: list):
    """
    Function that order the properties based on the entropy of the property, the relevance of the value locally
    normalized measured by the zscore of the count of the property on the sub graph and the relevance of the value
    globally measured by the  zscore of the count of the property on the full graph
    :param sub_graph: sub graph that represents the current graph that matches the users preferences
    :param global_zscore: dictionary of all properties on the dataset (full graph)
        prop and obj keys and count and zscores as columns
    :param properties: properties list that the user has liked in the past. The list has tuples (property, value), e.g.
        (actor, Di Caprio); (producer, Disney); etc
    :param weight_vec: vector of weigths for the entropy and local and global relevance respectively
        the size of this list is 3 always
    :return: ordered properties on a DataFrame
    """

    # make slice of subgraph of just property and obj
    sub_slice = sub_graph[['prop', 'obj']]

    # calculate zscore locally
    split_dfs = pd.DataFrame(columns=['prop', 'obj', 'count'])
    for prop in sub_slice['prop'].unique():
        df_prop = sub_slice[sub_slice['prop'] == prop]
        df_lzscore = df_prop.copy()
        df_lzscore['count'] = df_prop.groupby('obj').transform('count')
        df_lzscore['local_zscore'] = (df_lzscore['count'] - df_lzscore['count'].mean()) / df_lzscore['count'].std()
        split_dfs = pd.concat([split_dfs, df_lzscore])

    split_dfs['global_zscore'] = split_dfs.apply(lambda x: global_zscore['global_zscore'][(x['prop'], x['obj'])], axis=1)

    # calculate entropy and create entropy column
    entrs = calculate_entropy(sub_graph)
    split_dfs['h'] = split_dfs.apply(lambda x: entrs[x['prop']], axis=1)

    # generate zscore for the entropy
    split_dfs['h_zscore'] = (split_dfs['h'] - split_dfs['h'].mean()) / split_dfs['h'].std()

    # replace na when std is nan to 0
    split_dfs = split_dfs.fillna(0)

    # sum the zscores for the total value
    split_dfs['value'] = (weight_vec[0] * split_dfs['h_zscore']) + \
                         (weight_vec[1] * split_dfs['local_zscore']) + \
                         (weight_vec[2] * split_dfs['global_zscore'])

    # remove the favorites to not show again
    for t in properties:
        split_dfs = split_dfs[(split_dfs['prop'] != t[0]) & (split_dfs['obj'] != t[1])]

    return split_dfs.sort_values(by=['value'], ascending=False)


def generate_global_zscore(full_graph: pd.DataFrame, path: str, flag=False):
    """
    Function that generates a dictionary with all the zscore of movies. If flag is true, generate file,
    else only reads the file
    :param full_graph: full graph of the movie dataset
    :param path: path to save the generated DataFrame
    :param flag: True to generate file of DataFrame with global zscores, False to read it
    :return: dictionary with prop and obj keys and count and zscores as columns
    """
    if flag:
        full_slice = full_graph[['prop', 'obj']]
        full_split_dfs = pd.DataFrame(columns=['prop', 'obj', 'count', 'global_zscore'])
        for prop in full_slice['prop'].unique():
            df_prop = full_slice[full_slice['prop'] == prop]
            df_gzscore = df_prop.copy()
            df_gzscore['count'] = df_prop.groupby('obj').transform('count')
            df_gzscore['global_zscore'] = (df_gzscore['count'] - df_gzscore['count'].mean()) / df_gzscore['count'].std()
            full_split_dfs = pd.concat([full_split_dfs, df_gzscore])

        full_split_dfs.to_csv(path, mode='w', header=True, index=False)

    return pd.read_csv(path, usecols=['prop', 'obj', 'count', 'global_zscore']).set_index(['prop', 'obj']).to_dict()


# import database and import of the ratings
full_prop_graph = pd.read_csv("../WikidataIntegration/wikidata_integration_small.csv")
full_prop_graph = full_prop_graph.set_index('movie_id')

ratings = pd.read_csv("../dataset/1851_movies_ratings.txt", sep='\t', header=None)
ratings.columns = ['user_id', 'movie_id', 'rating']

# generate user to movie partial graph to integrate on the method shrink graph with the properties
# the dataframe has two columns, the origin of the  edge and the destination
edgelist = pd.DataFrame(columns=['origin', 'destination'])
ratings['origin'] = ['U' + x for x in ratings['user_id'].astype(str)]
ratings['destination'] = ['M' + x for x in ratings['movie_id'].astype(str)]
edgelist = pd.concat([edgelist, ratings[['origin', 'destination']]])

# get the global zscore for the movies
g_zscore = generate_global_zscore(full_prop_graph, path="./global_properties.csv", flag=False)

# copy original property graph to shrink it
sub_graph = full_prop_graph.copy()

# start conversation
print("Hello, I'm here to help you choose a movie. We have these characteristics: \n")
print(*sub_graph['prop'].unique(), sep="\n", end="\n\n")
print("From which one are you interested in exploring today?")

# set end conversation to false to end the talk when movie rec is accepted
end_conversation = False

# ask user for fav prop and value and then shrink graph
p_chosen = str(input())
print("\nThese are the favorites along the characteristic:")
print(*prop_most_pop(sub_graph, p_chosen), sep="\n", end="\n\n")
print("Which one are you looking for in one of these?")
o_chosen = str(input())

# create vectors of movies and objects of preference and set seed and user id
watched = []
prefered_objects = [sub_graph[(sub_graph['prop'] == p_chosen) & (sub_graph['obj'] == o_chosen)]['obj_code'].unique()[0]]
prefered_prop = [(p_chosen, o_chosen)]
user_id = 'U' + str(ratings['user_id'].max() + 1)
seed(42)

# start the loop until the recommendation is accepted or there are no movies based on users' filters
while not end_conversation:
    # get subgraph based on property chosen and order properties
    sub_graph = shrink_graph(sub_graph, p_chosen, o_chosen)

    resp = "no"

    # while user did not like recommendation or property suggestion do not shrink graph again
    # or if sub graph is empty there are no entries or there are no movies, recommendation fails
    while resp == "no" or resp == "watched":
        # choose action and ask if user liked it
        ask = randint(0, 10) % 2

        # if ask == 0 suggest new property
        if ask == 0:
            # show most relevant property
            top_p = order_props(sub_graph, g_zscore, prefered_prop, [1/3, 1/3, 1/3])

            print("\nWhich of these properties do you like the most? Type the number of the preferred attribute or "
                  "answer \"no\" if you like none")
            dif_properties = top_p.drop_duplicates()[:5]
            for i in range(0, len(dif_properties)):
                p_topn = str(dif_properties.iloc[i]['prop'])
                o_topn = str(dif_properties.iloc[i]['obj'])
                print(str(i + 1) + ") " + p_topn + " - " + o_topn)

            # hear answer
            resp = input()

            # if user chose prop, get the prop, the obj and obj code and append it to the favorties properties
            # else remove all prop from graph
            if resp != "no":
                p_chosen = str(dif_properties.iloc[int(resp) - 1]['prop'])
                o_chosen = str(dif_properties.iloc[int(resp) - 1]['obj'])
                o_chose_code = str(sub_graph[(sub_graph['prop'] == p_chosen) & (sub_graph['obj'] == o_chosen)]['obj_code'].unique()[0])
                prefered_objects.append(o_chose_code)
                prefered_prop.append((p_chosen, o_chosen))
            else:
                for index, row in dif_properties.iterrows():
                    p = row[0]
                    o = row[1]
                    movies_with_prop = sub_graph.loc[(sub_graph['prop'] == p) & (sub_graph['obj'] == o)].index
                    for m in movies_with_prop:
                        top_p = top_p.drop(m)
                        sub_graph = sub_graph.drop(m)

        # if ask != 0 recommend movie
        else:
            top_m = order_movies_by_pagerank(sub_graph, edgelist, watched, prefered_objects, [0.8, 0.2], True)

            # case if all movies with properties were recommended but no movies were accepted by user
            if len(top_m.index) == 0:
                print("\nYou have already watched all the movies with the properties you liked :(")
                end_conversation = True
                break

            # show recommendation
            print("\nBased on your current preferences, this movie may be suited for you: ")
            print("\"" + full_prop_graph.loc[top_m.index[0]]['title'].unique()[0] + "\"")
            print("Because it has these properties that are relevant to you: ")
            for i in range(0, len(prefered_prop)):
                t = prefered_prop[i]
                print(str(i + 1) + ") " + str(t[0]) + " - " + str(t[1]))
            print("Did you like the recommendation, didn't like the recommendation or have you "
                  "already watched the movie? (yes/no/watched)")

            # hear answer
            resp = str(input())

            # if liked the recommendation end conversation
            # else if watched add edge to the graph
            if resp == "yes":
                print(
                    "\nHave a good time watching the movie \"" + full_prop_graph.loc[top_m.index[0]]['title'].unique()[
                        0] +
                    "\". Please come again!")
                end_conversation = True
            else:
                m_id = top_m.index[0]
                if resp == "watched":
                    watched.append(m_id)
                    edgelist = edgelist.append({"origin": user_id, "destination": 'M' + str(m_id)}, ignore_index=True)

                top_m = top_m.drop(m_id)
                sub_graph = sub_graph.drop(m_id)

        if len(sub_graph) == 0 or len(sub_graph.index.unique()) == 0:
            print("\nThere are no movies that corresponds to your preferences on our database "
                  "or you already watched them all")
            end_conversation = True
            break
