from flask import Blueprint, render_template
from models import User
from app import db

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return "Logged in!"
