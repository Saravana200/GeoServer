import ee
import geemap
from datetime import datetime, timedelta

async def mapCreator(position,centerpos):
    Map=geemap.Map(center=centerpos,zoom=11.5)

    geojsonObject = {
    "type": "Polygon",
    "coordinates": [
        position
    ]
    }
    geometry=ee.Geometry(geojsonObject)

    end_date = datetime.today()
    start_date = end_date - timedelta(days=14)

    dataset = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/006')\
        .filter(ee.Filter.date(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))\
        .filterBounds(geometry)

    soilMositureSurface = dataset.select('soil_moisture_am')

    merged_image = soilMositureSurface.mean().clip(geometry)

    min = merged_image.reduceRegion(reducer=ee.Reducer.min(), geometry=geometry, scale=1000)
    max = merged_image.reduceRegion(reducer=ee.Reducer.max(), geometry=geometry, scale=1000)
    avg = merged_image.reduceRegion(reducer=ee.Reducer.mean(), geometry=geometry, scale=1000)

    min_value = min.get('soil_moisture_am').getInfo()
    max_value = max.get('soil_moisture_am').getInfo()
    avg_value = avg.get('soil_moisture_am').getInfo()

    print("Average Soil Moisture Value:", avg_value)

    vis={
        "min": min_value,
        "max": max_value,
        'palette': ['ff0303', 'efff07', 'efff07', '418504', '0300ff']
        }

    Map.add_layer(merged_image,vis, 'Soil Mositure',True,1)

    # Map.layer_to_image("Soil Mositure",output="./assets/output.png",scale=20,region=geometry)

    params = {
        'dimensions': '1024x1024',
        'region': geometry,
        'format': 'png',
        **vis
    }

    url = merged_image.getThumbURL(params)
    print("Fetching image from URL:", url)
    return {"url":url,"avg_value":avg_value}