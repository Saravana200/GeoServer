import asyncio
from fastapi import Body, FastAPI,Request,Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response
import uvicorn
from pydantic import BaseModel
import requests
from modules.engine import initialize,mapCreator

initialize()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="views")

class postion(BaseModel):
      lat:float
      long:float

@app.get("/")
async def test():
    return {
  "greeting": "Welcome to quicktype!"
}

@app.post("/image",responses={200:{"content":{"image/png":{}}}},response_class=Response)
async def image(pos:postion):
      x=0.1
      y=0.1
      c1=[pos.long-x,pos.lat+y]
      c2=[pos.long-x,pos.lat-y]
      c3=[pos.long+x,pos.lat-y]
      c4=[pos.long+x,pos.lat+y]
      coordinates=[c1,c2,c3,c4]
      await mapCreator(coordinates,(pos.lat,pos.long))
      f=open("./assets/output.png","rb")
      img:bytes=f.read()
      return Response(content=img,media_type="image/png")




api_key = "3aa0dead85a724309f8cb68adc84017f"
base_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"

class Coordinates(BaseModel):
    lat: float
    long: float

@app.post("/weather")
async def get_weather(coords: Coordinates = Body(...)):
    lat = coords.lat
    lon = coords.long
    url = base_url.format(lat, lon, api_key)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        wind_speed = data["wind"]["speed"]
        humidity = data["main"]["humidity"]
        temperature = data["main"]["temp"]
        return {"greeting": ""} 
    else:
        return {"error": f"Failed to retrieve weather data. Status code: {response.status_code}"}

if(__name__) == '__main__':
        uvicorn.run(
        "server:app",
        host    = "127.0.0.1",
        port    = 8036, 
        reload  = True
    )