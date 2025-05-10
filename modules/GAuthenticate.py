import ee

def initialize():
    service_acct = "eesaravana@ee-dhruvassaravana.iam.gserviceaccount.com"
    credentials= ee.ServiceAccountCredentials(service_acct,"gee_apikey.json")
    ee.Initialize(credentials)
    print(ee.String('Hello from the Earth Engine servers!').getInfo())
