from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# Database configuration
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'gradetrackerdb'
DB_USER = 'postgres'
DB_PASSWORD = 'Shelley2010'

# Function to connect to the database


def connect_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Get all the available classes ---------------------------------------------------------------------------------------------
@app.route('/classes', methods=['GET'])
def get_classes():
    try:
        # Connect to the database
        connection = connect_db()

        # Create a cursor
        cursor = connection.cursor()

        # Retrieve all data from classes table
        query = "select * from classes order by class_year DESC"
        cursor.execute(query)

        # Check if there are any results
        if cursor.description is None:
            # No results, return an empty list
            data = []
        else:
            # Fetch all the results with labeled keys
            columns = [desc[0] for desc in cursor.description]
            data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert data to JSON and return
        return jsonify(data)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Get class by ID ----------------------------------------------------------------------------------------------------------
def map_grade_data(grade_data):
    # Define the labels for the grade data
    grade_labels = ['uuid', 'title', 'score', 'total', 'parent_uuid', 'date_added', 'date_due']

    # Map each tuple to a dictionary with labeled keys
    mapped_grades = [dict(zip(grade_labels, grade)) for grade in grade_data]

    return mapped_grades

@app.route('/class/<id>', methods=['GET'])
def get_class_by_id(id):
    try:
        # Connect to the database
        connection = connect_db()

        # Create a cursor
        cursor = connection.cursor()

        # Query to get class information
        query_class = "SELECT * FROM classes WHERE uuid=%s"
        cursor.execute(query_class, (id,))
        class_data = cursor.fetchone()

        if not class_data:
            return jsonify({'status': 'error', 'message': 'Class not found'}), 404

        # Query to get grade information
        query_grades = "SELECT * FROM grades WHERE parent_uuid=%s ORDER BY date_added DESC"
        cursor.execute(query_grades, (id,))
        grade_data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        data = {
            'class': {
                'uuid': class_data[0],
                'className': class_data[1],
                'year': class_data[2],
                'semester': class_data[3],
                'location': class_data[4],
                'professor': class_data[5],
                'gpa': class_data[6],
                'credits': class_data[7]
            },
            'grades': map_grade_data(grade_data)
        }

        # Convert data to JSON and return
        return jsonify(data)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Add a class
@app.route('/classes/add', methods=['POST'])
def add_class():
    try:
        # Get JSON data from the request body
        data = request.get_json()

        # Extract values from JSON data
        class_title = data.get('class_title')
        year = data.get('year')
        semester = data.get('semester')
        prof = data.get('prof')
        location = data.get('location')
        credits = data.get('credits')
        
        # Connect to the database
        connection = connect_db()

        # Create a cursor
        cursor = connection.cursor()

        # Use parameterized query to prevent SQL injection
        query = "insert into classes (class_title, class_year, semester, professor, location, credits) values (%s, %s, %s, %s, %s, %s);"
        cursor.execute(query, (class_title, year, semester, prof, location, credits))

        # Commit changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert data to JSON and return
        return jsonify({'status': 'success', 'message': 'Class added successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
    
# Add a assignment
@app.route('/class/<id>/add', methods=['POST'])
def add_assignment(id):
    try:
        # Get JSON data from the request body
        data = request.get_json()
        
        # Extract values from JSON data
        assignment_name = data.get('assignment_name')
        score = data.get('score')
        total_score = data.get('total_score')
        date_due = data.get('date_due')

        # Connect to the database
        connection = connect_db()

        # Create a cursor
        cursor = connection.cursor()

        # Use parameterized query to prevent SQL injection
        query = "insert into grades (title, score, total_score, parent_uuid, date_due) values (%s, %s, %s, %s, %s);"
        cursor.execute(query, (assignment_name, score, total_score, id, date_due))

        # Commit changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert data to JSON and return
        return jsonify({'status': 'success', 'message': 'Class added successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Get grades for a class
@app.route('/class/<id>/grades', methods=['GET'])
def get_class_grades(id):
    try:
        # Connect to the database
        connection = connect_db()

        # Create a cursor
        cursor = connection.cursor()

        # Example query: Retrieve all data from a table named 'grades'
        query = "SELECT * FROM grades WHERE parent_uuid=%s ORDER BY date_added DESC"
        cursor.execute(query, (id,))

        # Fetch all the results
        data = cursor.fetchall()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        data = map_grade_data(data)

        # Convert data to JSON and return
        return jsonify(data)

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    

# Update an assignment
@app.route('/updateAssignment/<grade_uuid>', methods=['POST'])
def update_assignment(grade_uuid):
    try:
        # Get JSON data from the request body
        data = request.get_json()
        
        # Extract values from JSON data
        assignment_name = data.get('assignment_name')
        score = data.get('score')
        total_score = data.get('total_score')
        date_due = data.get('date_due')

        # Connect to the database
        connection = connect_db()

        # Create a cursor
        cursor = connection.cursor()

        # Use parameterized query to prevent SQL injection
        query = """
        UPDATE grades
        SET title=%s, score=%s, total_score=%s, date_due=%s
        WHERE uuid=%s;
        """
        cursor.execute(query, (assignment_name, score, total_score, date_due, grade_uuid))

        # Commit changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert data to JSON and return
        return jsonify({'status': 'success', 'message': 'Assignment updated successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
# Remove an assignment
@app.route('/removeAssignment/<grade_uuid>', methods=['DELETE'])
def remove_assignment(grade_uuid):
    try:
        # Connect to the database
        connection = connect_db()

        # Create a cursor
        cursor = connection.cursor()

        # Use parameterized query to prevent SQL injection
        query = "DELETE FROM grades WHERE uuid = %s"
        cursor.execute(query, (grade_uuid,))

        # Commit changes to the database
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        # Convert data to JSON and return
        return jsonify({'status': 'success', 'message': 'Assignment deleted successfully'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
