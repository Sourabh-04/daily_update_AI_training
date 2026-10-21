from flask import Flask, jsonify, request

app  = Flask(__name__)

students = [
{
"id": 1,
"name": "Rhea Kapoor",
"course": "Python",
"score": 82
},
{
"id": 2,
"name": "Zain Malik",
"course": "SQL",
"score": 76
},
{
"id": 3,
"name": "Devika Rao",
"course": "Cloud",
"score": 91
}
]
@app.route("/student",methods=['GET'])
def student():
    return jsonify(students)

@app.route("/student/<int:id>",methods=['GET'])
def student_id(id):
    for student in students:
        if student['id'] == id:
            return jsonify(student)
    return {'message':'Student not found'}

@app.route("/student",methods=['POST'])
def add_student():
    data = request.get_json()
    students.append(data)
    return jsonify({'message':'Student added'})

@app.route("/student/<int:id>",methods=['PUT'])
def update_student(id):
    data = request.get_json()
    for student in students:
        if int(student['id']) == id:
            student.update(data)
            return jsonify({'message':'Student updated'})

    return jsonify({'message':'Student not found'})


@app.route("/student/<int:id>",methods=['DELETE'])
def delete_student(id):
    for student in students:
        if int(student['id']) == id:
            students.remove(student)
            return jsonify({'message':'Student deleted'})
    return jsonify({'message':'Student not found'})

if __name__ == '__main__':
    app.run(debug=True)

