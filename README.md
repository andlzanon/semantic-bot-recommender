# Semantic Bot Movie Recommender 

## Descrição do Algoritmo:
Codificação de um algoritmo de recomendação conversacional de filmes utilizando Linked Open Data.

A partir de uma propriedade (ator, tema, produtora, diretor, etc.) e valor (ação, Woody Allen, Scarlett Johansson, etc.) incialmente declarados pelo usuário, o algoritmo busca um subgrafo na Wikidata (https://www.wikidata.org/) de todos os filmes e propriedades deste que contém as preferências inicialmente declaradas pelo usuário.

Em seguida o sistema ordena essas outras propriedades dos filmes que com a característica  incialmente explicitada pelo usuário e vai perguntando por propriedades ou recomendações mais relevantes até que chegue a uma recomendação ou falhe por falta de opções.

## Detalhamento da Proposta:
1. Incialmente o usuário escolhe de maneira explícita uma aresta e um valor importante para ele em um filme
2. Em seguida o algoritmo busca um subgrafo com todos os filmes e respectivas propriedades para limitar o espaço de busca
3. O algoritmo escolhe uma ação, dentre duas, que são: recomendar um filme ou perguntar se uma outra propriedade é relevante para o usuário para buscar um novo subgrafo, baseado no subgrafo anterior
    - Para a escolha de ação, atualmente o sistema considera aleatoriamente um número, se for par realiza uma pergunta por propriedade e caso o contrário recomenda um filme
    - Para escolher a propriedade mais relvante é importante destacar que a propriedade é uma aresta e uma entidade no grafo, como, por exemplo, Morgan Freeman como ator. Assim, é realizada uma multiplicação entre a entropia da propriedade, considerando a probabilidade de ocorrer cada valor da propriedade, multiplicado pelo TF-IDF do valor considerando o subgrafo e o grafo completo
    - Para a escolha do filme, atualmente é escolhido o mais popular dentre aqueles que possuem as propriedades de preferencia do usuário

4. O algoritmo executa até que uma recomendação seja aceita pelo usuário ou não encontre mais soluções

## Reprodução:

1. Importar dataset deste [repositório](https://github.com/LuanSSouza/word-recommender-api/blob/master/dataset.rar)
2. Extrair dataset na raiz do projeto com nome da pasta dataset
3. Executar main.py do projeto [WikidataIntegration](https://github.com/andlzanon/semantic-bot-recommender/tree/main/WikidataIntegration) para gerar o arquivo [wikidata_integration_small.csv](https://github.com/andlzanon/semantic-bot-recommender/blob/main/WikidataIntegration/wikidata_integration_small.csv)
4. Executar main.py do projeto [SemanticBot](https://github.com/andlzanon/semantic-bot-recommender/tree/main/SemanticBot) para iniciar conversa

## Créditos de Bibliotecas:
Para instalar utilizar comando: 
    
    pip install requirements

* [numpy 1.19.1](https://numpy.org/)
* [pandas 1.0.4](https://pandas.pydata.org/)
* [scipy 1.5.0](https://www.scipy.org/)
* [SPARQLWrapper 1.8.5](https://github.com/RDFLib/sparqlwrapper)

## Consulta SPARQL
    SELECT DISTINCT
      ?itemLabel
      ?propertyItemLabel
      ?valueLabel ?imdbId
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
    ORDER BY ?imdbId

## Exemplo de Conversa

    Hello, I'm here to help you choose a movie. We have these characteristics: 

    director
    screenwriter
    composer
    genre
    cast member
    producer
    production company
    director of photography
    main subject
    film editor
    costume designer
    award received
    nominated for
    performer
    part of the series
    voice actor
    creator

    From which one are you interested in exploring today?
    main subject

    These are the favorites along the characteristic:
    revenge
    terrorism
    dysfunctional family
    serial killer
    supernatural
    time travel
    World War II
    aviation
    incest
    suicide

    Which one are you looking for in one of these?
    World War II

    Which of these properties do you like the most? Type the number of the preferred attribute or answer "no" if you like none
    1- drama as genre
    2- war film as genre
    3- Alexandre Desplat as cast member
    4- National Board of Review: Top Ten Films as award received
    5- Liev Schreiber as cast member
    1

    Based on your current preferences, this movie may be suited for you: 
    "The Pianist"
    Because it has these properties that are relevant to you: 
    1: drama as genre
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    no

    Which of these properties do you like the most? Type the number of the preferred attribute or answer "no" if you like none
    1- Alexandre Desplat as cast member
    2- National Board of Review: Top Ten Films as award received
    3- Quentin Tarantino as cast member
    4- Academy Award for Best Writing, Adapted Screenplay as award received
    5- Academy Award for Best Writing, Adapted Screenplay as nominated for
    3

    Which of these properties do you like the most? Type the number of the preferred attribute or answer "no" if you like none
    1- Academy Award for Best Supporting Actor as award received
    2- Academy Award for Best Supporting Actor as nominated for
    3- Lawrence Bender as producer
    4- Sally Menke as film editor
    5- Robert Richardson as director of photography
    1

    Based on your current preferences, this movie may be suited for you: 
    "Inglourious Basterds"
    Because it has these properties that are relevant to you: 
    1: drama as genre
    2: Quentin Tarantino as cast member
    3: Academy Award for Best Supporting Actor as award received
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    yes

    Have a good time watching the movie "Inglourious Basterds". Please come again!