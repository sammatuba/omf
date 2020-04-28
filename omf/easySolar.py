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
import math
import requests
import datetime
import pysolar
import pytz
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


#Station_Dict

# Station_Dict = {

# "AK_Cordova_14_ESE"
# "AK_Deadhorse_3_S"
# "AK_Denali_27_N"
# "AK_Fairbanks_11_NE"
# "AK_Glennallen_64_N"
# "AK_Gustavus_2_NE"
# "AK_Ivotuk_1_NNE"
# "AK_Kenai_29_ENE"
# "AK_King_Salmon_42_SE"
# "AK_Metlakatla_6_S"
# "AK_Port_Alsworth_1_SW"
# "AK_Red_Dog_Mine_3_SSW"
# "AK_Ruby_44_ESE"
# "AK_Sand_Point_1_ENE"
# "AK_Selawik_28_E"
# "AK_Sitka_1_NE"
# "AK_St._Paul_4_NE"
# "AK_Tok_70_SE"
# "AK_Toolik_Lake_5_ENE"
# "AK_Yakutat_3_SSE"
# "AL_Brewton_3_NNE"
# "AL_Clanton_2_NE"
# "AL_Courtland_2_WSW"
# "AL_Cullman_3_ENE"
# "AL_Fairhope_3_NE"
# "AL_Gadsden_19_N"
# "AL_Gainesville_2_NE"
# "AL_Greensboro_2_WNW"
# "AL_Highland_Home_2_S"
# "AL_Muscle_Shoals_2_N"
# "AL_Northport_2_S"
# "AL_Russellville_4_SSE"
# "AL_Scottsboro_2_NE"
# "AL_Selma_6_SSE"
# "AL_Selma_13_WNW"
# "AL_Talladega_10_NNE"
# "AL_Thomasville_2_S"
# "AL_Troy_2_W"
# "AL_Valley_Head_1_SSW"
# "AR_Batesville_8_WNW"
# "AZ_Elgin_5_S"
# "AZ_Tucson_11_W"
# "AZ_Williams_35_NNW"
# "AZ_Yuma_27_ENE"
# "CA_Bodega_6_WSW"
# "CA_Fallbrook_5_NE"
# "CA_Merced_23_WSW"
# "CA_Redding_12_WNW"
# "CA_Santa_Barbara_11_W"
# "CA_Stovepipe_Wells_1_SW"
# "CA_Yosemite_Village_12_W"
# "CO_Boulder_14_W">CO_Bould
# "CO_Cortez_8_SE">CO_Cortez
# "CO_Dinosaur_2_E">CO_Dinos
# "CO_La_Junta_17_WSW">CO_La
# "CO_Montrose_11_ENE">CO_Mo
# "CO_Nunn_7_NNE">CO_Nunn</o
# "FL_Everglades_City_5_NE">
# "FL_Sebring_23_SSE">FL_Seb
# "FL_Titusville_7_E">FL_Tit
# "GA_Brunswick_23_S">GA_Bru
# "GA_Newton_8_W">GA_Newton<
# "GA_Newton_11_SW">GA_Newto
# "GA_Watkinsville_5_SSE">GA
# "HI_Hilo_5_S">HI_Hilo</opt
# "HI_Mauna_Loa_5_NNE">HI_Ma
# "IA_Des_Moines_17_E">IA_De
# "ID_Arco_17_SW">ID_Arco</o
# "ID_Murphy_10_W">ID_Murphy
# "IL_Champaign_9_SW">IL_Cha
# "IL_Shabbona_5_NNE">IL_Sha
# "IN_Bedford_5_WNW">IN_Bedf
# "KS_Manhattan_6_SSW">KS_Ma
# "KS_Oakley_19_SSW">KS_Oakl
# "KY_Bowling_Green_21_NNE">
# "KY_Versailles_3_NNW">KY_V
# "LA_Lafayette_13_SE">LA_La
# "LA_Monroe_26_N">LA_Monroe
# "ME_Limestone_4_NNW">ME_Li
# "ME_Old_Town_2_W">ME_Old_T
# "MI_Chatham_1_SE">MI_Chath
# "MI_Gaylord_9_SSW">MI_Gayl
# "MN_Goodridge_12_NNW">MN_G
# "MN_Sandstone_6_W">MN_Sand
# "MO_Chillicothe_22_ENE">MO
# "MO_Joplin_24_N">MO_Joplin
# "MO_Salem_10_W">MO_Salem</
# "MS_Holly_Springs_4_N">MS_
# "MS_Newton_5_ENE">MS_Newto
# "MT_Dillon_18_WSW">MT_Dill
# "MT_Lewistown_42_WSW">MT_L
# "MT_St._Mary_1_SSW">MT_St.
# "MT_Wolf_Point_29_ENE">MT_
# "MT_Wolf_Point_34_NE">MT_W
# "NC_Asheville_8_SSW">NC_As
# "NC_Asheville_13_S">NC_Ash
# "NC_Durham_11_W">NC_Durham
# "ND_Jamestown_38_WSW">ND_J
# "ND_Medora_7_E">ND_Medora<
# "ND_Northgate_5_ESE">ND_No
# "NE_Harrison_20_SSE">NE_Ha
# "NE_Lincoln_8_ENE">NE_Linc
# "NE_Lincoln_11_SW">NE_Linc
# "NE_Whitman_5_ENE">NE_Whit
# "NH_Durham_2_N">NH_Durham<
# "NH_Durham_2_SSW">NH_Durha
# "NM_Las_Cruces_20_N">NM_La
# "NM_Los_Alamos_13_W">NM_Lo
# "NM_Socorro_20_N">NM_Socor
# "NV_Baker_5_W">NV_Baker</o
# "NV_Denio_52_WSW">NV_Denio
# "NV_Mercury_3_SSW">NV_Merc
# "NY_Ithaca_13_E">NY_Ithaca
# "NY_Millbrook_3_W">NY_Mill
# "OH_Wooster_3_SSE">OH_Woos
# "OK_Goodwell_2_E">OK_Goodw
# "OK_Goodwell_2_SE">OK_Good
# "OK_Stillwater_2_W">OK_Sti
# "OK_Stillwater_5_WNW">OK_S
# "ON_Egbert_1_W">ON_Egbert<
# "OR_Coos_Bay_8_SW">OR_Coos
# "OR_Corvallis_10_SSW">OR_C
# "OR_John_Day_35_WNW">OR_Jo
# "OR_Riley_10_WSW">OR_Riley
# "PA_Avondale_2_N">PA_Avond
# "RI_Kingston_1_NW">RI_King
# "RI_Kingston_1_W">RI_Kings
# "SA_Tiksi_4_SSE">SA_Tiksi<
# "SC_Blackville_3_W">SC_Bla
# "SC_McClellanville_7_NE">S
# "SD_Aberdeen_35_WNW">SD_Ab
# "SD_Buffalo_13_ESE">SD_Buf
# "SD_Pierre_24_S">SD_Pierre
# "SD_Sioux_Falls_14_NNE">SD
# "TN_Crossville_7_NW">TN_Cr
# "TX_Austin_33_NW">TX_Austi
# "TX_Bronte_11_NNE">TX_Bron
# "TX_Edinburg_17_NNE">TX_Ed
# "TX_Monahans_6_ENE">TX_Mon
# "TX_Muleshoe_19_S">TX_Mule
# "TX_Palestine_6_WNW">TX_Pa
# "TX_Panther_Junction_2_N">
# "TX_Port_Aransas_32_NNE">T
# "UT_Brigham_City_28_WNW">U
# "UT_Torrey_7_E">UT_Torrey<
# "VA_Cape_Charles_5_ENE">VA
# "VA_Charlottesville_2_SSE"
# "WA_Darrington_21_NNE">WA_
# "WA_Quinault_4_NE">WA_Quin
# "WA_Spokane_17_SSW">WA_Spo
# "WI_Necedah_5_WNW">WI_Nece
# "WV_Elkins_21_ENE">WV_Elki
# "WY_Lander_11_SSE">WY_Land
# "WY_Moose_1_NNE">WY_Moose<
# "WY_Sundance_8_NNW">WY_Sun


# }



def _getUscrnData(year='2020', location='TX_Austin_33_NW', dataType="SOLARAD"):
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

def getCosineOfSolarZenith(lat, lon, datetime, timezone='US/Central'):
	date = pytz.timezone(timezone).localize(datetime)
	solar_altitude = pysolar.solar.get_altitude(lat,lon,date)
	solar_zenith = 90 - solar_altitude
	cosOfSolarZenith = math.cos(math.radians(solar_zenith))
	return cosOfSolarZenith

def preparePredictionVectors(year='2020', lat=30.581736, lon=-98.024098, station='TX_Austin_33_NW', timezone='US/Central'):
	cloudCoverData = _getDarkSkyCloudCoverForYear(year, lat, lon)
	ghiData = _getUscrnData(year, station)
	#for each 8760 hourly time slots, make a timestamp for each slot, look up cloud cover by that slot
	#then append cloud cover and GHI reading together
	start_time = datetime.datetime(int(year),1,1,0)
	cosArray = []
	input_array = []
	for i in range(len(ghiData)): #Because ghiData is leneth 8760, one for each hour of a year
		time = start_time + datetime.timedelta(minutes=60*i)
		tstamp = int(datetime.datetime.timestamp(time))
		try:
			cloudCover = cloudCoverData[tstamp]
		except KeyError:
			cloudCover = 0
		#I have my cloud cover, iterate over my ghi and cosine arrays
		cosOfSolarZenith = getCosineOfSolarZenith(lat, lon, time, timezone)
		ghi = ghiData[i]
		if ghi == 0:
			#Not most efficient logic but....
			#Still need to decide how to handle zero vals. Test this
			input_array.append((ghi, cloudCover))
		else:	
			ghi = np.log(ghi)
			input_array.append((ghi, cloudCover))
		cosArray.append(cosOfSolarZenith)
	return input_array, ghiData, cosArray


def predictPolynomial(X, model, degrees=5):
	X = _initPolyModel(X, degrees=5)
	predictions_dhi = model.predict(X)
	return predictions_dhi

def tests():
	print("********EASY SOLAR TEST STARTED************")

	# input_array, ghiData, cosArray = preparePredictionVectors(year='2020')
	# assert len(input_array) == len(ghiData) == len(cosArray)
	# log_prediction = predictPolynomial(input_array, clf_log_poly)
	# dhiPredictions = np.exp(log_prediction)
	# dhiXCosTheta = ghiData - dhiPredictions #This is cos(theta) * DNI
	# dhi_array = ([dhiXCosTheta[i]/cosArray[i] for i in range(len(dhiXCosTheta))]) 
	# result = list(zip(dhiPredictions, ghiData, dhi_array))
	# print([i for i in result])
	# print(len(result))
	# print(len(input_array))




if __name__ == '__main__':
	tests()
