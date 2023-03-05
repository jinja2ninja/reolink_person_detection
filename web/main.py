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

logging.basicConfig()
logging.getLogger().setLevel("INFO")
templates = Jinja2Templates(directory="/web/app/templates")
app = FastAPI()
app.mount("/photos", StaticFiles(directory="/web/app/photos"), name="photos")
app.mount("/templates", StaticFiles(directory="/web/app/templates"), name="templates")
api_router = APIRouter()

async def read_latest_rows(camera):
  try:
      connection = psycopg2.connect(user="detector",
                                    password="replace",
                                    host="db",
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


async def read_rows(filename, camera):
  try:
      connection = psycopg2.connect(user="detector",
                                    password="replace",
                                    host="db",
                                    port="5432",
                                    database="detector")
      cursor = connection.cursor()
      table = camera.replace("'", "")
      cursor.execute(
          """
        WITH init AS (
            SELECT timestamp
            FROM %s
            WHERE filename = %s
         )
         
         (
            (SELECT %s.*
             FROM %s
                CROSS JOIN init
             WHERE %s.timestamp > init.timestamp
             ORDER BY %s.timestamp DESC 
             LIMIT 2)
           UNION ALL
         (
            SELECT %s.*
            FROM %s
            WHERE filename = %s
         )
          UNION ALL 
            (SELECT %s.*
             FROM %s
                CROSS JOIN init 
             WHERE %s.timestamp < init.timestamp
             ORDER BY %s.timestamp DESC
             LIMIT 2)
         );
          """,
          [AsIs(table), filename, AsIs(table), AsIs(table), AsIs(table), AsIs(table), AsIs(table), AsIs(table), filename, AsIs(table), AsIs(table), AsIs(table), AsIs(table)]
      )
      rows = cursor.fetchall()
      return rows
  except (Exception, psycopg2.Error) as error:
      logging.error("Error while fetching data from PostgreSQL", error)

async def get_cameras():
  try:
      connection = psycopg2.connect(user="detector",
                                    password="ksljhfdsljkfhbnsldkjnsithenswtiowehrtpi4467usbngfjklhfnghjkdsgbfdk007n",
                                    host="db",
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

@app.get("/{camera}/detection/latest", response_class=HTMLResponse)
async def latest(request: Request, camera: str):
  
  #filename_full = f"./photos/{camera}/{filename}.jpeg"
  #filename_minimal = re.sub(".\/photos\/.+\/", "", filename)
  latest_rows = await read_latest_rows(camera)
  filename = latest_rows[0][0]
  cameras_list = await get_cameras()
  return templates.TemplateResponse("detection_template_latest.html", {"request": request, "cameras_list": cameras_list, "filename": filename, "latest_rows": latest_rows, "camera": camera})

@app.get("/{camera}/detection/{filename}", response_class=HTMLResponse)
async def detection(request: Request, filename: str, camera: str):
  filename_full = f"./photos/{camera}/{filename}.jpeg"
  #filename_minimal = re.sub(".\/photos\/.+\/", "", filename)
  rows = await read_rows(filename_full, camera)
  cameras_list = await get_cameras()
  return templates.TemplateResponse("detection_template.html", {"request": request, "cameras_list": cameras_list, "filename": filename, "rows": rows, "camera": camera})

######
# Read Single row
#######
#async def read_rows(filename):
#  try:
#      connection = psycopg2.connect(user="detector",
#                                    password="ksljhfdsljkfhbnsldkjnsithenswtiowehrtpi4467usbngfjklhfnghjkdsgbfdk007n",
#                                    host="db",
#                                    port="5432",
#                                    database="detector")
#      cursor = connection.cursor()
#      cursor.execute(
#          """
#          SELECT *
#          FROM test
#          WHERE filename = %s;
#          """,
#          [filename,]
#      )
#      row = cursor.fetchone()
#      return row
#  except (Exception, psycopg2.Error) as error:
#      logging.error("Error while fetching data from PostgreSQL", error)
