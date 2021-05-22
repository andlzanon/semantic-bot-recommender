# Semantic Bot Movie Recommender 

## Descrição do Algoritmo:
Codificação de um algoritmo de recomendação conversacional de filmes utilizando Linked Open Data.

A partir de uma propriedade (ator, tema, produtora, diretor, etc.) e valor (ação, Woody Allen, Scarlett Johansson, etc.) incialmente declarados pelo usuário, o algoritmo busca um subgrafo na Wikidata (https://www.wikidata.org/) de todos os filmes e propriedades deste que contém as preferências inicialmente declaradas pelo usuário.

Em seguida o sistema ordena essas outras propriedades dos filmes que com a característica  incialmente explicitada pelo usuário e vai perguntando por propriedades ou recomendações mais relevantes até que chegue a uma recomendação ou falhe por falta de opções.

## Detalhamento da Proposta:
1. Incialmente o usuário escolhe de maneira explícita uma aresta e um valor importante para ele em um filme
2. Em seguida o algoritmo busca um subgrafo com todos os filmes e respectivas propriedades para limitar o espaço de busca
3. O algoritmo escolhe uma ação, dentre duas, que são: recomendar um filme ou perguntar se uma outra propriedade é relevante para o usuário para buscar um novo subgrafo, baseado no subgrafo anterior
    - Para a escolha de ação, o sistema pode utilizar vários algoritmos de aprendizado por reforço:
      1. Aleatório
      2. E-greedy
      3. UCB
      4. Thompson Sampling
    - Para escolher a propriedade mais relvante é importante destacar que a propriedade é uma aresta e uma entidade no grafo, como, por exemplo, Morgan Freeman como ator. Assim, é realizada uma soma entre a entropia da propriedade (ator), somada com a relevância do valor (Morgan Freeman) no subgrafo e a relvância global do valor (Morgan Freeman) no grafo completo. Os valores são normalizados com o zscore e os pesos da entropia, e relevâncias locais e globais possuem pesos que podem ser configurados. O padrão é 0.33 para cada
    - Para a escolha do filme, atualmente é realizado um PageRank Personalizado em que 80% do peso são para filmes e propriedades que o usuário gostou e 20% para o resto dos nós (o grafo para o PR possui nós de usuários, filmes e valores como Morgan Freeman, a propriedade ator é uma aresta entre os filmes e o ator)

4. O algoritmo executa até que uma recomendação seja aceita pelo usuário ou não encontre mais soluções

## Reprodução:

1. Importar dataset deste [repositório](https://github.com/LuanSSouza/word-recommender-api/blob/master/dataset.rar)
2. Extrair dataset na raiz do projeto com nome da pasta dataset
3. Executar wikidata_integration.py do projeto [WikidataIntegration](https://github.com/andlzanon/semantic-bot-recommender/tree/main/WikidataIntegration) para gerar o arquivo [wikidata_integration_small.csv](https://github.com/andlzanon/semantic-bot-recommender/blob/main/WikidataIntegration/wikidata_integration_small.csv)
4. Executar main.py do projeto [SemanticBot](https://github.com/andlzanon/semantic-bot-recommender/tree/main/SemanticBot) para iniciar conversa

## Créditos de Bibliotecas:
Para instalar utilizar comando: 
    
    pip install requirements

* [numpy 1.19.1](https://numpy.org/)
* [pandas 1.0.4](https://pandas.pydata.org/)
* [scipy 1.5.0](https://www.scipy.org/)
* [networkx 2.5.0](https://github.com/networkx/networkx)
* [SPARQLWrapper 1.8.5](https://github.com/RDFLib/sparqlwrapper)

A integração com faixa etária indicativa foi realizada com API [OMBD](https://www.omdbapi.com/)

## Consulta SPARQL
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
    1) cast member - Samuel L. Jackson
    2) cast member - Brad Pitt
    3) cast member - Thomas Kretschmann
    4) screenwriter - Ronald Harwood
    5) cast member - Stanley Tucci
    2

    Which of these properties do you like the most? Type the number of the preferred attribute or answer "no" if you like none
    1) cast member - Samuel L. Jackson
    2) cast member - Cate Blanchett
    3) cast member - Shia LaBeouf
    4) cast member - Tilda Swinton
    5) genre - drama
    5

    Based on your current preferences, this movie may be suited for you: 
    "Inglourious Basterds"
    Because it has these properties that are relevant to you: 
    1) main subject - World War II
    2) cast member - Brad Pitt
    3) genre - drama
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    watched

    Which of these properties do you like the most? Type the number of the preferred attribute or answer "no" if you like none
    1) cast member - Cate Blanchett
    2) cast member - Shia LaBeouf
    3) cast member - Tilda Swinton
    4) award received - National Board of Review: Top Ten Films
    5) cast member - Jason Isaacs
    4

    Based on your current preferences, this movie may be suited for you: 
    "Fury"
    Because it has these properties that are relevant to you: 
    1) main subject - World War II
    2) cast member - Brad Pitt
    3) genre - drama
    4) award received - National Board of Review: Top Ten Films
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    watched

    Based on your current preferences, this movie may be suited for you: 
    "The Curious Case of Benjamin Button"
    Because it has these properties that are relevant to you: 
    1) main subject - World War II
    2) cast member - Brad Pitt
    3) genre - drama
    4) award received - National Board of Review: Top Ten Films
    Did you like the recommendation, didn't like the recommendation or have you already watched the movie? (yes/no/watched)
    yes

    Have a good time watching the movie "The Curious Case of Benjamin Button". Please come again!