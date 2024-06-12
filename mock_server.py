from flask import Flask, jsonify, abort

app = Flask(__name__)

def load_ids(filename):
    with open(filename, 'r') as f:
        return set(map(int, f.read().splitlines()))

active_ids = load_ids('active_ids.txt')
inactive_ids = load_ids('inactive_ids.txt')

@app.route('/<int:id>')
def get_page(id):
    if id in active_ids:
        return jsonify({"message": "This is a valid page", "id": id})
    elif id in inactive_ids:
        abort(404)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
