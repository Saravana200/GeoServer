from modules import *
from models import *
from mistralai import Mistral
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv
import uvicorn
import os
import requests

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def test():
    wind_speed =20
    humidity = 10
    temperature =34
    api_key = os.getenv("MISTRAL_KEY")
    model = "mistral-large-latest"
    client = Mistral(api_key=api_key)
    lat=22.3
    lon=22.7
    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": "(dont include formating for special characters and give in one paragraph)given the wind speed {0} and humidity as {1} and temperature {2} and the coordinates are {3},{4} what is the best crop to grow in the location? and what more can you advice a farmer at that place".format(wind_speed,humidity,temperature,lat,lon),
            },
        ]
    )
    print(chat_response.choices[0].message.content)
    return {
  "greeting": chat_response
}

@app.post("/SoilMoistureImage",responses={200:{"content":{"image/png":{}}}},response_class=Response)
async def image(pos:Coordinates):
      x=0.1
      y=0.1
      c1=[pos.long-x,pos.lat+y]
      c2=[pos.long-x,pos.lat-y]
      c3=[pos.long+x,pos.lat-y]
      c4=[pos.long+x,pos.lat+y]
      coordinates=[c1,c2,c3,c4]
      url = await mapCreator(coordinates,(pos.lat,pos.long))
      image_bytes = requests.get(url)
      return Response(content=image_bytes.content,media_type="image/png")

@app.post("/SoilAridityImage",responses={200:{"content":{"image/png":{}}}},response_class=Response)
async def image(pos:Coordinates):
      x=0.1
      y=0.1
      c1=[pos.long-x,pos.lat+y]
      c2=[pos.long-x,pos.lat-y]
      c3=[pos.long+x,pos.lat-y]
      c4=[pos.long+x,pos.lat+y]
      coordinates=[c1,c2,c3,c4]
      url = await mapCreatorSoilAridity(coordinates,(pos.lat,pos.long))
      image_bytes = requests.get(url)
      return Response(content=image_bytes.content,media_type="image/png")


@app.post("/weather")
async def get_weather(coords:Coordinates = Body(...)):
    api_key = os.getenv("OPEN_WEATHER_KEY")
    base_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    lat = coords.lat
    lon = coords.long
    url = base_url.format(lat, lon, api_key)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]
        temperature = data["main"]["temp"]
        mistral_api_key = os.getenv("MISTRAL_KEY")
        model = "mistral-large-latest"
        client = Mistral(api_key=mistral_api_key)
        chat_response = client.chat.complete(
            model = model,
            messages = [
                {
                    "role": "user",
                    "content": "(dont include formating for special characters and give in one paragraph)given the wind speed {0} and humidity as {1} and temperature {2} and the coordinates are {3},{4} what is the best crop to grow in the location? and what more can you advice a farmer at that place".format(wind_speed,humidity,temperature,lat,lon),
                },
            ]
        )
        print(chat_response.choices[0].message.content)
        
        return {"greeting": chat_response.choices[0].message.content} 
    else:
        return {"error": f"Failed to retrieve weather data. Status code: {response.status_code}"}



if(__name__) == '__main__':
        uvicorn.run(
        "server:app",
        host    = "127.0.0.1",
        port    = 8036, 
        reload  = True
    )