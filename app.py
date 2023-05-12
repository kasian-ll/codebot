from flask import Flask, render_template, request, jsonify, redirect
import subprocess
import sys
import json
import os
import openai
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv('OPENAI_API_KEY')


@app.route('/')
def index():
    # list throught all files from problems folder and get the json data
    problems = []
    for filename in os.listdir('problems'):
        with open(f'problems/{filename}') as f:
            data = json.load(f)
            data['id'] = filename.split('.')[0]
            problems.append(data)

    return render_template('index.html', problems=problems)


@app.route('/problem/<problem_id>')
def problem(problem_id: int):
    # get json data from file from problems folder
    with open(f'problems/{problem_id}.json') as f:
        data = json.load(f)
        data['id'] = problem_id

    return render_template('problem.html', problem=data)


@app.route('/submit_solution', methods=['POST'])
def submit_solution():
    # Extract data from request
    problem_id = request.json.get('problem_id')
    solution_code = request.json.get('solution_code')

    with open(f'problems/{problem_id}.json') as f:
        data = json.load(f)
    test_cases = data['tests']

    # Save the solution to a temporary Python file
    with open('solution.py', 'w') as f:
        f.write(solution_code)

    # Run the solution against each test case
    results = []
    for test_case in test_cases:
        try:
            # Run the solution with the test case input
            process = subprocess.run([sys.executable, 'solution.py'], input=test_case['input'], text=True, capture_output=True)

            # Check the output against the expected output
            if process.stdout.strip() == test_case['output']:
                results.append({'input': test_case['input'], 'passed': True})
            else:
                results.append({'input': test_case['input'], 'passed': False, 'actual_output': process.stdout.strip()})
        except Exception as e:
            results.append({'input': test_case['input'], 'passed': False, 'error': str(e)})

    # Return the results
    return jsonify(results)


@app.route('/api/chat', methods=['POST'])
def chat():
    chat_history = request.json.get('history')

    problem_id = request.json.get('problem_id')
    with open(f'problems/{problem_id}.json') as f:
        problem = json.load(f)

    user_code = request.json.get('code')

    print(chat_history)
    # Generate a response using GPT-3 chat models
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=chat_history
    )

    # Get the assistant's reply from the response
    assistant_reply = response['choices'][0]['message']['content']

    # Return the response
    return jsonify({'reply': assistant_reply})


# run app on port 7777
if __name__ == "__main__":
    app.run(port=7777, debug=True)

