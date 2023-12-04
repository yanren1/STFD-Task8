import rdflib
from rdflib import Namespace, URIRef, Literal
from rdflib.namespace import RDF
from datetime import datetime, timedelta



def check_date(user_input,start_date,available_days):

    user_start_date = user_input['startDate'].split('-')
    user_start_date = datetime(int(user_start_date[0]), int(user_start_date[1]), int(user_start_date[2]),)
    user_num_days = timedelta(days=int(user_input['numDays']))
    user_shift_days = timedelta(days=int(user_input['maxDateShift']))
    #
    user_min_start_date = user_start_date - user_shift_days
    user_max_start_date = user_start_date + user_shift_days
    user_max_end_date = user_max_start_date + user_num_days

    #
    co_start_date = str(start_date).split('-')
    co_start_date = datetime(int(co_start_date[0]), int(co_start_date[1]), int(co_start_date[2]),)
    co_num_days = timedelta(days=int(available_days))
    #
    co_avail_end_date = co_start_date + co_num_days

    end_date_diff = co_avail_end_date - user_max_end_date
    start_date_diff = user_min_start_date - co_start_date

    return end_date_diff.days >=0 and start_date_diff.days >=0



def cottage_offer(user_input):
    #
    g = rdflib.Graph()
    g.parse("ontology.rdf", format="turtle")

    query = f"""
    PREFIX ex: <http://example.org#>
    SELECT ?cottage ?address ?image ?num_places ?num_bedrooms ?lake_distance ?nearest_city ?start_date ?available_days ?unavailablePeriod
    WHERE {{
        ?cottage a ex:Cottage ;
                 ex:address ?address ;
                 ex:places ?num_places ;
                 ex:bedrooms ?num_bedrooms ;
                 ex:distanceToLake ?lake_distance ;
                 ex:nearestCity ?nearest_city ;
                 ex:availableDays ?available_days ;
                 ex:unavailablePeriod ?unavailablePeriod;
                 ex:startDate ?start_date ;
                 ex:imageURL ?image.
        
        FILTER (?num_places >= {user_input['numPlace']} &&
                ?num_bedrooms >= {user_input['numBedrooms']} &&
                ?lake_distance <= {user_input['maxLakeDistance']} &&
                ?nearest_city = "{user_input['nearestCity']}" &&
                ?available_days >= {user_input['numDays']} ).
    }}
    """
    results = g.query(query, initNs={"": Namespace("http://example.org/cottage#")})

    offer = {'cottageName':[],
             'bookerName':[],
             'bookingNum': [],
             'address': [],
             'imageURL': [],
             'numPlaces': [],
             'numBedrooms': [],
             'lakeDistance': [],
             'nearestCity': [],
             'startDate': [],
             'endDate': [],}

    for result in results:

        cottage, address, image, num_places, num_bedrooms, lake_distance, nearest_city, start_date, available_days, unavailablePeriod= result
        if str(unavailablePeriod) == '1':
            continue

        if check_date(user_input,start_date,available_days):
            tmp_start_date = str(user_input['startDate']).split('-')
            end_date = datetime(int(tmp_start_date[0]), int(tmp_start_date[1]), int(tmp_start_date[2]),) + timedelta(days=int(user_input['numDays']))
            end_date = f'{str(end_date.year)}-{str(end_date.month)}-{str(end_date.day)}'
            offer['cottageName'].append(cottage.split("#")[-1])
            offer['bookerName'].append(user_input['bookerName'])
            offer['address'].append(str(address))
            offer['imageURL'].append(str(image))
            offer['numPlaces'].append(str(num_places))
            offer['numBedrooms'].append(str(num_bedrooms))
            offer['lakeDistance'].append(str(lake_distance))
            offer['nearestCity'].append(str(nearest_city))
            offer['startDate'].append(str(user_input['startDate']))
            offer['endDate'].append(str(end_date))
            booking_num = f'{str(cottage).split("#")[-1]}-{str(user_input["startDate"])}-{str(end_date)}'
            offer['bookingNum'].append(str(booking_num))

    return offer

def update_ont(resevation):

    g = rdflib.Graph()
    ontology_file = 'ontology.rdf'
    g.parse(ontology_file, format="turtle")
    ex = Namespace('http://example.org#')

    cottage_uri = URIRef(f'http://example.org#{resevation["cottageName"]}')


    g.set((cottage_uri, ex.unavailablePeriod, Literal('1')))
    g.serialize(ontology_file, format='turtle')

