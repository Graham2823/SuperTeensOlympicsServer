from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import ssl
import certifi
from bson import json_util, ObjectId
import json
import mysql.connector
from dotenv import load_dotenv
from datetime import datetime
import csv


app = Flask(__name__)
CORS(app)

# Define database configuration
db_config = {
    'host': os.environ.get('MYSQL_HOST'),
    'user': os.environ.get('MYSQL_USER'),
    'password': os.environ.get('MYSQL_PASSWORD'),
    'database': 'perfectMind'
}

# Connect to MySQL database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

#gets all events for an admin
@app.route('/', methods=['GET'])
def home():
    try:
        query = """
                SELECT * FROM STOlympics.community_centers
            """
        cursor.execute(query)
            
        # Fetch all rows for the query
        rows = cursor.fetchall()
        print(rows)

        # Initialize a dictionary to store events where the eventID is the key
        communityCenters = []
        for row in rows:
            communityCenterData={
                "communityCenterName": row[1],
                "communityCenterPoints": row[2]
            }
            communityCenters.append(communityCenterData)

        return jsonify(communityCenters)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
