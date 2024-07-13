#!/usr/bin/env python3
from nicegui import ui
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import AsIs
from itertools import cycle
import hvac
import os
import logging
import re
############################
# Hashicorp Vault Secret Retrevial
############################
client = hvac.Client(
        url='https://vault.mischaf.us'
        )
client.auth.approle.login(
    role_id=os.environ['ROLE_ID'],
    secret_id=os.environ['SECRET_ID'],
)
secrets = client.secrets.kv.v2.read_secret(path='detector')
logging.info(secrets)
secrets = client.secrets.kv.v2.read_secret(path='detector')

############################
# Logging Config
############################
logging.basicConfig()
logging.getLogger().setLevel("DEBUG")


##############################
# Images List
##############################
## create images list
def read_latest_rows(camera):
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
        ORDER BY TIMESTAMP DESC;
          """,
          [AsIs(table)]
      )
      latest_rows = cursor.fetchall()
      #logging.debug(latest_rows)
      return latest_rows
  except (Exception, psycopg2.Error) as error:
      logging.error("Error while fetching data from PostgreSQL", error)
def create_images_list(camera):
  latest_rows = read_latest_rows(camera)
  #image_paths = list(latest_rows[0])
  image_paths = []
  for row in latest_rows:
    image_paths.append(row[0])
  return(image_paths)
#####################################
# Camera List
#####################################
def get_cameras():
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
          #logging.debug(camera_name)
          camera_names.append(camera_name)
      return camera_names
  except (Exception, psycopg2.Error) as error:
      logging.error("Error while fetching data from PostgreSQL", error)

#######################################
# Create Image Lists
#######################################
cameras = get_cameras()
images = {}
for camera in cameras:
  image_list = create_images_list(camera)
  images[f'{camera}'] = image_list

print(images)

######################################
# Nice UI
######################################
@ui.page('/', response_timeout = 99)

async def page():
    async def check(image_iterator, camera):
        try:
            result = await ui.run_javascript('window.pageYOffset >= document.body.offsetHeight - 2 * window.innerHeight')
            logging.debug(f'JavaScript result for {camera}: {result}')
            if result:
                next_image = next(image_iterator)
                logging.debug(f'Next image for {camera}: {next_image}')
                ui.image(next_image)
        except TimeoutError:
            logging.error('TimeoutError: The client might have disconnected')
        except Exception as e:
            logging.error(f'Exception occurred: {e}')

    await ui.context.client.connected()
    dark = ui.dark_mode()
    ui.page_title('Person Detector')
    with ui.header(elevated=True).style('background-color: #3874c8').classes('items-center justify-between'):
        ui.label('Person Detector')
        with ui.tabs() as tabs:
          for camera in cameras:
              ui.tab(re.sub(r'_', ' ', camera))
        with ui.row():
          ui.button('Dark Mode', on_click=dark.enable)
          ui.button('Light Mode', on_click=dark.disable)
    with ui.footer(value=False) as footer:
        ui.label('Footer')
    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support').props('fab')
    with ui.tab_panels(tabs, value=cameras[0]).classes('w-full'):
        for camera in cameras:
            with ui.tab_panel(re.sub(r'_', ' ', camera)):
                image_iterator = cycle(images[camera])
                ui.timer(1.1, lambda it=image_iterator, cam=camera: check(it, cam))

ui.run()
