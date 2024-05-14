from flask import Flask, render_template
from api import getEmails
import os

app = Flask(__name__)

@app.route('/')
async def index():
    return render_template('index.html')

@app.route('/authenticate')
async def authenticate():
    data= await getEmails()
    return render_template('predictions.html',data=data) 

@app.route('/logout')
async def logout():
    os.remove('token.pickle')
    return await index()

if __name__ == '__main__':
    app.run(debug=True)
