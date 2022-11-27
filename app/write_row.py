import psycopg2
import asyncio
from psycopg2 import sql


def write_row(db_config, detection, camera):
  conn = psycopg2.connect(
      host=db_config["host"],
      database=db_config["db"],
      user=db_config["user"],
      password=db_config["password"])
  cur = conn.cursor()
  # check if table exists
  #tablecheck = "SELECT datname FROM pg_catalog.pg_database WHERE datname = (%s);"
  tablecheck = "SELECT exists(select * from information_schema.tables where table_name=%s);"
  table = (camera, )
  cur.execute(tablecheck, table)
  table_test = cur.fetchone()[0]
  print(table_test)
  print(camera)
  if not table_test:
   # print(f"{camera} table doesn't exist, creating it now")
    tablecreate = sql.SQL("""
      create table {camera} (
        filename   VARCHAR PRIMARY KEY NOT NULL,
        label      VARCHAR,
        confidence INT,
        ymincoord       INT,
        ymaxcoord       INT,
        xmincoord       INT,
        xmaxcoord       INT,
        timestamp  VARCHAR,
        success    BOOLEAN
        );""").format(camera=sql.Identifier(camera))
    table2 = (str(camera), )
    createtable = cur.execute(tablecreate, table)
    print(tablecreate)
  else:
    print(f"table: {camera} already exists, nothing to do.")
  row_query = sql.SQL("""
    INSERT INTO {camera} (filename, label, confidence, ymincoord, ymaxcoord, xmincoord, xmaxcoord, timestamp, success)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s );""").format(camera=sql.Identifier(camera))
  row_data = (detection["filename"], detection["label"], detection["confidence"], detection["ymaxcoord"], detection["ymincoord"], detection["xmaxcoord"], detection["xmincoord"], detection["timestamp"], detection["success"])
  cur.execute(row_query, row_data)
  conn.commit()
  cur.close()

  return table_test


# Example DB params:
db_config = {'password': 'test', 'db': 'detector', 'host': 'db', 'user': 'detector'}
# Example detection:
#detection = {"camera": "test"}
detection = {'label': "person", 'confidence': 50, 'ymincoord': 100, 'ymaxcoord': 120, 'xmincoord': 175, 'xmaxcoord': 200, 'timestamp': "2022-11-09T05.03.06", 'filename': "2022-11-09T05.13.06.jpeg", 'success': True}

#row = create_table(db_config, detection, "front_door")
#print(row)
#while True:
#  if __name__ == '__write_row__':
#    asyncio.run(main())