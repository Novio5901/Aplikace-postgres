import psycopg
from config import  *

def connect():
    return psycopg.connect(
        host="192.168.135.10",
        port="5432",
        dbname="obce",
        user="student",
        password="bluemonkey3"
    )