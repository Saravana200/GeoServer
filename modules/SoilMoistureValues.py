import ee
import geemap

async def mapCreator(position,centerpos):
    Map=geemap.Map(center=centerpos,zoom=11.5)

    geojsonObject = {
    "type": "Polygon",
    "coordinates": [
        position
    ]
    }
    geometry=ee.Geometry(geojsonObject)

    dataset = ee.ImageCollection('NASA/SMAP/SPL3SMP_E/006').filter(ee.Filter.date('2025-01-01', '2025-04-30')).filterBounds(geometry)

    soilMositureSurface = dataset.select('soil_moisture_am')

    merged_image = soilMositureSurface.mean().clip(geometry)

    min = merged_image.reduceRegion(reducer=ee.Reducer.min(), geometry=geometry, scale=1000)
    max = merged_image.reduceRegion(reducer=ee.Reducer.max(), geometry=geometry, scale=1000)

    print("Maximum Soil Moisture Value:", max.get('soil_moisture_am').getInfo())

    min_value = min.get('soil_moisture_am').getInfo()
    max_value = max.get('soil_moisture_am').getInfo()

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
    return url