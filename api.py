# Import required modules.
import requests
import pytz
import datetime
import time

# Pacific timezone used for setting the Yelp API quota refresh time.
zone = pytz.timezone('US/Pacific')


# Function to query url and convert json to dict.
def url_query(url, params=None, headers=None, reqtype='get', repeat=0):

    # Attempt GET or POST request for given parameters and headers.
    try:
        if reqtype.lower() == 'get':
            if params is not None:
                request = requests.get(url, params, headers=headers, timeout=30)
            else:
                request = requests.get(url, headers=headers, timeout=30)
        elif reqtype.lower() == 'post':
            request = requests.post(url, params, timeout=30)
        if request.status_code == 200:
            results = request.json()
            return results

        # If over quota limit, determine Yelps quota limit refresh time, and
        # sleep until then.
        elif request.status_code == 429:
            start = datetime.datetime.now(zone)
            end = datetime.datetime(start.year, start.month, start.day, tzinfo=zone)
            end += datetime.timedelta(days=1)
            wait = end - start
            seconds = wait.seconds + 60
            print('Over quota limit, sleeping {0} seconds'.format(seconds))
            time.sleep(seconds)
            return url_query(url, params, headers, reqtype, repeat)
        else:
            request.raise_for_status()

    # Repeat query upon fail up to 5 times (to avoid timeout errors), or print
    # Exception error if still failing after 5 attempts.
    except Exception as e:
        if repeat < 5:
            repeat += 1
            return url_query(url, params, headers, reqtype, repeat)
        else:
            error = 'Failed on url {0}'.format(url)
        if params:
            error += ' with parameters {0}'.format(params)
        print(error)
        print(e)


class YelpFusion(object):
    def __init__(self, client_id, client_secret):
        """
        Class to manage access to the Yelp Fusion API (v3). Obtain a client_id
        and client_secret by signing up with Yelp developers and creating an
        app at: https://www.yelp.com/developers/

        Parameters:

        - client_id (str):
            Alphanumeric client ID for your application.

        - client_secret (str):
            Alphanumeric client secret (password) for your application.

        """

        # Request access token, and build header for subsequent queries.
        params = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        request = url_query('https://api.yelp.com/oauth2/token',
                            params, reqtype='post')
        token = request['access_token']
        self.headers = {'Authorization': 'bearer {0}'.format(token)}

    def autocomplete(self, text, latitude=None, longitude=None, locale=None):
        """
        This endpoint returns autocomplete suggestions for search keywords,
        businesses and categories, based on the input text.

        Parameters:

        - text (str):
            Required. Text to return autocomplete suggestions for.

        - latitude (float):
            Required if want to get autocomplete suggestions for businesses.
            Latitude of the location to look for business autocomplete
            suggestions.

        - longitude (float):
            Required if want to get autocomplete suggestions for businesses.
            Longitude of the location to look for business autocomplete
            suggestions.

        - locale (str):
            Optional. Specify the locale to return the business information in.
            See the list of supported locales:
            https://www.yelp.com/developers/documentation/v3/supported_locales

        """

        params = {'text': text}
        if longitude is not None and latitude is not None:
            params['latitude'] = latitude
            params['longitude'] = longitude
        if locale is not None:
            params['locale'] = locale
        url = 'https://api.yelp.com/v3/autocomplete'
        request = url_query(url, params, headers=self.headers)
        return request

    def business_details(self, businessid):
        """
        This endpoint returns the detail information of a business.

        Note: at this time, the API does not return businesses without any
        reviews.

        Parameters:

        - businessid (str):
            Yelp business ID to retrieve details for, as returned by the "id"
            key of the search, phone_search, and transactions methods.

        Returns:

        - request (dict):
            The query results, converted from JSON to a Python dict. See
            https://www.yelp.com/developers/documentation/v3/business

        """

        url = 'https://api.yelp.com/v3/businesses/{0}'.format(businessid)
        request = url_query(url, headers=self.headers)
        return request

    def business_reviews(self, businessid, locale=None):
        """
        This endpoint returns the up to three reviews of a business.

        Note: at this time, the API does not return businesses without any
        reviews.

        Parameters:

        - businessid (str):
            Yelp business ID to retrieve details for, as returned by the "id"
            key of the search, phone_search, and transactions methods.

        - locale (str):
            Optional. Specify the locale to return the business information in.
            See the list of supported locales:
            https://www.yelp.com/developers/documentation/v3/supported_locales

        Returns:

        - request (dict):
            The query results, converted from JSON to a Python dict. See
            https://www.yelp.com/developers/documentation/v3/business

        """

        url = 'https://api.yelp.com/v3/businesses/{0}/reviews'.format(businessid)
        if locale is not None:
            params = {'locale': locale}
            request = url_query(url, params, headers=self.headers)
        else:
            request = url_query(url, headers=self.headers)
        return request

    def search(self, term=None, location=None, latitude=None, longitude=None,
               radius=None, categories=None, locale=None, limit=20,
               offset=None, sort_by='best_match', price=None, open_now=False,
               open_at=None, attributes=None):
        """
        This endpoint returns up to 1000 businesses based on the provided
        search criteria. It has some basic information about the business.

        Parameters:

        - term (str):
            Optional. Search term (e.g. "food", "restaurants"). If term isn’t
            included we search everything. The term keyword also accepts
            business names such as "Starbucks".

        - location (str):
            Required if either latitude or longitude is not provided. Specifies
            the combination of "address, neighborhood, city, state or zip,
            optional country" to be used when searching for businesses.

        - latitude (float):
            Required if location is not provided. Latitude of the location you
            want to search near by.

        - longitude (float):
            Required if location is not provided. Longitude of the location you
            want to search near by.

        - radius (int):
            Optional. Search radius in meters. If the value is too large, a
            AREA_TOO_LARGE error may be returned. The max value is 40000 meters
            (25 miles).

        - categories (str/list/tuple):
            Optional. Categories to filter the search results with. See the
            list of supported categories:
            https://www.yelp.com/developers/documentation/v3/all_category_list
            The category filter can be a list of comma delimited categories.
            For example, "bars,french" will filter by Bars and French. The
            category identifier should be used (for example "discgolf", not
            "Disc Golf").

        - locale (str):
            Optional. Specify the locale to return the business information in.
            See the list of supported locales:
            https://www.yelp.com/developers/documentation/v3/supported_locales

        - offset (int):
            Optional. Offset the list of returned business results by this
            amount.

        - sort_by (str):
            Optional. Sort the results by one of the these modes: best_match,
            rating, review_count or distance. By default it's best_match. The
            rating sort is not strictly sorted by the rating value, but by an
            adjusted rating value that takes into account the number of
            ratings, similar to a bayesian average. This is so a business with
            1 rating of 5 stars doesn’t immediately jump to the top.

        - price (int/list/tuple):
            Optional. Pricing levels to filter the search result with: 1 = $,
            2 = $$, 3 = $$$, 4 = $$$$. The price filter can be a list of comma
            delimited pricing levels. For example, "1, 2, 3" will filter the
            results to show the ones that are $, $$, or $$$.

        - open_now (bool):
            Optional. Default to false. When set to true, only return the
            businesses open now. Notice that open_at and open_now cannot be
            used together.

        - open_at (int):
            Optional. An integer represending the Unix time in the same
            timezone of the search location. If specified, it will return
            business open at the given time. Notice that open_at and open_now
            cannot be used together.

        - attributes (str/list/tuple):
            Optional. Additional filters to restrict search results. Possible
            values are: hot_and_new - Hot and New businesses; request_a_quote -
            Businesses that have the Request a Quote feature;
            waitlist_reservation - Businesses that have an online waitlist;
            cashback - Businesses that offer Cash Back; deals - Businesses that
            offer Deals. You can combine multiple attributes by providing a
            comma separated like "attribute1,attribute2". If multiple
            attributes are used, only businesses that satisfy ALL attributes
            will be returned in search results. For example, the attributes
            "hot_and_new,cashback" will return businesses that are Hot and New
            AND offer Cash Back.

        Returns:

        - request (dict):
            The query results, converted from JSON to a Python dict. See
            https://www.yelp.com/developers/documentation/v3/business_search

        """

        # Parse input parameters ready for GET request.
        if limit > 50:
            maxlimit = limit
            limit = 50
        else:
            maxlimit = None
        params = {'term': term,
                  'limit': limit,
                  'sort_by': sort_by}
        if location is not None:
            params['location'] = location
        else:
            params['latitude'] = latitude
            params['longitude'] = longitude
        if radius is not None:
            params['radius'] = radius
        if categories is not None:
            if type(categories) != str:
                categories = ','.join(categories)
            params['categories'] = categories
        if locale is not None:
            params['locale'] = locale
        if offset is not None:
            params['offset'] = offset
        if price is not None:
            if type(price) not in (str, int):
                price = ','.join(price)
            params['price'] = price
        if open_now:
            params['open_now'] = 'true'
        elif open_at is not None:
            params['open_at'] = open_at
        if attributes is not None:
            if type(attributes) != str:
                attributes = ','.join(attributes)
            params['attributes'] = attributes

        # Query Yelp url with parameters and access token provided.
        url = 'https://api.yelp.com/v3/businesses/search'
        request = url_query(url, params, self.headers)

        # If more than >50 results have been requested, repeat query until
        # the desired limit is reached or all possible records have been
        # retrieved, extending the original results set.
        if maxlimit is not None:
            total = request['total']
            if offset is None:
                offset = 50
            while offset < maxlimit and offset < total:
                params['offset'] = offset
                results = url_query(url, params, self.headers)
                if results is not None:
                    businesses = results['businesses']
                    if len(businesses) + offset > maxlimit:
                        businesses = businesses[:maxlimit - offset]
                    request['businesses'].extend(businesses)
                offset += 50
        return request

    def phone_search(self, phone):
        """
        This endpoint returns a list of businesses based on the provided phone
        number. It is possible for more than one businesses having the same
        phone number (for example, chain stores with the same +1 800 phone
        number).

        Note: at this time, the API does not return businesses without any
        reviews.

        Parameters:

        - phone (str):
            Required. Phone number of the business you want to search for. It
            must start with + and include the country code, like +14159083801.

        Returns:

        - request (dict):
            The query results, converted from JSON to a Python dict. See
            https://www.yelp.com/developers/documentation/v3/
            business_search_phone

        """

        url = 'https://api.yelp.com/v3/businesses/search/phone'
        params = {'phone': phone}
        request = url_query(url, params, headers=self.headers)
        return request

    def transaction_search(self, transaction_type='delivery',
                           latitude=None, longitude=None, location=None):
        """
        This endpoint returns a list of businesses which support certain
        transactions. Currently, this endpoint only supports food delivery in
        the US.

        Note: at this time, the API does not return businesses without any
        reviews.

        Parameters:

        - latitude (float):
            Required when location isn't provided. Latitude of the location you
            want to deliver to.

        - longitude (float):
            Required when location isn't provided. Longitude of the location
            you want to deliver to.

        - location (str): Required when latitude and longitude aren't provided.
          Address of the location you want to deliver to.

        Returns:

        - request (dict):
            The query results, converted from JSON to a Python dict. See
            https://www.yelp.com/developers/documentation/v3/
            business_search_phone

        """

        params = {}
        if location is not None:
            params['location'] = location
        else:
            params['latitude'] = latitude
            params['longitude'] = longitude
        url = 'https://api.yelp.com/v3/transactions/{0}/search'.format(transaction_type)
        request = url_query(url, params, headers=self.headers)
        return request
