from flask import Flask, render_template, request, jsonify, redirect
import subprocess
import sys
import json

app = Flask(__name__)


@app.route('/')
def index():
    return redirect('/1')


@app.route('/<problem_id>')
def problem(problem_id: int):
    # get json data from file from problems folder
    with open(f'problems/{problem_id}.json') as f:
        data = json.load(f)

    return render_template('index.html', problem=data)


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


# run app on port 7777
if __name__ == "__main__":
    app.run(port=7777, debug=True)

