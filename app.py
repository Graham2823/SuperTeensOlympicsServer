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
    'database': 'STOlympics'
}

# Connect to MySQL database
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

#gets all events for an admin
@app.route('/', methods=['GET'])
def home():
    try:
        query = """
                SELECT * FROM STOlympics.community_centers cc ORDER BY cc.community_centerPoints DESC
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

@app.route('/getSchedule', methods=['GET'])
def getSchedule():
    try:
        query="""
           SELECT sc.*, cc.community_centerName AS communityCenterName1, cc2.community_centerName AS communityCenterName2
            FROM 
            STOlympics.scheduled_events sc 
            LEFT JOIN 
            STOlympics.community_centers cc 
            ON sc.communityCenter1ID = cc.community_centerID 
            LEFT JOIN 
            STOlympics.community_centers cc2 
            ON sc.communityCenter2ID = cc2.community_centerID;

        """
        cursor.execute(query)
            
        # Fetch all rows for the query
        rows = cursor.fetchall()
        print(rows)

        # Initialize a dictionary to store events where the eventID is the key
        events = []
        for row in rows:
            eventData={
                "eventID": row[0],
                "eventSport": row[1],
                "eventDate": row[2],
                "eventTime": row[3],
                "eventTeam1": row[8],
                "eventTeam2": row[9],
                "eventWinner": row[6]
            }
            events.append(eventData)

        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/eventsBySite/<siteName>', methods=['GET'])
def getEventsBySite(siteName):
    try:
        query = """
           SELECT sc.*, cc1.community_centerName AS communityCenterName1, cc2.community_centerName AS communityCenterName2
            FROM 
            STOlympics.scheduled_events sc 
            LEFT JOIN 
            STOlympics.community_centers cc1 
            ON sc.communityCenter1ID = cc1.community_centerID 
            LEFT JOIN 
            STOlympics.community_centers cc2 
            ON sc.communityCenter2ID = cc2.community_centerID
            WHERE cc1.community_centerName = %s OR cc2.community_centerName = %s
        """
        cursor.execute(query, (siteName, siteName))
            
        # Fetch all rows for the query
        rows = cursor.fetchall()
        print(rows)

        # Initialize a dictionary to store events where the eventID is the key
        events = []
        for row in rows:
            eventData={
                "eventID": row[0],
                "eventSport": row[1],
                "eventDate": row[2],
                "eventTime": row[3],
                "eventTeam1": row[8],
                "eventTeam2": row[9],
                "eventWinner": row[6]
            }
            events.append(eventData)

        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/eventsByDate/<date>', methods=['GET'])
def getEventsByDate(date):
    try:
        query = """
           SELECT sc.*, cc1.community_centerName AS communityCenterName1, cc2.community_centerName AS communityCenterName2
            FROM 
            STOlympics.scheduled_events sc 
            LEFT JOIN 
            STOlympics.community_centers cc1 
            ON sc.communityCenter1ID = cc1.community_centerID 
            LEFT JOIN 
            STOlympics.community_centers cc2 
            ON sc.communityCenter2ID = cc2.community_centerID
            WHERE sc.eventDate = %s
        """
        cursor.execute(query, (date,))
            
        # Fetch all rows for the query
        rows = cursor.fetchall()
        print(rows)

        # Initialize a dictionary to store events where the eventID is the key
        events = []
        for row in rows:
            eventData={
                "eventID": row[0],
                "eventSport": row[1],
                "eventDate": row[2],
                "eventTime": row[3],
                "eventTeam1": row[8],
                "eventTeam2": row[9],
                "eventWinner": row[6]
            }
            events.append(eventData)

        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/eventsByDateAndCenter/<date>/<center>', methods=['GET'])
def getEventsByDateAndCenter(date, center):
    try:
        # Get date and community center name from the request body

        # Construct the SQL query
        query = """
           SELECT sc.*, cc1.community_centerName AS communityCenterName1, cc2.community_centerName AS communityCenterName2
            FROM 
            STOlympics.scheduled_events sc 
            LEFT JOIN 
            STOlympics.community_centers cc1 
            ON sc.communityCenter1ID = cc1.community_centerID 
            LEFT JOIN 
            STOlympics.community_centers cc2 
            ON sc.communityCenter2ID = cc2.community_centerID
            WHERE sc.eventDate = %s AND (cc1.community_centerName = %s OR cc2.community_centerName = %s)
        """
        
        # Execute the query with parameters
        cursor.execute(query, (date, center, center))
            
        # Fetch all rows for the query
        rows = cursor.fetchall()
        print(rows)
        # Initialize a list to store events
        events = []
        for row in rows:
            eventData={
                "eventID": row[0],
                "eventSport": row[1],
                "eventDate": row[2],
                "eventTime": row[3],
                "eventTeam1": row[8],
                "eventTeam2": row[9],
                "eventWinner": row[6]
            }
            events.append(eventData)

        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500




   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
