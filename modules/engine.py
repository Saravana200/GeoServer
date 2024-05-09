import ee
import geemap

def initialize():
    print(ee.Authenticate())
    ee.Initialize(project='ee-dhruvassaravana')
    print(ee.String('Hello from the Earth Engine servers!').getInfo())


async def mapCreator(position,centerpos):
    Map=geemap.Map(center=centerpos,zoom=11.5)

    geojsonObject = {
    "type": "Polygon",
    "coordinates": [
        position
    ]
    }
    geometry=ee.Geometry(geojsonObject)

    dataset = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/006').filter(ee.Filter.date('2024-01-01', '2024-01-31')).filterBounds(geometry)

    soilMositureSurface = dataset.select('soil_moisture_am')

    merged_image = soilMositureSurface.mean().clip(geometry)

    min = merged_image.reduceRegion(reducer=ee.Reducer.min(), geometry=geometry, scale=400)
    max = merged_image.reduceRegion(reducer=ee.Reducer.max(), geometry=geometry, scale=400)

    print("Maximum Soil Moisture Value:", max.get('soil_moisture_am').getInfo())

    vis={
        "min":0,
        "max":0.5,
        "palette":  ['0300ff', '418504', 'efff07', 'efff07', 'ff0303']
    }

    Map.add_layer(merged_image, {"min":min.get('soil_moisture_am').getInfo(),"max":max.get('soil_moisture_am').getInfo(),'palette': ['0300ff', '418504', 'efff07', 'efff07', 'ff0303']}, 'Soil Mositure',True,1)
    Map.add_layer(soilMositureSurface.mean(),vis,"test")

    Map.layer_to_image("Soil Mositure",output="./assets/output.png",scale=20,region=geometry)