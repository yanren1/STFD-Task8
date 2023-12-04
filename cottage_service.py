from flask import Flask, request, jsonify,Response
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from sswap_utils import read_rig,fill_rrg
from readont import cottage_offer,update_ont
from alignment import greedy_mapping

cottage_service = Flask(__name__)

@cottage_service.route('/cottageServices/getAvailableCottage', methods=['GET'])
def searchCottage_rdg():
    # file_path = 'checkavailable.rdf'
    file_path = 'xml_rdg'
    try:
        g = Graph()
        g.parse(file_path, format='n3')
        rdg = g.serialize(format='n3')
        response = Response(rdg)
    except:
        g = Graph()
        g.parse(file_path, format='xml')
        rdg = g.serialize(format='n3')
        response = Response(rdg)

    return response

@cottage_service.route('/cottageServices/getAvailableCottage', methods=['POST'])
def searchCottage():
    rig = request.get_data(as_text=True)

    user_input = read_rig(rig)
    # print(user_input)

    offer_keys = ['bookerName','numPlace','numBedrooms','maxLakeDistance','nearestCity',
                  'maxCityDistance','numDays','startDate','maxDateShift']
    user_input_keys = list(user_input.keys())
    key_map = greedy_mapping(offer_keys, user_input_keys, use_model=1)
    u_input = {k:user_input[v[0]] for k,v in key_map.items()}
    # print(u_input)

    offer = cottage_offer(u_input)
    print('searchCottage offer')
    print(offer)

    rrg = fill_rrg(rig,offer)

    response = Response(rrg)
    return response

@cottage_service.route('/cottageServices/bookCottage', methods=['GET'])
def bookCottage_rdg():
    file_path = 'bookcottage.rdf'
    g = Graph()
    g.parse(file_path, format='n3')
    rdg = g.serialize(format='n3')
    response = Response(rdg)
    return response

@cottage_service.route('/cottageServices/bookCottage', methods=['POST'])
def bookCottage():
    rig = request.get_data(as_text=True)
    choosen_offer = read_rig(rig)

    update_ont(choosen_offer)
    status = {'bookingStatus':'1'}
    rrg = fill_rrg(rig,status)
    response = Response(rrg)
    return response



if __name__ == '__main__':
    cottage_service.run(port=5001)
    # my_rdg()