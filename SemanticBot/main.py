import numpy as np
import pandas as pd
import utils
from bandit import thompson_sampling as ts


# import database and import of the ratings
full_prop_graph = pd.read_csv("../WikidataIntegration/wikidata_integration_small.csv")
full_prop_graph = full_prop_graph.set_index('movie_id')

ratings = pd.read_csv("../dataset/1851_movies_ratings.txt", sep='\t', header=None)
ratings.columns = ['user_id', 'movie_id', 'rating']

movie_rate = pd.read_csv("../WikidataIntegration/rated_movies.csv", usecols=['movie_id', 'rated'])
movie_rate = movie_rate.set_index('movie_id')

# generate user to movie partial graph to integrate on the method shrink graph with the properties
# the dataframe has two columns, the origin of the  edge and the destination
edgelist = pd.DataFrame(columns=['origin', 'destination'])
ratings['origin'] = ['U' + x for x in ratings['user_id'].astype(str)]
ratings['destination'] = ['M' + x for x in ratings['movie_id'].astype(str)]
edgelist = pd.concat([edgelist, ratings[['origin', 'destination']]])

# get the global zscore for the movies
g_zscore = utils.generate_global_zscore(full_prop_graph, path="./global_properties.csv", flag=False)

# copy original property graph to shrink it
sub_graph = full_prop_graph.copy()

# create bandit to decide when to ask and recommend
ban = ts.ThompsonSamplingBandit(2)

# start conversation
print("Hello, I'm here to help you choose a movie. What's your age? ")
age = int(input())

sub_graph = utils.remove_films_by_age(age, movie_rate, sub_graph)

print("We have these characteristics from our movie database: \n")
print(*sub_graph['prop'].unique(), sep="\n", end="\n\n")
print("From which one are you interested in exploring today?")

# set end conversation to false to end the talk when movie rec is accepted
end_conversation = False

# ask user for fav prop and value and then shrink graph
p_chosen = str(input())
print("\nThese are the favorites along the characteristic:")
print(*utils.prop_most_pop(sub_graph, p_chosen), sep="\n", end="\n\n")
print("Which one are you looking for in one of these?")
o_chosen = str(input())

# create vectors of movies and objects of preference and set seed and user id
watched = []
prefered_objects = [sub_graph[(sub_graph['prop'] == p_chosen) & (sub_graph['obj'] == o_chosen)]['obj_code'].unique()[0]]
prefered_prop = [(p_chosen, o_chosen)]
user_id = 'U' + str(ratings['user_id'].max() + 1)
np.random.RandomState(42)

# start the loop until the recommendation is accepted or there are no movies based on users' filters
while not end_conversation:
    # get subgraph based on property chosen and order properties
    sub_graph = utils.shrink_graph(sub_graph, p_chosen, o_chosen)

    resp = "no"

    # while user did not like recommendation or property suggestion do not shrink graph again
    # or if sub graph is empty there are no entries or there are no movies, recommendation fails
    while resp == "no" or resp == "watched":
        # choose action and ask if user liked it
        ask = ban.pull()
        reward = 0

        # if ask suggest new property
        if ask and len(sub_graph.index.unique()) > 1:
            # show most relevant property
            top_p = utils.order_props(sub_graph, g_zscore, prefered_prop, [1/3, 1/3, 1/3])

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
                if resp == 1:
                    reward = 1

            else:
                for index, row in dif_properties.iterrows():
                    p = row[0]
                    o = row[1]
                    sub_graph = sub_graph.loc[(sub_graph['obj'] != o)]

        # if ask == 0 recommend movie
        else:
            top_m = utils.order_movies_by_pagerank(sub_graph, edgelist, watched, prefered_objects, [0.8, 0.2], True)

            # case if all movies with properties were recommended but no movies were accepted by user
            if len(top_m.index) == 0:
                print("\nYou have already watched all the movies with the properties you liked :(")
                end_conversation = True
                break

            # show recommendation
            print("\nBased on your current preferences, this " + movie_rate.loc[top_m.index[0], 'rated'] +
                  " rated movie may be suited for you: ")
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
                    reward = 1
                    watched.append(m_id)
                    edgelist = edgelist.append({"origin": user_id, "destination": 'M' + str(m_id)}, ignore_index=True)

                top_m = top_m.drop(m_id)
                sub_graph = sub_graph.drop(m_id)

        # updated bandit based on the response of the user
        ban.update(ask, reward)

        # if there are no movies to recommend end conversation
        if len(sub_graph) == 0 or len(sub_graph.index.unique()) == 0:
            print("\nThere are no movies that corresponds to your preferences on our database "
                  "or you already watched them all")
            end_conversation = True
            break

# show bandit statistics
# ban.show_statistics()
