from flask import Blueprint, render_template, flash
from flask import request, redirect
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
import random
import requests
import pandas as pd
import torch
from model_training.model import ADNIModel
from model_training.dataset import ADNIDataset
from model_training.model_1_res.config_model_1 import *

from __init__ import create_app, db
from models import Users
from sqlalchemy import update

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method=='GET':
        return render_template('profile.html', current_user=current_user)
    else:
        if request.form.get('name'):
            name = request.form.get('name')
            email = request.form.get('email')
            stmt = (
                update(Users)
                .where(Users.id == current_user.id)
                .values(name=name, email=email)
                .execution_options(synchronize_session="fetch")
            )
            db.session.execute(stmt)
            db.session.commit()
        
        if request.form.get('password'):
            password = request.form.get('password')
            stmt = (
                update(Users)
                .where(Users.id == current_user.id)
                .values(password=generate_password_hash(password, method='sha256'))
                .execution_options(synchronize_session="fetch")
            )

            db.session.execute(stmt)
            db.session.commit()
        return redirect("/profile")

@main.route('/progression', methods=['POST', 'GET'])
@login_required
def progression():
    if request.method=='GET':
        return render_template('progression_profile.html', console="")

@main.route('/pred', methods=['POST'])
def pred():
    df = pd.read_json(request.text)
    df.plot(x='Months Since First Observation', y='ADAS-13 Measurement', kind='line')    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    bug.seek(0)

    image_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    model = ADNIModel(4, HIDDEN_SIZE, NUM_LAYERS, torch.device('cpu'))
    model.load_state_dict(torch.load('model_training/model_1_res/model.pt'))
    model.eval()

    dataset = ADNIDataset(df)
    data_loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    predictions = []
    with torch.no_grad():
        for batch in data_loader:
            X, y= batch['X'], batch['y']
            outputs = model(X)
            predictions.append(outputs.item()) 
     
    return render_template('results.html', image_data=image_data, pred=predictions[-1])

app = create_app()
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
