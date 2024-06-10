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
            ON sc.communityCenter2ID = cc2.community_centerID ORDER BY sc.eventDate, sc.eventTime;

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
                "eventLocation": row[4],
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
                "eventLocation": row[4],
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
                "eventLocation": row[4],
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
                "eventLocation": row[4],
                "eventTeam1": row[8],
                "eventTeam2": row[9],
                "eventWinner": row[6]
            }
            events.append(eventData)

        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import datetime

@app.route('/createEvent', methods=['POST'])
def createEvent():
    try:
        event_data = request.json

        # Extract only the date part
        event_date = event_data['eventDate'].split('T')[0]

        # Lookup community center IDs
        cursor.execute("""
            SELECT community_centerID FROM STOlympics.community_centers 
            WHERE community_centerName = %s OR community_centerName = %s""",
            (event_data['eventCommunityCenter1ID'], event_data['eventCommunityCenter2ID'])
        )
        community_center_ids = cursor.fetchall()
        
        # Check if both community centers exist
        if len(community_center_ids) != 2:
            return jsonify({'error': 'Invalid community center names provided'}), 400

        # Insert event into database
        cursor.execute("""
            INSERT INTO STOlympics.scheduled_events 
            (eventSport, eventDate, eventTime, eventLocation, communityCenter1ID, communityCenter2ID)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                event_data['eventSport'], 
                event_date,  # Use extracted date
                event_data['eventTime'], 
                event_data['eventLocation'], 
                community_center_ids[0][0],  # First community center ID
                community_center_ids[1][0]   # Second community center ID
            )
        )

        # Commit the transaction
        conn.commit()
        return jsonify({'message': 'Event created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/signIn/<fireBaseUID>', methods=["GET"])
def signIn(fireBaseUID):
    try:
        # Query the user table
        query_user = """
            SELECT * FROM
            STOlympics.Admin a
            WHERE a.AdminFireBaseID = %s
        """
        cursor.execute(query_user, (fireBaseUID,))
        user_row = cursor.fetchone()
        
        # If user is found, return user data
        if user_row:
            user_data = {
                'adminID': user_row[0],
                'adminEmail': user_row[1],
                'adminFirebaseID': user_row[2],
            }
            return jsonify({'data': user_data}), 200
        
        # If neither user nor admin is found, return "User not found" error
        return jsonify({'error': 'User not found'}), 404
        
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500

@app.route('/deleteEvent/<eventID>', methods=['DELETE'])
def deleteEvent(eventID):
    try:
        cursor = conn.cursor()
        sql = "DELETE FROM STOlympics.scheduled_events WHERE eventID = %s"
        cursor.execute(sql, (eventID,))
        conn.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
    

   

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
