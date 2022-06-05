Hej!!
Välkommen till Hyresbolagets hemsida.
Här kan du enkelt skapa en användare och logga in och börja hyra ut
garage och hyra andras garage!
För tillfället så kan du endast skriva till garageuthyrarna.

För kunna köra programmet behöver du ladda ned några bibliotek
och du gör det enklast genom ladda ner dom genom PIP
Du hämtar PIP här: https://pypi.org/project/pip/
Här kommer följande kommandon för att ladda ned dessa bibliotek;
**FLASK** ramverket för att kunna skapa funktioner och webbapplikationer
from flask import Flask, request, session, redirect, url_for, render_template, flash
**psycopg2** bibliotek för att kunna ansluta till en databas
import psycopg2 
import psycopg2.extras
**regular expression**  
import re 
**werkzeug** för att skapa ett WSGI (web server gateway interface)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
**os** för att kunna öppna upp och hämta objekt från mappar

import os







Webbsidan körs genom app.py