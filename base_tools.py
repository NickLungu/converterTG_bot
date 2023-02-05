import psycopg2
import time
from datetime import datetime, timezone
import os


# Connect to db on google cloud
def connection():
    """
        :rtype: database connection
        :return: database connection
    """
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'))
    return conn


def insert_image_data(data_):
    """
        insert data into database "images" table
        :param data_: list [image path on the server, message id]
    """
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


def insert_command_data(data_):
    """
        insert data into database "commands" table
        :param data_: list [image path on the server, message id]
    """
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
    """
        :param chat_id: chat id
        :type chat_id: int

        :rtype: string
        :return: return path to last image from user on server
    """
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
    """
        :param chat_id: chat id
        :type chat_id: int

        :rtype: string
        :return: return path to last command from user on server
    """
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
        cursor.close()
        conn.close()
        command_name = record[0]
        return command_name
    except Exception as e:
        print(e)
        return "noway"


def update_is_on_server(chat_id, img_path):
    """
        mark in the database that the image has been removed from the server
        :param chat_id: chat id
        :type chat_id: int

        :param img_path: images path on server
        :type img_path: string
    """
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


def update_is_done(chat_id, command_name):
    """
        mark in the database that the command has been completed
        :param chat_id: chat id
        :type chat_id: int

        :param command_name: command name to update
        :type command_name: string
    """
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
