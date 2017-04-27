# yelp-fusion
Python module for managing access to and querying the Yelp Fusion API (version 3)

Requires:

  - requests
  - pytz (for determining the quota refresh time)
  
Prior to use, acquire a client_id and client_secret from Yelp, by setting up an App with Yelp Developers (https://www.yelp.com/developers).

Then, set up the client as follows:

`from yelpfusion import YelpFusion`

`client_id = "YOUR_CLIENT_ID"`
`client_secret = "YOUR_CLIENT_SECRET"`

`client = YelpFusion(client_id, client_secret)`

With the client, an access token is generated, passed to each of the API queries as below:

- Search API: https://www.yelp.com/developers/documentation/v3/business_search

Retrieve up to 1,000 businesses (the maximum) related to the search term "coffee". The query is automatically paginated, requiring 1 API call per 50 results:

`results = client.search(term='coffee', latitude=40.783565, longitude=-73.964658, limit=1000)`

Query based on an address, filtering by other parameters:

`results = client.search(term='pizza', location='New York', radius=1000, categories='restaurants,italian', locale='en_US', limit=10, offset=5, sort_by='distance', price='1,2', open_now=True)`

- Obtain business details: https://www.yelp.com/developers/documentation/v3/business

`businessid = results['businesses'][0]['id']`

`client.business_details(businessid)`

- Obtain business reviews: https://www.yelp.com/developers/documentation/v3/business_reviews

`client.business_reviews(businessid))`
