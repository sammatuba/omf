#Easy Solar
"""

Runs easySolar prediction of DHi from GHI

Params:
{Year, USCRN Location}



"""
#Imports
import os
import pandas as pd
import numpy as np
import requests
import datetime
from joblib import dump, load

from sklearn.preprocessing import PolynomialFeatures


from weather import pullUscrn


#Establish directories
_currDir = os.getcwd()
print(_currDir)

#Import model
clf_log_poly = load('Log_Polynomial_clf.joblib')

#darksky key
_key = '31dac4830187f562147a946529516a8d'
_key2 = os.environ.get('DARKSKY','')

def _getUscrnData(year, location='TX_Austin_33_NW', dataType="SOLARAD"):
	ghiData = pullUscrn(year, location, dataType)
	return ghiData

#Standard positional arguments are for TX_Austin
def _getDarkSkyCloudCoverForYear(year, lat=30.581736, lon=-98.024098, key=_key, units='si'):
	cloudCoverByHour = {}
	coords = '%0.2f,%0.2f' % (lat, lon)
	times = list(pd.date_range('{}-01-01'.format(year), '{}-12-31'.format(year), freq='D'))
	while times:
		time = times.pop(0)
		print(time)
		url = 'https://api.darksky.net/forecast/%s/%s,%s?exclude=daily,alerts,minutely,currently&units=%s' % (key, coords, time.isoformat(), units ) 
		res = requests.get(url).json()
		try:
			dayData = res['hourly']['data']
		except KeyError:
			print("No day data!!!!!!")
			continue
		for hour in dayData:
			try:
				cloudCoverByHour[hour['time']] = hour['cloudCover']
			except KeyError:
				print("No Cloud Cover Data")
				pass
	return cloudCoverByHour

def _makeDataNonzero(data):
	ghiData=list(filter(lambda num: num!=0.0, data))
	assert(all(x[0]!=0 for x in ghiData))
	return ghiData

def _logifyData(data):
	data = np.log(data)
	return data

def _initPolyModel(X, degrees=5):
    poly = PolynomialFeatures(degree=degrees)
    _X_poly = poly.fit_transform(X)
    return _X_poly

def preparePredictionVectors(year='2018'):
	cloudCoverData = _getDarkSkyCloudCoverForYear(year)
	ghiData = _getUscrnData(year)
	#for each 8760 hourly time slots, make a timestamp for each slot, look up cloud cover by that slot
	#then append cloud cover and GHI reading together
	start_time = datetime.datetime(int(year),1,1,0)
	training_array = []
	for i in range(len(ghiData)): #Because ghiData is leneth 8760, one for each hour of a year
		time = start_time + datetime.timedelta(minutes=60*i)
		tstamp = int(datetime.datetime.timestamp(time))
		try:
			cloudCover = cloudCoverData[tstamp]
		except KeyError:
			cloudCover = 0
		ghi = ghiData[i]
		if ghi == 0:
			continue
		else:
			ghi = np.log(ghi)
		training_array.append((ghi, cloudCover))

	return training_array


def predictPolynomial(X, model, degrees=5):
	X = _initPolyModel(X, degrees=5)
	predictions = model.predict(X)
	return predictions

# d = _getUscrnData(year='2020')
# print([x for x in d])
training_X = preparePredictionVectors(year='2020')
# print(training_X)

log_prediction = predictPolynomial(training_X, clf_log_poly)
prediction = np.exp(log_prediction)
print(prediction)
