import os

import psycopg2

# Connection settings are read from the environment so credentials stay out of the code
BLAZEGRAPH_URL = os.environ.get("BLAZEGRAPH_URL", "http://localhost:9999/blazegraph/sparql")


def connect_postgres():
    # The password is not passed here: libpq reads it from PGPASSWORD or ~/.pgpass
    return psycopg2.connect(
        dbname=os.environ.get("PGDATABASE", "heu-intelligent"),
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5432"),
        user=os.environ.get("PGUSER", "postgres"),
    )
