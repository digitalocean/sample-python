from flask import Flask
from bigquery_to_mysql import bigquery_to_mysql

app = Flask(__name__)

@app.route("/")
def home():
    bigquery_to_mysql()
    return "Data has been updated!"
    # return "Hello, world!"

if __name__ == "__main__":
    app.run(host="0.0.0.0")
