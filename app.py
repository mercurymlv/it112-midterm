from flask import Flask, render_template, redirect, url_for, request, session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField, EmailField, RadioField
from wtforms.validators import DataRequired, Length, Email
import secrets
import requests


app = Flask(__name__)

# use secrets to make a random key for security
app.secret_key = secrets.token_urlsafe(16)
# for the image on the confirmation page
UNSPLASH_ACCESS_KEY = "l50LB9b24njfWK6Yq9nFKYDX2fG0ho629H7m6ECzNgw"


# Initialize extensions
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)

# Function to reformat the form data
def first_cap(str):
    str = str.strip() # just a bit of cleanup
    if not str: # check if string is empty
        return ""
    return str.title()


class NameForm(FlaskForm):
    name = StringField('Please enter your name:', validators=[DataRequired(), Length(1, 40)])
    email = EmailField('Please enter your email:', validators=[DataRequired(), Email(), Length(1, 40)])
    # I wanted to try out a radio button and passing a value to another page that does something with it
    color = RadioField('Pick Your Fav Color:', choices=[('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('orange', 'Orange'), ('purple', 'Purple')], default='red', validators=[DataRequired()])
    submit = SubmitField('Submit')

# index/home page
@app.route('/')
def index():
    return render_template('index.html')

# Contact me page - this page has the form
# if form entries are valid, send "redirect" to a separate confirmation page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = NameForm()    
    if form.validate_on_submit():
        try:
            name = form.name.data
            email = form.email.data
            color = form.color.data

            name = first_cap(name)
            email = email.lower()
            color = first_cap(color)
            return redirect(url_for('confirmation', name=name, email=email, color=color))
        except Exception as e:
            print(f"Error processing form: {e}")
            return render_template('contact.html', form=form, error="Something went wrong. Please try again.")
    
    return render_template('contact.html', form=form)

# Confirmation page after submitting teh contact form, not in navbar
@app.route('/confirmation')
def confirmation():
    # "unknown" is if the value is missing
    name = request.args.get('name', 'Unknown')
    email = request.args.get('email', 'Unknown')
    color = request.args.get('color', 'Unknown')

    # Call Unsplash API to get an image that is related to the color choice
    image_url = ""  # Fallback if API fails
    # Some error handling so the site won't fail if we can't get an image
    try:
        response = requests.get(f"https://api.unsplash.com/photos/random?query={color}-color&client_id={UNSPLASH_ACCESS_KEY}", timeout=5)
        response.raise_for_status()  # Raise an error for bad status codes (4xx, 5xx)
        image_url = response.json().get("urls", {}).get("regular", "")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")  # error if API fails
    

    return render_template('confirmation.html', name=name, email=email, color=color, image_url=image_url)  # Pass image_url

# about page
@app.route('/about')
def about():
    return render_template('about.html')

# for debugging
if __name__ == '__main__':
    app.run(debug=True)
