from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/<nome>')
def hello_world(nome=None):
    return render_template('teste.html', nome=nome)



if __name__ == '__main__':
    app.run()
