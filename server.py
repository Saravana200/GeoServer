from modules import *
from models import *
from security import *
from service import *
from mistralai import Mistral
from fastapi import Body, FastAPI, Depends,Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv
import uvicorn
import os
import asyncio
import requests
from sqlalchemy import text
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager


load_dotenv()

@asynccontextmanager
async def conn_check(app: FastAPI):
    for attempts in range(5):
        try:
            async with session_maker() as session:
                await session.execute(text("select 1"))
            print("Connection successful")
            break
        except Exception as e:
            if(attempts==5):
                 print("Connection failed please retry due to:" +e) 
                 raise
            await asyncio.sleep(2)
    yield
    print("Ending service")

app = FastAPI(lifespan=conn_check)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def value_error_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": str(exc.detail)},
    )

@app.exception_handler(Exception)
async def value_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

@app.post("/signup")
async def singup(token:str=Depends(register_user)):
    return JSONResponse(status_code=200,content={"token":token})

@app.post("/login")
async def login(token:str = Depends(login_user)):
    return JSONResponse(status_code=200,content={"token":token})
     

@app.post("/SoilMoistureImage",responses={200:{"content":{"image/png":{}}}},response_class=Response)
async def image(pos:Coordinates = Body(...),user = Depends(get_user), service:SoilMoistureService = Depends(soil_moisture_service_factory)):
      if(not user):
           raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="invalid user",
        )

      x=0.1
      y=0.1
      c1=[pos.long-x,pos.lat+y]
      c2=[pos.long-x,pos.lat-y]
      c3=[pos.long+x,pos.lat-y]
      c4=[pos.long+x,pos.lat+y]
      coordinates=[c1,c2,c3,c4]
      data = await mapCreator(coordinates,(pos.lat,pos.long))
      image_bytes = requests.get(data["url"])
      if await service.save_soil_moisture(user_id=user.id,value=data["avg_value"],coordinates=pos):   
        return Response(content=image_bytes.content,media_type="image/png")

@app.post("/SoilAridityImage",responses={200:{"content":{"image/png":{}}}},response_class=Response)
async def image(pos:Coordinates = Body(...),user = Depends(get_user), service:SoilAridityService = Depends(soil_aridity_service_factory)):
      if(not user):
           raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="invalid user",
        )
      x=0.1
      y=0.1
      c1=[pos.long-x,pos.lat+y]
      c2=[pos.long-x,pos.lat-y]
      c3=[pos.long+x,pos.lat-y]
      c4=[pos.long+x,pos.lat+y]
      coordinates=[c1,c2,c3,c4]
      data = await mapCreatorSoilAridity(coordinates,(pos.lat,pos.long))
      image_bytes = requests.get(data["url"])
      if await service.save_soil_aridity(user_id=user.id,value=data["avg_value"],coordinates=pos):   
        return Response(content=image_bytes.content,media_type="image/png")


@app.post("/weather")
async def get_weather(coords:Coordinates = Body(...),user = Depends(get_user)):
    if(not user):
           raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="invalid user",
        )
    api_key = os.getenv("OPEN_WEATHER_KEY")
    base_url = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}"
    lat = coords.lat
    lon = coords.long
    url = base_url.format(lat, lon, api_key)
    response = requests.get(url)
    response_payload = dict()
    if response.status_code == 200:
        data = response.json()
        response_payload["wind_speed"] = data["wind"]["speed"]
        response_payload["humidity"] = data["main"]["humidity"]
        response_payload["temperature"] = data["main"]["temp"]
        return JSONResponse(status_code=200,content=response_payload)
    else:
        return {"error": f"Failed to retrieve weather data. Status code: {response.status_code}"}

@app.post("/chat/weather")
async def get_weather(coords:Coordinates = Body(...),user = Depends(get_user)):
    if(not user):
           raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="invalid user",
        )
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
    

@app.post("/chat")
async def get_weather(data = Body(...),user = Depends(get_user)):
    if(not user):
           raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="invalid user",
        )
    mistral_api_key = os.getenv("MISTRAL_KEY")
    model = "mistral-large-latest"
    client = Mistral(api_key=mistral_api_key)
    chat_response = client.chat.complete(
        model = model,
        messages = [
            {
                "role": "user",
                "content": data["text"],
            },
        ]
    )
    print(chat_response.choices[0].message.content)
    return JSONResponse(status_code=200,content={"reply":chat_response.choices[0].message.content})
    
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



if(__name__) == '__main__':
        uvicorn.run(
        "server:app",
        host    = "127.0.0.1",
        port    = 8036, 
        reload  = True
    )