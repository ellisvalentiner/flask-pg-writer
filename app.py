#!/usr/bin/env/python3
# -*- coding: utf-8 -*-
import os
import psycopg2
from psycopg2.extras import (
    RealDictCursor,
)
from psycopg2.extensions import (
    new_type,
    register_type,
    register_adapter,
)
from flask import (
    Flask,
    request,
)

DEC2FLOAT = new_type(
    psycopg2.extensions.DECIMAL.values,
    "DEC2FLOAT",
    lambda value, curs: float(value) if value is not None else None,
)
register_type(DEC2FLOAT)
register_adapter(dict, psycopg2.extras.Json)

app = Flask(__name__)

USER = os.getenv("POSTGRES_USER", "postgres")
PWD = os.getenv("POSTGRES_PWD", "postgres")
HOST = os.getenv("POSTGRES_HOST", "0.0.0.0")
PORT = os.getenv("POSTGRES_PORT", 5432)
DBNAME = os.getenv("POSTGRES_DBNAME", "postgres")

try:
    conn = psycopg2.connect(
        dsn=f"postgres://{USER}:{PWD}@{HOST}:{PORT}/{DBNAME}",
        cursor_factory=RealDictCursor
    )
except psycopg2.OperationalError as err:
    print(err)


@app.route("/", methods=["POST"])
def save():
    with conn.cursor() as cur:
        cur.execute(
            query="INSERT INTO requests (headers, content) VALUES (%(headers)s, %(content)s);",
            vars={
                "headers": dict(request.headers),
                "content": request.get_json()
            }
        )
        conn.commit()
    return "OK"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
