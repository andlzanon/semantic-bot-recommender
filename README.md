# Semantic Bot Movie Recommender 

## Algorithm Description:
Conversacional recommender system with Linked Open Data. Given an property (actor, director, genre, etc) and a value (di Caprio, Tarantino, drama, etc) on the Wikidata (https://www.wikidata.org/) knowledge graph (KG), the system talks to the user asking questions about other properties or recommending movies. The systems ranks the property, value tuple and based on the Personalized Page-Rank algorithm on the KG and a reinforcement learning algorithm chooses if the system will ask a question for a movie property or recommend. The session finishes until a suggestion is accepted by the user or there aren't any movies left with the properties that the user liked.  

## Implementation Details of the Proposal:
1. Initially the user chooses a property and a value relevant to her/him on a movie; 
2. Then, the algorithm reduces the original graph into a subgraph to limit the search space. The movies and properties are the ones that contains the property and value chosen by the user as relevants;
3. The algorithm chooses an action between: asking a question or recommending a movie;
    - To choose an action four algorithms were implemented:
      1. Random
      2. E-greedy
      3. UCB
      4. Thompson Sampling
    - Currently the Thompson Sampling is the one running on the system;
    - To rank the properties the formula bellow is used. The first term is the entropy of the property (actor, director, genre, etc). This term is responsible to choose a property that will reduce mostly the current graph in order to lower the quantity of questions. The second term is responsible to compute the local relevance of the value based on the Personalized PageRank of the subgraph with 80% of the weight to movies and values that the user liked and 20% to the rest of the nodes. The final term is the global relevance based on the Personalized PageRank of the full Wikidata graph. All the terms are normalized with zscore and weighted. The weights are currently 0.33 to each;  

        <img src="https://render.githubusercontent.com/render/math?math=value =\alpha*zscore(entropy(p)) %2B \beta*zscore(pagerank(subgraph, value)) %2B \gama*zscore(pagerank(fullgraph, value))">

    - To choose a movie the same Personalized Page Rank is used with 80% of the weight to movies and values that the user liked and 20% to the rest of the nodes.

4. The algorithm loops between 2 and 3 until a recommendation is accepted.

## Reproduce Results:

1. Import dataset from this [repository](https://github.com/LuanSSouza/word-recommender-api/blob/master/dataset.rar);
2. Extract dataset on the root of this project;
3. (Optional) Execute the wikidata_integration.py of the project [WikidataIntegration](https://github.com/andlzanon/semantic-bot-recommender/tree/main/WikidataIntegration) to generate the file [wikidata_integration_small.csv](https://github.com/andlzanon/semantic-bot-recommender/blob/main/WikidataIntegration/wikidata_integration_small.csv);
4. Execute the main.py of the project [SemanticBot](https://github.com/andlzanon/semantic-bot-recommender/tree/main/SemanticBot) to start the conversacion. 

## Libraries used:
To install the libraries use the command: 
    
    pip install requirements

* [numpy 1.19.1](https://numpy.org/)
* [pandas 1.0.4](https://pandas.pydata.org/)
* [scipy 1.5.0](https://www.scipy.org/)
* [requests 2.25.1](https://github.com/psf/requests)
* [networkx 2.5.0](https://github.com/networkx/networkx)
* [SPARQLWrapper 1.8.5](https://github.com/RDFLib/sparqlwrapper)

The integration to get the ratings of the movies (PG, R, etc) the [OMBD](https://www.omdbapi.com/) API was used.

## SPARQL Query
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
        ?propertyRel = wdt:P179 || ?propertyRel = wdt:P136 || 
        ?propertyRel = wdt:P170 || ?propertyRel = wdt:P57 || 
        ?propertyRel = wdt:P58 || ?propertyRel = wdt:P161 ||
        ?propertyRel = wdt:P725 ||  ?propertyRel = wdt:P1040 ||
        ?propertyRel = wdt:P86 || ?propertyRel = wdt:P162 ||  
        ?propertyRel = wdt:P272 || ?propertyRel = wdt:P344 || 
        ?propertyRel = wdt:P166 || ?propertyRel = wdt:P1411 || 
        ?propertyRel = wdt:P2515 || ?propertyRel = wdt:P921 || 
        ?propertyRel = wdt:P175
      )  
    }
    ORDER BY ?imdbId

## Example of Conversacion

    Hello, I'm here to help you choose a movie. What's your age? 
    24
    We have these characteristics from our movie database: 

    director
    screenwriter
    composer
    genre
    cast member
    producer
    production company
    director of photography
    film editor

    From which one are you interested in exploring today?
    director

    These are the favorites along the characteristic:
    Steven Soderbergh
    Woody Allen
    Ridley Scott
    Steven Spielberg
    Clint Eastwood
    Shawn Levy
    Robert Rodriguez
    Brett Ratner
    Martin Scorsese
    Dennis Dugan
    Next Page ->
    Which one are you looking for in one of these? Type "Next Page" or  "Previous Page"  to see more properties
    Martin Scorsese

    Based on your current preferences, this Not Rated rated movie may be suited for you: 
    "George Harrison: Living in the Material World"
    Because it has these properties that are relevant to you: 
    1) director - Martin Scorsese
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    no

    Which of these properties do you like the most? Type the number of the preferred attribute or type "Next Page" or  "Previous Page"  to see more properties and "Recommend" to suggest a movie
    1) genre - drama
    2) genre - comedy film
    3) genre - documentary film
    4) cast member - Elia Kazan
    5) cast member - Ben Kingsley
    Recommend
    Next Page ->
    1

    Which of these properties do you like the most? Type the number of the preferred attribute or type "Next Page" or  "Previous Page"  to see more properties and "Recommend" to suggest a movie
    1) genre - comedy film
    2) cast member - Ben Kingsley
    3) cast member - Mark Ruffalo
    4) cast member - Leonardo DiCaprio
    5) cast member - Jonah Hill
    Recommend
    Next Page ->
    4

    Based on your current preferences, this R rated movie may be suited for you: 
    "The Wolf of Wall Street"
    Because it has these properties that are relevant to you: 
    1) director - Martin Scorsese
    2) genre - drama
    3) cast member - Leonardo DiCaprio
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    watched

    Based on your current preferences, this R rated movie may be suited for you: 
    "Shutter Island"
    Because it has these properties that are relevant to you: 
    1) director - Martin Scorsese
    2) genre - drama
    3) cast member - Leonardo DiCaprio
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    watched

    Which of these properties do you like the most? Type the number of the preferred attribute or type "Next Page" or  "Previous Page"  to see more properties and "Recommend" to suggest a movie
    1) cast member - Matt Damon
    2) cast member - Liam Neeson
    3) cast member - Willem Dafoe
    4) cast member - Brendan Gleeson
    5) cast member - Jim Broadbent
    Recommend
    Next Page ->
    2

    Based on your current preferences, this R rated movie may be suited for you: 
    "Gangs of New York"
    Because it has these properties that are relevant to you: 
    1) director - Martin Scorsese
    2) genre - drama
    3) cast member - Leonardo DiCaprio
    4) cast member - Liam Neeson
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    yes

    Have a good time watching the movie "Gangs of New York". Please come again!