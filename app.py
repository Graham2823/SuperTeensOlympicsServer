from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import mysql.connector
import csv
import io

app = Flask(__name__)
CORS(app)

# Define database configuration
db_config = {
    'user': 'admin',                       # MySQL username for AWS RDS
    'password': os.environ.get('MYSQL_PASSWORD'),  # MySQL password
    'host': 'stolympics.ctiwugy8azgr.us-east-2.rds.amazonaws.com',  # MySQL host for AWS RDS
    'port': 3306,                          # MySQL port
    'database': 'STOlympics'               # MySQL database name
}

# Helper function to get a new database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)
@app.route('/', methods=['GET'])
def home():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
                SELECT * 
FROM STOlympics.community_centers cc 
ORDER BY cc.community_centerPoints DESC, cc.community_centerName ASC;
            """
        cursor.execute(query)

        rows = cursor.fetchall()

        community_centers = []
        for row in rows:
            community_center_data = {
                "communityCenterName": row[1],
                "communityCenterPoints": row[2]
            }
            community_centers.append(community_center_data)

        return jsonify(community_centers)

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/getSchedule', methods=['GET'])
def getSchedule():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
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

        rows = cursor.fetchall()

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
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/eventsBySite/<siteName>', methods=['GET'])
def getEventsBySite(siteName):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

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

        rows = cursor.fetchall()

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
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/eventsByDate/<date>', methods=['GET'])
def getEventsByDate(date):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()


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

        rows = cursor.fetchall()

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
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/eventsByDateAndCenter/<date>/<center>', methods=['GET'])
def getEventsByDateAndCenter(date, center):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

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
        cursor.execute(query, (date, center, center))

        rows = cursor.fetchall()

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
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/createEvent', methods=['POST'])
def createEvent():
    conn = None
    cursor = None
    try:
        event_data = request.json

        conn = get_db_connection()
        cursor = conn.cursor()

        event_date = event_data['eventDate'].split('T')[0]

        cursor.execute("""
            SELECT community_centerID FROM STOlympics.community_centers 
            WHERE community_centerName = %s OR community_centerName = %s""",
            (event_data['eventCommunityCenter1ID'], event_data['eventCommunityCenter2ID'])
        )
        community_center_ids = cursor.fetchall()

        if len(community_center_ids) != 2:
            return jsonify({'error': 'Invalid community center names provided'}), 400

        cursor.execute("""
            INSERT INTO STOlympics.scheduled_events 
            (eventSport, eventDate, eventTime, eventLocation, communityCenter1ID, communityCenter2ID)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                event_data['eventSport'], 
                event_date,  
                event_data['eventTime'], 
                event_data['eventLocation'], 
                community_center_ids[0][0],  
                community_center_ids[1][0]   
            )
        )

        conn.commit()
        return jsonify({'message': 'Event created successfully'}), 201
    except mysql.connector.Error as e:
        if conn:
            conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/signIn/<fireBaseUID>', methods=["GET"])
def signIn(fireBaseUID):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query_user = """
            SELECT * FROM STOlympics.Admin a
            WHERE a.AdminFireBaseID = %s
        """
        cursor.execute(query_user, (fireBaseUID,))
        user_row = cursor.fetchone()

        if user_row:
            user_data = {
                'adminID': user_row[0],
                'adminEmail': user_row[1],
                'adminFirebaseID': user_row[2]
            }
            return jsonify(user_data)
        else:
            return jsonify({'message': 'User not found'}), 404

    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/deleteEvent/<eventID>', methods=['DELETE'])
def deleteEvent(eventID):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        sql = "DELETE FROM STOlympics.scheduled_events WHERE eventID = %s"
        cursor.execute(sql, (eventID,))
        conn.commit()
        return jsonify({'message': 'Event deleted successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/updatePoints/<communityCenterName>/<points>', methods=['POST'])
def update_points(communityCenterName, points):
    if not communityCenterName or points is None:
        return jsonify({'error': 'Missing communityCenterName or points'}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        update_query = """
        UPDATE STOlympics.community_centers
        SET community_centerPoints = %s
        WHERE community_centerName = %s
        """
        cursor.execute(update_query, (points, communityCenterName))
        conn.commit()

        return jsonify({'message': 'Points updated successfully'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500
    finally:
        cursor.close()
        conn.close()
@app.route('/downloadCSV/', methods=['GET'])
def download_csv():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
                SELECT * 
                FROM STOlympics.community_centers cc 
                ORDER BY cc.community_centerPoints DESC, cc.community_centerName ASC;
            """
        cursor.execute(query)

        rows = cursor.fetchall()

        # Prepare CSV data
        csv_data = []

        for row in rows:
            community_center_data = {
                "Community Center Name": row[1],
                "Community Center Points": row[2]
            }
            csv_data.append(community_center_data)

        # Create a string buffer to write CSV data
        csv_buffer = io.StringIO()

        # Get fieldnames from the first row of data
        if csv_data:
            fieldnames = csv_data[0].keys()
        else:
            fieldnames = []

        # Create a CSV writer
        writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)

        # Write header
        writer.writeheader()

        # Write participant information
        writer.writerows(csv_data)

        # Move the buffer cursor to the beginning
        csv_buffer.seek(0)

        # Create a Flask response with CSV content
        response = Response(
            csv_buffer.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=community_centers.csv'}
        )

        return response

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        return jsonify({'error': str(err)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
