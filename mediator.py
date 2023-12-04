from flask import Flask, request, render_template, redirect, url_for,send_from_directory
from sswap_utils import fill_rig,read_rrg
import requests
import ast
from alignment import greedy_mapping

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def form_client():
    book_info = {}

    if request.method == 'POST':
        book_info['bookerName'] = str(request.form['bookerName'])
        book_info['numPeople'] = str(request.form['numPeople'])
        book_info['numBedrooms'] = str(request.form['numBedrooms'])
        book_info['maxLakeDistance'] = str(request.form['maxLakeDistance'])
        book_info['nearestCity'] = str(request.form['nearestCity'])
        book_info['maxCityDistance'] = str(request.form['maxCityDistance'])
        book_info['numDays'] = int(request.form['numDays'])
        book_info['startDate'] = str(request.form['startDate'])
        book_info['maxDateShift'] = int(request.form['maxDateShift'])


        target_url = "http://127.0.0.1:5001/cottageServices/getAvailableCottage"
        rdg = requests.get(target_url).text
        rig = fill_rig(book_info,rdg)

        rrg = requests.post(target_url, data=rig, headers={"Content-Type": "text/turtle"}).text
        offer_dict = {'offer':read_rrg(rrg)}

        return redirect(url_for('offers', **offer_dict))


    return render_template('index.html')


@app.route('/offers')
def offers():
    str_offer = request.args.get('offer', 'default_value')
    rrg_offers = ast.literal_eval(str_offer)

    html_keys = ['cottageName','bookerName','bookingNum','address','image','numPlaces',
                 'numBedrooms','lakeDistance','nearestCity','startDate','endDate']
    rrg_offers_keys = list(rrg_offers.keys())
    key_mapping = greedy_mapping(html_keys, rrg_offers_keys)

    offer = {k:rrg_offers[v[0]] for k,v in key_mapping.items()}


    return render_template('offers.html', data=offer)


@app.route('/choose_reservation', methods=['POST'])
def choose_reservation():
    choose_button = request.form['choose_button']
    i, data = choose_button.split('|')
    offer = ast.literal_eval(data)
    choosen_offer = {k:offer[k][int(i)] for k in offer.keys()}


    target_url = "http://127.0.0.1:5001/cottageServices/bookCottage"
    rdg = requests.get(target_url).text

    rig = fill_rig(choosen_offer, rdg)
    rrg = requests.post(target_url, data=rig, headers={"Content-Type": "text/turtle"}).text

    status = read_rrg(rrg)
    status_key = ['bookingStatus']
    rrg_offers_keys = list(status.keys())
    key_mapping = greedy_mapping(status_key, rrg_offers_keys)

    print(status)
    status = status[key_mapping['bookingStatus'][0]][0]
    print(status)


    if status==1:
        # update_ont(choosen_offer)
        return render_template('result.html', data=offer, i = int(i))
    else:
        return render_template('result.html', data=offer, i=int(i))


if __name__ == '__main__':
    app.run(port=5000)