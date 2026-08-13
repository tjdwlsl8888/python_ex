from flask import Flask, render_template
from blueprints.member.routes import member_bp, app_bp
from blueprints.bank.routes import bank_bp 

app = Flask(__name__)
app.secret_key = 'interplanetaryNetworkKey'

app.register_blueprint(member_bp)
app.register_blueprint(app_bp)
app.register_blueprint(bank_bp)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


