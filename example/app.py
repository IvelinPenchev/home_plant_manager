from flask import Flask
import requests

app = Flask(__name__)

@app.route("/hi/<username>")
def greet(username):
    return f"Hello, {username}"

@app.route("/")
def home():
    return "Hello, world"

@app.route('/post', methods=['GET'])
def post_message_route_get():
    return show_post_message_form()

@app.route('/post', methods=['POST'])
def post_message_route_post():
    return post_message_to_site()

def show_post_message_form():
    return "Hello post form"

def post_message_to_site():
    return "Hello post to site"

