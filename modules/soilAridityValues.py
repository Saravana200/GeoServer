import ee
import geemap

async def mapCreatorSoilAridity(position,centerpos):

    Map=geemap.Map(center=centerpos,zoom=11.5)

    # Define region of interest
    geojsonObject = {
    "type": "Polygon",
    "coordinates": [position]
    }
    geometry=ee.Geometry(geojsonObject)

    dataset = ee.ImageCollection('MODIS/061/MOD11A1').filterDate('2025-01-31', '2025-04-01')
    dataset1 = ee.ImageCollection('MODIS/061/MOD09CMG').filterDate('2025-01-31', '2025-04-01')

    def calculate_rmax(image):
        image = image.clip(geometry)
        r = (
            image.select('Coarse_Resolution_Surface_Reflectance_Band_1').multiply(0.160)
            .add(image.select('Coarse_Resolution_Surface_Reflectance_Band_2').multiply(0.291))
            .add(image.select('Coarse_Resolution_Surface_Reflectance_Band_3').multiply(0.243))
            .add(image.select('Coarse_Resolution_Surface_Reflectance_Band_4').multiply(0.116))
            .add(image.select('Coarse_Resolution_Surface_Reflectance_Band_5').multiply(0.112))
            .add(image.select('Coarse_Resolution_Surface_Reflectance_Band_7').multiply(0.081))
        )

        mask = r.gt(0.7)
        zenith_angle = image.select('Coarse_Resolution_Solar_Zenith_Angle').multiply(3.14159 / 180).cos()
        rmax = r.multiply(-1).add(1).multiply(1367).multiply(zenith_angle)
        zenith_angle_mask = image.select('Coarse_Resolution_Solar_Zenith_Angle').gt(80)
        mask = mask.And(zenith_angle_mask)

        return rmax.updateMask(mask.Not())

    rmax_value = dataset1.map(calculate_rmax)
    rmax_mean_value = rmax_value.mean()
    rmax_mean_value

    landSurfaceTemperatureDay = dataset.select('LST_Day_1km').mean().multiply(0.02);
    landSurfaceTemperatureNight= dataset.select('LST_Night_1km').mean().multiply(0.02);

    difference= landSurfaceTemperatureDay.subtract(landSurfaceTemperatureNight).abs();


    AI= difference.divide(rmax_mean_value)

    AI = AI.reproject(crs='EPSG:3857', scale= 1000)


    stats = AI.reduceRegion(
    reducer= ee.Reducer.minMax(), # Calculate min and max
    geometry= geometry, # Use the image geometry (whole image)
    scale= 500, # Set an appropriate scale (in meters, adjust based on your dataset)
    maxPixels= 1e8 # Set a high maxPixels to ensure that all pixels are considered
    )

    minValue = stats.get('LST_Day_1km_min');
    maxValue = stats.get('LST_Day_1km_max');

    diffVis = {
    "min": minValue,
    "max": maxValue,
    "palette": ['blue', 'green', 'yellow', 'red']
    }

    Map.addLayer(AI.clip(geometry), diffVis, 'Land Surface Temperature (Masked)');
    Map

    params = {
        'dimensions': '1024x1024',
        'region': geometry,
        'format': 'png',
        **diffVis
    }

    # Generate thumbnail URL
    url = AI.getThumbURL(params)
    print("Fetching image from URL:", url)

    return url