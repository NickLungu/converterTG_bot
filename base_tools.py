import psycopg2
import time
from datetime import datetime, timezone
from config import *


# Connect to db on google cloud
def connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD)
    return conn


def insert(data_):
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_insert_query = """ INSERT INTO images (img_id, img_path, chat_id, date_reg, is_on_server)
                                           VALUES (%s,%s,%s,%s,%s)"""

        # insert img_id, img_path, chat_id, date_time
        record_to_insert = (int((time.time()*1000)/60), data_[0], data_[1], datetime.now(timezone.utc), True)
        cursor.execute(postgres_insert_query, record_to_insert)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Cannot insert," + str(e))


def insert_command(data_):
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_insert_query = """ INSERT INTO commands (command_id, chat_id, command_name, date_reg, is_done)
                                           VALUES (%s,%s,%s,%s,%s)"""

        # insert command_id, chat_id, command_name, date_reg
        record_to_insert = (int((time.time()*1000)/60),
                            data_[0],
                            data_[1],
                            datetime.now(timezone.utc),
                            data_[2])
        cursor.execute(postgres_insert_query, record_to_insert)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Cannot insert," + str(e))


def get_last_image(chat_id):
    path = ""
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_get_query = "SELECT img_path FROM images WHERE chat_id = %s and " \
                             "is_on_server = true ORDER BY date_reg DESC " \
                             "LIMIT 1" \
                             % str(chat_id)
        cursor.execute(postgres_get_query)
        record = cursor.fetchall()
        if len(record) > 0:
            path = record[0]
        cursor.close()
        conn.close()
        return path
    except Exception as e:
        print(e)
        return path


def get_last_command(chat_id):
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_get_query = "SELECT command_name FROM commands " \
                             "WHERE chat_id = %s AND is_done = False " \
                             "ORDER BY date_reg DESC " \
                             "LIMIT 1" \
                             % str(chat_id)
        cursor.execute(postgres_get_query)
        record = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        command_name = record[0]
        return command_name
    except Exception as e:
        print(e)
        return "noway"


def update_is_on_server(chat_id, img_path):
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_get_query = "UPDATE images set is_on_server = False " \
                             "WHERE chat_id = %s and img_path = '%s'; " % (str(chat_id), str(img_path))
        cursor.execute(postgres_get_query)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        return "noway"


def update_is_done(chat_id, command_name):
    try:
        conn = connection()
        cursor = conn.cursor()
        postgres_get_query = "UPDATE commands set is_done = True WHERE chat_id = %s and command_name = '%s'; " % (str(chat_id), str(command_name))
        cursor.execute(postgres_get_query)
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
        return "noway"
