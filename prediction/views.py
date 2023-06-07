from django.shortcuts import render
from listings.models import Listing
from sklearn.ensemble import RandomForestRegressor
from django.conf import settings
import pickle
import os


def predict_price(request):
    if request.method == 'POST':
        # get the input values from the form
        bathrooms = int(request.POST.get('bathrooms'))
        marla = float(request.POST.get('marla'))
        bedrooms = int(request.POST.get('bedrooms'))
        nearMasjid = int(request.POST.get('nearMasjid'))
        nearMarket = int(request.POST.get('nearMarket'))

        # load the model from the pickle file
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(BASE_DIR, 'model_pickle'), 'rb') as f:
            model = pickle.load(f)

        # make the prediction using the loaded model
        prediction = model.predict([[bathrooms, marla, bedrooms, nearMasjid, nearMarket]])
        
        # round the predicted price to 2 decimal places
        predicted_price = round(prediction[0], 2)
        
        return render(request, 'prediction/predict_price.html', {'predicted_price': predicted_price})
    else:
        return render(request, 'prediction/predict_price.html')


def price_map(request):
    return render(request, 'prediction/price_colormap.html')


def report(request):
    return render(request, 'prediction/report.html')
