from flask import Flask, flash, render_template, request, redirect

app = Flask(__name__)
app.secret_key = "FDLA_PJL"

import FlaskWebProject1.views_alt
