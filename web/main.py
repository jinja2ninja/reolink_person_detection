from fastapi import FastAPI, UploadFile, File, Form, APIRouter, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2 import sql
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
#from sqlalchemy import Column, Integer, MetaData, String, Table, select
import os
import logging
import psycopg2
import asyncio
from psycopg2 import sql
from psycopg2.extensions import AsIs
import re
import hvac

############################
# Hashicorp Vault Secret Retrevial
############################
vault_addr = os.environ['VAULT_ADDR']
client = hvac.Client(
        url=vault_addr,
        cert=('/web/app/cert.pem', '/web/app/key.pem')
        )

client.auth.cert.login()
secrets = client.secrets.kv.v2.read_secret(path='detector')
logging.info(secrets)
secrets = client.secrets.kv.v2.read_secret(path='detector')
############################
# Variable Declaration
############################
logging.basicConfig()
logging.getLogger().setLevel("DEBUG")
templates = Jinja2Templates(directory="/web/app/templates")
app = FastAPI()
app.mount("/photos", StaticFiles(directory="/web/app/photos"), name="photos")
app.mount("/templates", StaticFiles(directory="/web/app/templates"), name="templates")
api_router = APIRouter()

############################
# Retrieve previous image
############################
async def get_previous(camera, filename):
  try:
      connection = psycopg2.connect(user=secrets['data']['data']["pg_user"],
                                    password=secrets['data']['data']["pg_pass"],
                                    host=secrets['data']['data']["pg_host"],
                                    port="5432",
                                    database="detector")
      filename = f"./photos/{camera}/{filename}.jpeg"
      logging.debug(f"filename is {filename}")
      cursor = connection.cursor()
      table = camera.replace("'", "")
  
      cursor.execute(
          """
          SELECT * 
          FROM %s 
          WHERE TIMESTAMP > (
              SELECT TIMESTAMP 
              FROM %s 
              WHERE filename = %s
          )
          ORDER BY TIMESTAMP ASC
          LIMIT 1;
          """,
          [AsIs(table), AsIs(table), filename]
      )
      previous_image = cursor.fetchall()
      logging.debug(f"five rows result: {five_rows}")
      return previous_image
  except (Exception, psycopg2.Error) as error:
      logging.error("Error while fetching data from PostgreSQL", error)


############################
# Retrieve next image
############################
async def get_next(camera, filename):
  try:
      connection = psycopg2.connect(user=secrets['data']['data']["pg_user"],
                                    password=secrets['data']['data']["pg_pass"],
                                    host=secrets['data']['data']["pg_host"],
                                    port="5432",
                                    database="detector")
      filename = f"./photos/{camera}/{filename}.jpeg"
      logging.debug(f"filename is {filename}")
      cursor = connection.cursor()
      table = camera.replace("'", "")
  
      cursor.execute(
          """
          SELECT * 
          FROM %s 
          WHERE TIMESTAMP < (
              SELECT TIMESTAMP 
              FROM %s 
              WHERE filename = %s
          )
          ORDER BY TIMESTAMP DESC
          LIMIT 1;
          """,
          [AsIs(table), AsIs(table), filename]
      )
      next_image = cursor.fetchall()
      return next_image
  except (Exception, psycopg2.Error) as error:
      logging.error("Error while fetching data from PostgreSQL", error)



############################
# Retrieve DB Rows for "latest" page
############################
async def read_latest_rows(camera):
  try:
      connection = psycopg2.connect(user=secrets['data']['data']["pg_user"],
                                    password=secrets['data']['data']["pg_pass"],
                                    host=secrets['data']['data']["pg_host"],
                                    port="5432",
                                    database="detector")
      cursor = connection.cursor()
      table = camera.replace("'", "")
      cursor.execute(
          """
        SELECT * from %s
        ORDER BY TIMESTAMP DESC LIMIT 5;
          """,
          [AsIs(table)]
      )
      latest_rows = cursor.fetchall()
      logging.debug(latest_rows)
      return latest_rows
  except (Exception, psycopg2.Error) as error:
      logging.error("Error while fetching data from PostgreSQL", error)


############################
# Retrieve list of cameras from DB
############################
async def get_cameras():
  try:
      connection = psycopg2.connect(user=secrets['data']['data']["pg_user"],
                                    password=secrets['data']['data']["pg_pass"],
                                    host=secrets['data']['data']["pg_host"],
                                    port="5432",
                                    database="detector")
      cursor = connection.cursor()
      cursor.execute(
          """
          SELECT table_name
            FROM information_schema.tables
           WHERE table_schema='public'
             AND table_type='BASE TABLE';
          """
      )
      cameras = cursor.fetchall()
      camera_names = []
      for name in cameras:
          camera_name = re.sub(r'\'\,\)', '', re.sub(r'\(\'', '', str(name)))
          logging.debug(camera_name)
          camera_names.append(camera_name)
      return camera_names
  except (Exception, psycopg2.Error) as error:
      logging.error("Error while fetching data from PostgreSQL", error)

############################
# "Latest" Page
############################
@app.get("/{camera}/detection/latest", response_class=HTMLResponse)
async def latest(request: Request, camera: str):
  latest_rows = await read_latest_rows(camera)
  filename = latest_rows[0][0]
  cameras_list = await get_cameras()
  previous_image = await get_previous(camera,filename)
  current_image = re.sub(r'^.*/', '', filename).rstrip(".jpeg")
  next_image = await get_next(camera,current_image)
  logging.debug(f"previous image is {previous_image}")
  return templates.TemplateResponse("template.html", {"next_image": next_image,"current_image": current_image,"previous_image": previous_image,"request": request, "cameras_list": cameras_list, "camera": camera})

############################
# detection Page
############################
@app.get("/{camera}/detection/{filename}", response_class=HTMLResponse)
async def five_rows(request: Request,filename: str, camera: str):
  previous_image = await get_previous(camera,filename)
  current_image = re.sub(r'^.*/', '', filename)
  next_image = await get_next(camera,filename)
  cameras_list = await get_cameras()
  return templates.TemplateResponse("template.html", {"next_image": next_image,"current_image": current_image,"previous_image": previous_image,"request": request, "cameras_list": cameras_list, "camera": camera})