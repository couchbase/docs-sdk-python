# REFERENCE FILE ONLY.
# This file is a copy of 'travel.py' in the 'try-cb-python' repo. It's not
# intended to run. Please make any improvements or changes to the original
# codebase and replicate the changes here afterwards. Docstrings have been
# truncated or shortened for brevity.

import argparse
import math
import uuid
import jwt  # from PyJWT
from datetime import datetime
from random import random
from flasgger import Swagger, SwaggerView
from flask import Flask, jsonify, make_response, request
from flask.blueprints import Blueprint
from flask_classy import FlaskView
from flask_cors import CORS, cross_origin

# Couchbase Imports
import couchbase.search as FT
import couchbase.subdocument as SD
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions, SearchOptions
from couchbase.auth import PasswordAuthenticator
from couchbase.exceptions import *

JWT_SECRET = 'cbtravelsample'

# tag::args[]
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cluster', help='Connection String i.e. localhost', default='db')
parser.add_argument('-s', '--scheme', help='couchbase or couchbases', default='couchbase')
parser.add_argument('-a', '--connectargs', help="?any_additional_args", default="")
parser.add_argument('-u', '--user', help='User with access to bucket')
parser.add_argument('-p', '--password', help='Password of user with access to bucket')

args = parser.parse_args()

if not args.cluster:
  raise ConnectionError("No value for CB_HOST set!")

if ("couchbases://" in args.cluster) or ("couchbase://" in args.cluster):
    CONNSTR = f"{args.cluster}{args.connectargs}"
else:
    CONNSTR = f"{args.scheme}://{args.cluster}{args.connectargs}"
        
authenticator = PasswordAuthenticator(args.user, args.password)
print("Connecting to: " + CONNSTR)

# ...
# API endpoints
# ...

# end::args[]

# tag::api[]
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SWAGGER'] = {
    'openapi': '3.0.3',
    'title': 'Travel Sample API',
    'version': '1.0',
    'description': 'A sample API for getting started with Couchbase Server and the SDK.',
    'termsOfService': ''
}

swagger_template = {
    "components": {
        "securitySchemes": {
            "bearer": {
            ...
            }
        },
        "schemas": {
        ...
        }
    }
}

api = Blueprint("api", __name__)

CORS(app, headers=['Content-Type', 'Authorization'])
# end::api[]

# tag::route[]
@app.route('/')
def index():
    ...
# end::route[]
    """Returns the index page
    ...
    """

    return """
    <h1> Python Travel Sample API </h1>
    A sample API for getting started with Couchbase Server and the Python SDK.
    <ul>
    <li> <a href = "/apidocs"> Learn the API with Swagger, interactively </a>
    <li> <a href = "https://github.com/couchbaselabs/try-cb-python"> GitHub </a>
    </ul>
    """


def lowercase(key):
    return key.lower()

# tag::airport-class-def[]
class AirportView(SwaggerView):
    """Airport class for airport objects in the database"""
# end::airport-class-def[]
# tag::airports-endpoint[]
    @api.route('/airports', methods=['GET', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def airports():
        """Returns list of matching airports and the source query
        ...
        """

        queryType = "SQL++ query - scoped to inventory: "
        partialAirportName = request.args['search']

        queryPrep = "SELECT airportname FROM `travel-sample`.inventory.airport WHERE "
        sameCase = partialAirportName == partialAirportName.lower() or partialAirportName == partialAirportName.upper() #bool

        if sameCase and len(partialAirportName) == 3:
            queryPrep += "faa=$1"
            queryArgs = [partialAirportName.upper()]
        elif sameCase and len(partialAirportName) == 4:
            queryPrep += "icao=$1"
            queryArgs = [partialAirportName.upper()]
        else:
            queryPrep += "POSITION(LOWER(airportname), $1) = 0"
            queryArgs = [partialAirportName.lower()]

        results = cluster.query(queryPrep, *queryArgs)
        airports = [x for x in results]

        context = [queryType + queryPrep]

        response = make_response(jsonify({"data": airports, "context": context}))
        return response
# end::airports-endpoint[]
# tag::flights-class[]
class FlightPathsView(SwaggerView):
    """ FlightPath class for computed flights between two airports FAA codes"""

    @api.route('/flightPaths/<fromLoc>/<toLoc>', methods=['GET', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def flightPaths(fromLoc, toLoc):
        """
        Return flights information, cost and more for a given flight time and date
        ...
        """
# end::flights-class[]
# tag::flights-first-query[]
        queryType = "SQL++ query - scoped to inventory: "
        context = []

        faaQueryPrep = "SELECT faa as fromAirport FROM `travel-sample`.inventory.airport \
                        WHERE airportname = $1 \
                        UNION SELECT faa as toAirport FROM `travel-sample`.inventory.airport \
                        WHERE airportname = $2"
        
        faaResults = cluster.query(faaQueryPrep, fromLoc, toLoc)

        flightPathDict = {}
        for result in faaResults:
            flightPathDict.update(result)

        queryFrom = flightPathDict['fromAirport']
        queryTo = flightPathDict['toAirport']

        context.append(queryType + faaQueryPrep)

# end::flights-first-query[]
# tag::flights-second-query[]
        routeQueryPrep = "SELECT a.name, s.flight, s.utc, r.sourceairport, r.destinationairport, r.equipment \
                        FROM `travel-sample`.inventory.route AS r \
                        UNNEST r.schedule AS s \
                        JOIN `travel-sample`.inventory.airline AS a ON KEYS r.airlineid \
                        WHERE r.sourceairport = $fromfaa AND r.destinationairport = $tofaa AND s.day = $dayofweek \
                        ORDER BY a.name ASC;"

        flightDay = convdate(request.args['leave'])
        routeResults = cluster.query(routeQueryPrep, 
                                     fromfaa=queryFrom, 
                                     tofaa=queryTo, 
                                     dayofweek=flightDay)

        routesList = []
        for route in routeResults:
            route['price'] = math.ceil(random() * 500) + 250
            routesList.append(route)

        context.append(queryType + routeQueryPrep)

        response = make_response(jsonify({"data": routesList, "context": context}))
        return response

# end::flights-second-query[]

# tag::user-class-def[]
class TenantUserView(SwaggerView):
    """Class for storing user related information for a given tenant"""
# end::user-class-def[]
# tag::login-def[]
    @api.route('/tenants/<tenant>/user/login', methods=['POST', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def login(tenant):
        """Login an existing user for a given tenant agent
        ...
        """
# end::login-def[]
# tag::login-code[]
        requestBody = request.get_json()
        user = requestBody['user']
        providedPassword = requestBody['password']

        userDocumentKey = lowercase(user)

        agent = lowercase(tenant)
        scope = bucket.scope(agent)
        users = scope.collection('users')

        queryType = f"KV get - scoped to {scope.name}.users: for password field in document "

        try:
            documentPassword = users.lookup_in(userDocumentKey, (
                SD.get('password'),
            )).content_as[str](0)

            if documentPassword != providedPassword:
                return abortmsg(401, "Password does not match")

        except DocumentNotFoundException:
            print(f"User {user} item does not exist", flush=True)
        except AmbiguousTimeoutException or UnAmbiguousTimeoutException:
            print("Request timed out - has Couchbase stopped running?", flush=True)
        else:
            return jsonify({'data': {'token': genToken(user)}, 'context': [queryType + user]})

        return abortmsg(401, "Failed to get user data")
# end::login-code[]
# tag::signup-def[]
    @api.route('/tenants/<tenant>/user/signup', methods=['POST', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def signup(tenant):
        """Signup a new user
        ...
        """
# end::signup-def[]
# tag::signup-code[]
        requestBody = request.get_json()
        user = requestBody['user']
        password = requestBody['password']

        userDocumentKey = lowercase(user)

        agent = lowercase(tenant)
        scope = bucket.scope(agent)
        users = scope.collection('users')

        queryType = f"KV insert - scoped to {scope.name}.users: document "

        try:
            users.insert(userDocumentKey, {'username': user, 'password': password})
            responseJSON = jsonify(
                {'data': {'token': genToken(user)}, 'context': [queryType + user]})
            response = make_response(responseJSON)
            return response, 201

        except DocumentExistsException:
            print(f"User {user} item already exists", flush=True)
            return abortmsg(409, "User already exists")
        except Exception as e:
            print(e)
            return abortmsg(500, "Failed to save user", flush=True)
# end::signup-code[]
# tag::view-flight-get-keys[]
    @api.route('/tenants/<tenant>/user/<username>/flights', methods=['GET', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def getflights(tenant, username):
        """List the flights that have been reserved by a user
        ...
        """
        agent = lowercase(tenant)

        scope = bucket.scope(agent)
        users = scope.collection('users')
        flights = scope.collection('bookings')

        # HTTP token authentication
        bearer = request.headers['Authorization']
        if not auth(bearer, username):
            return abortmsg(401, 'Username does not match token username: ' + username)
        
        try:
            userDocumentKey = lowercase(username)

            lookupResult = users.lookup_in(
              userDocumentKey,
              [
                SD.get('bookings'),
                SD.exists('bookings')
              ])
            
            bookedFlightKeys = []
            if lookupResult.exists(1):
                bookedFlightKeys = lookupResult.content_as[list](0)
# end::view-flight-get-keys[]
# tag::view-flight-get-details[]
            rows = []
            for key in bookedFlightKeys:
                rows.append(flights.get(key).content_as[dict])

            queryType = f"KV get - scoped to {scope.name}.users: for {len(bookedFlightKeys)} bookings in document "
            response = make_response(jsonify({"data": rows, "context": [queryType + userDocumentKey]}))
            return response
        
        except DocumentNotFoundException:
            return abortmsg(401, "User does not exist")
# end::view-flight-get-details[]

# tag::booking-doc[]
    @api.route('/tenants/<tenant>/user/<username>/flights', methods=['PUT', 'OPTIONS'])
    @cross_origin(supports_credentials=True)
    def updateflights(tenant, username):
        """Book a new flight for a user
        ...
        """
        agent = lowercase(tenant)
        user = lowercase(username)

        scope = bucket.scope(agent)
        users = scope.collection('users')
        bookings = scope.collection('bookings')

        queryType = f"KV update - scoped to {scope.name}.users: for bookings field in document "

        # HTTP token authentication
        bearer = request.headers['Authorization']
        if not auth(bearer, username):
            return abortmsg(401, 'Username does not match token username: ' + username)

        try:
            flightData = request.get_json()['flights'][0]
            flightID = str(uuid.uuid4())
            bookings.upsert(flightID, flightData)

        except Exception as e:
            print(e, flush=True)
            return abortmsg(500, "Failed to add flight data")
# end::booking-doc[]
# tag::update-user[]
        try:
            users.mutate_in(user, (SD.array_append('bookings', flightID, create_parents=True),))
            resultJSON = {'data': {'added': [flightData]},
                          'context': [queryType + user]}
            return make_response(jsonify(resultJSON))
        
        except DocumentNotFoundException:
            return abortmsg(401, "User does not exist")
        except Exception:
            return abortmsg(500, "Couldn't update flights")
# end::update-user[]

class HotelView(SwaggerView):
    """Class for storing Hotel search related information"""
# tag::search-query[]
    @api.route('/hotels/<description>/<location>/', methods=['GET'])
    @cross_origin(supports_credentials=True)
    def hotels(description, location):
        # Requires FTS index called 'hotels-index'
        """Find hotels using full text search
        ...
        """
        queryPrep = FT.ConjunctionQuery()
        if location != '*' and location != "":
            queryPrep.conjuncts.append(
                FT.DisjunctionQuery(
                    FT.MatchPhraseQuery(location, field='country'),
                    FT.MatchPhraseQuery(location, field='city'),
                    FT.MatchPhraseQuery(location, field='state'),
                    FT.MatchPhraseQuery(location, field='address')
                ))

        if description != '*' and description != "":
            queryPrep.conjuncts.append(
                FT.DisjunctionQuery(
                    FT.MatchPhraseQuery(description, field='description'),
                    FT.MatchPhraseQuery(description, field='name')
                ))

        # Attempting to run a compound query with no sub-queries will result in
        # a 'NoChildrenException'.

        if len(queryPrep.conjuncts) == 0:
            queryType = "FTS search rejected - no search terms were provided"
            response = {'data': [], 'context': [queryType]}
            return jsonify(response)

        searchRows = cluster.search_query('hotels-index', 
                                          queryPrep, 
                                          SearchOptions(limit=100))
# end::search-query[]
# tag::search-subdoc[]
        allResults = []
        addressFields = ['address', 'city', 'state', 'country']
        dataFields = ['name', 'description']

        scope = bucket.scope('inventory')
        hotel_collection = scope.collection('hotel')

        for hotel in searchRows:

            hotelFields = hotel_collection.lookup_in(
                hotel.id, [SD.get(x) for x in [*addressFields, *dataFields]])

            hotelAddress = []
            for x in range(len(addressFields)):
                try:
                    hotelAddress.append(hotelFields.content_as[str](x))
                except:
                    pass
            hotelAddress = ', '.join(hotelAddress)

            hotelData = {}
            for x, field in enumerate(dataFields):
                try:    
                    hotelData[field] = hotelFields.content_as[str](x+len(addressFields))
                except:
                    pass
                
            hotelData['address'] = hotelAddress
            allResults.append(hotelData)

        queryType = f"FTS search - scoped to: {scope.name}.hotel within fields {','.join([*addressFields, *dataFields])}"
        response = {'data': allResults, 'context': [queryType]}
        return jsonify(response)
# end::search-subdoc[]


def abortmsg(code, message):
    response = jsonify({'message': message})
    response.status_code = code
    return response


def convdate(rawdate):
    """Returns integer data from mm/dd/YYYY"""
    day = datetime.strptime(rawdate, '%m/%d/%Y')
    return day.weekday()


def genToken(username):
    return jwt.encode({'user': username}, JWT_SECRET, algorithm='HS256').decode("ascii")


def auth(bearerHeader, username):
    bearer = bearerHeader.split(" ")[1]
    return username == jwt.decode(bearer, JWT_SECRET)['user']

# tag::connect[]
def connect_db():
    print(CONNSTR, authenticator)
    cluster = Cluster(CONNSTR, ClusterOptions(authenticator))
    bucket = cluster.bucket('travel-sample')
    return cluster, bucket

# end::connect[]
# tag::start-app[]
if __name__ == "__main__":
    cluster, bucket = connect_db()
    app.register_blueprint(api, url_prefix="/api")
    swagger = Swagger(app, template=swagger_template)
    app.run(debug=True, host='0.0.0.0', port=8080, threaded=False)
# end::start-app[]