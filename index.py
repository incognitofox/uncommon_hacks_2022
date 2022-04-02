from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', text='')

if __name__ == '__main__':
     app.run(port=8080)
