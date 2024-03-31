from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from openai import OpenAI
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask import render_template
from flask import redirect
from flask import request




app = Flask(__name__)
app.secret_key = "x#a12"  # make sure this matches with that's in client_secret.json
app.config["MONGO_URI"] = "mongodb+srv://urop-mern-project:MRXbbqQ5ZuuzLDYh@cluster0.e99jww1.mongodb.net/smart-to-do?retryWrites=true&w=majority&appName=Cluster0"  # Replace with your MongoDB URI
mongo = PyMongo(app)
CORS(app)
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
@app.route('/')
def home():
    return render_template('homecheck.html')
@app.route('/autocompletepage')
def autocompletepage():
    return render_template('autofinish.html')

def get_related_words(line):
    try:
        # Use the Mistral model to predict the next two or three best tokens
        completion = client.chat.completions.create(
            model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q2_K.gguf",
            messages=[
                {"role": "system", "content": "You are a recommendation system Who is tailored in recommending the next suitable words based on the current input which can make the sentence look meaningful"},
                {"role": "user", "content": line},
            ],
            max_tokens=3,
            temperature=0.7,
        )

        # Extract the predicted tokens from the completion
        predicted_tokens = completion.choices[0].message.content.split()
        print("Predicted Tokens:", predicted_tokens)
        return predicted_tokens
    except Exception as e:
        print(e)
        return []
    
@app.route('/autocomplete/<line>', methods=['GET'])
def autocomplete(line):
    try:
        # Replace this with your actual "code" to get the related words
        related_words = get_related_words(line)
        return jsonify(related_words)
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while getting the related words"}), 500
    

@app.route('/backtohome')
def backtohome():
    return render_template('homecheck.html')
@app.route('/takenotes')
def takenotes():
    try:
        id = request.args.get('id', None)  # Get the id from the request's arguments
        if id is None:
            return render_template('newcheck.html')
        # Find the note with the provided ID
        note = mongo.db.notes.find_one({'_id': ObjectId(id)})
        if note:
            print("Note Found") 
            return render_template('newcheck.html', id=id, title=note['title'], content=note['content'])
        else:
            
            return jsonify({"error": "Note not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while retrieving the note"}), 500
def get_file_name(content):
    try:
        # Use the Mistral model to predict the next two or three best tokens
        completion = client.chat.completions.create(
            model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q2_K.gguf",
            messages=[
                {"role": "system", "content": "You are a recommendation system Who is tailored in recommending the file name in 2 to 3 words based on the current input which can make the file name look meaningful"},
                {"role": "user", "content": content},
            ],
            max_tokens=10,
            temperature=0.7,
        )

        # Extract the predicted tokens from the completion
        predicted_file = completion.choices[0].message.content
        return predicted_file
    except Exception as e:
        print(e)
        return ""
@app.route('/note_name',methods=['GET'])
def note_name():
    try:
        title = request.args.get('title', None)
        content = request.args.get('content', None)
        if title is None or content is None:
            return jsonify({"error": "Title or content not provided"}), 400
        file_name = get_file_name(content)
        return jsonify({"file_name": file_name})
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while generating the file name"}), 500
    

@app.route('/savenote', methods=['POST'])
def savenote():
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        id = data.get('id', "")
        print("ID:", id)
        if id == "":
            # No ID was sent, create a new note
            id = mongo.db.notes.insert_one({'title': title, 'content': content}).inserted_id
        else:
            # An ID was sent, update the existing note
            mongo.db.notes.update_one({'_id': ObjectId(id)}, {'$set': {'title': title, 'content': content}})
        return jsonify({"success": True, "id": str(id)})
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while saving the note"}), 500

@app.route('/deletenote', methods=['POST'])
def delete_note():
    try:
        data = request.get_json()
        id = data.get('id', '')
        result = mongo.db.notes.delete_one({'_id': ObjectId(id)})
        if result.deleted_count == 1:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "Note not found"}), 404
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while deleting the note"}), 500
@app.route('/getnotes', methods=['GET'])
def get_notes():
    try:
        notes = mongo.db.notes.find()
        result = []
        for note in notes:
            note['_id'] = str(note['_id'])  # Convert ObjectId to string
            result.append(note)
        return jsonify(result)
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while getting the notes"}), 500
from flask import jsonify


'''@app.route('/createnotes', methods=['POST'])
def create_note():
    try:
        data = request.get_json()
        title = data.get('title', '')
        content = data.get('content', '')
        mongo.db.notes.insert_one({'title': title, 'content': content})
        return redirect('/takenotes')
    except Exception as e:
        print(e)
        return jsonify({"error": "An error occurred while creating the note"}), 500
'''
def classify_bullet_points(bullet_points):
    bullet_points_text = bullet_points
    completion = client.chat.completions.create(
        model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q2_K.gguf",
        messages=[
            {"role": "system", "content": "You are personal assistant who is skilled in finding the tasks in the given bullet points_text. You need to convert each task into the following format: [<Task Name>,<Task Date>,<Task Time>,<Task Duration>]. If the given input is not a task then respond in the following manner: [<Not a Task>]"},
            {"role": "user", "content": bullet_points_text},
        ],
        temperature=0.7,
    )
    return str(completion.choices[0].message)  # Convert to string

def generate_notes(bullet_points):
    bullet_points_text = bullet_points
    completion = client.chat.completions.create(
        model="TheBloke/Mistral-7B-Instruct-v0.1-GGUF/mistral-7b-instruct-v0.1.Q2_K.gguf",
        messages=[
            {"role": "system", "content": "As a personal assistant skilled in note-taking, You excel in providing neatly organized notes based on the given bullet points_text. Each bullet point is meticulously addressed, with clear and concise reasoning provided in a structured format. Your expertise lies in understanding the context of the topic and crafting well-organized notes that meet the requirements of the task."},
            {"role": "user", "content": bullet_points_text},
        ],
        temperature=0.7,
    )
    return str(completion.choices[0].message.content)  # Convert to string

@app.route("/analyze", methods=["POST"])
def analyze_bullet_points():
    print("Request Received")
    data = request.json
    title = data.get("title")
    content = data.get("content")
    bullet_points = title+":"+content
    print("Bullet Points:", bullet_points)
    #print("Bullet Points:", bullet_points)
    if bullet_points:
        classification_result = generate_notes(bullet_points)
        #print("generate_notes Result:", classification_result)
        return jsonify({"result": classification_result})
    else:
        return jsonify({"error": "No content provided"}), 400




if __name__ == "__main__":
    app.run(debug=True)
