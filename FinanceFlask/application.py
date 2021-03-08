import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, Response
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    cash = db.execute("SELECT cash FROM users WHERE id=:user_id", user_id=session["user_id"])
    holdings = db.execute("SELECT symbol, shares FROM holdings WHERE user_id=:user_id", user_id=session["user_id"])
    holding = []
    together = 0.0

    for hold in holdings:
        p = (lookup(hold["symbol"])["price"])
        t = p*float(hold["shares"])

        item = dict(name=(lookup(hold["symbol"]))["name"], symbol=hold["symbol"], shares=hold["shares"], price= p, total = t)
        holding.append(item)
        together = together + t
    alltotal = float(cash[0]["cash"] + together)
    return render_template("index.html", cash=cash[0]["cash"], holding=holding, alltotal=alltotal)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("pls provide symbol", 400)
        if not request.form.get("shares"):
            return apology("pls provide shares amount", 400)
        try:
            i = int(request.form.get("shares"))
        except:
            return apology("shares must be positive integer", 400)
        if i <= 0:
            return apology("shares must be positive integer", 400)
        q = lookup(request.form.get("symbol"))
        if not q:
            return apology("couldn't retrive quote", 400)
        rows = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        cash = rows[0]["cash"]
        total = (q["price"] * float(request.form.get("shares")))
        if cash < total:
            return apology("you dont have enough cash")
        transaction = db.execute("INSERT INTO thistory (user_id, symbol, shares, price, total, typ) VALUES (:user_id, :symbol, :shares, :price, :total, :typ)",
                                 user_id=session["user_id"], symbol=request.form.get("symbol"), shares=request.form.get("shares"), price=q["price"], total= total, typ="buy")
        # check if user already owns shares of this company
        addingToExisting = db.execute("SELECT * FROM holdings WHERE symbol=:symbol AND user_id=:user_id",
                                      symbol=request.form.get("symbol"), user_id=session["user_id"])
        if transaction:
            if addingToExisting:
                toAdd = addingToExisting[0]["shares"]+int(request.form.get("shares"))
                db.execute("UPDATE holdings SET shares =:shares WHERE user_id=:user_id AND symbol=:symbol",
                           shares=toAdd, user_id=session["user_id"], symbol=request.form.get("symbol"))
            else:
                db.execute("INSERT INTO holdings (user_id, symbol, shares) VALUES(:user_id, :symbol, :shares)",
                           user_id=session["user_id"], symbol=request.form.get("symbol"), shares=request.form.get("shares"))
            # Deduct the money
            db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash=cash-total, user_id=session["user_id"])
            return redirect("/")
        else:
            return apology("couldn't finalise the transaction", 403)
    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    if len(username) >= 1:
        userExists = db.execute("SELECT * FROM users WHERE username=:username", username=username)
        if userExists:
            return jsonify(False), 200
        else:
            return jsonify(True), 200
    else:
        return jsonify(True), 200


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    h = db.execute("SELECT * FROM thistory WHERE user_id=:user_id", user_id=session["user_id"])
    history = []
    for his in h:
        n = lookup(his["symbol"])
        item = dict(date=his["timestamp"], name=n["name"], symbol=his["symbol"],
                    shares=his["shares"], price=his["price"], total=his["total"], typ=his["typ"])
        history.append(item)
    return render_template("history.html", history=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 400)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("Please provide Symbol", 400)
        q = lookup(request.form.get("symbol"))
        if not q:
            return apology("couldn't retrive quote", 400)

        return render_template("quoted.html", name=q["name"], price=float(q["price"]), symbol=q["symbol"])
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide password confirmation", 400)
        # Ensure password and confirmation match
        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("passwords don't match", 400)
        hash2 = generate_password_hash(request.form.get("password"))
        result = db.execute("INSERT INTO users (username, hash) VALUES(:username, :hash1)",
                            username=request.form.get("username"), hash1=hash2)
        if not result:
            return apology("not created", 400)
        else:
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              username=request.form.get("username"))
            session["user_id"] = rows[0]["id"]
            return redirect("/", 200)

    else:
        return render_template("register.html")


@app.route("/changepass", methods=["GET", "POST"])
@login_required
def changepass():
    """Changes user password"""
    if request.method == "POST":
        if not request.form.get("password"):
            return apology("provide new password")
        if not request.form.get("confirm"):
            return apology("provide confirmation")
        elif not (request.form.get("password") == request.form.get("confirm")):
            return apology("passwords don't match", 400)
        hash2 = generate_password_hash(request.form.get("password"))
        update = db.execute("UPDATE users SET hash=:hash1 WHERE id=:user_id",
                            hash1=hash2, user_id=session["user_id"])
        return redirect("/")
    else:
        return render_template("password.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("pls provide symbol", 400)
        if not request.form.get("shares"):
            return apology("pls provide shares amount", 400)
        q = lookup(request.form.get("symbol"))
        if not q:
            return apology("couldn't retrive quote", 400)
        total = (q["price"] * float(request.form.get("shares")))
        rows = db.execute("SELECT * FROM holdings WHERE user_id=:user_id AND symbol=:symbol",
                          user_id=session["user_id"], symbol=request.form.get("symbol"))
        user = db.execute("SELECT * FROM users WHERE id = :user_id", user_id=session["user_id"])
        cash = user[0]["cash"]
        if not rows:
            return apology("you dont own any shares of that company")
        if rows[0]["shares"] < int(request.form.get("shares")):
            return apology("you dont have enough shares")
        #transaction = db.execute("INSERT INTO thistory (user_id, symbol, shares, price, total, typ) VALUES (:user_id, :symbol, :shares, :price, :total, :typ)", user_id=session["user_id"], symbol=request.form.get("symbol"), shares=request.form.get("shares"), price=q["price"], total= total, typ="buy")
        sharesAfter = (rows[0]["shares"])-int(request.form.get("shares"))
        updateholdings = db.execute("UPDATE holdings SET shares =:shares WHERE user_id=:user_id AND symbol=:symbol",
                                    shares=sharesAfter, user_id=session["user_id"], symbol=request.form.get("symbol"))
        if not updateholdings:
            return apology("couldn't finalise the transaction", 400)
        # Deduct the money
        updatecash = db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash=cash+total, user_id=session["user_id"])
        if not updatecash:
            return apology("couldn't finalise the transaction", 400)
        updatehistory = db.execute("INSERT INTO thistory (user_id, symbol, shares, price, total, typ) VALUES (:user_id, :symbol, :shares, :price, :total, :typ)",
                                   user_id=session["user_id"], symbol=request.form.get("symbol"), shares=request.form.get("shares"), price=q["price"], total=total, typ="sell")
        # check last sql query if not reverse previous queries
        if not updatehistory:
            db.execute("UPDATE holdings SET shares =:shares WHERE user_id=:user_id AND symbol=:symbol",
                       shares=rows[0]["shares"], user_id=session["user_id"], symbol=request.form.get("symbol"))
            db.execute("UPDATE users SET cash = :cash WHERE id = :user_id", cash=cash, user_id=session["user_id"])
            return apology("couldn't finalise the transaction", 400)
        return redirect("/")

    else:
        holdings = db.execute("SELECT symbol FROM holdings WHERE user_id=:user_id", user_id=session["user_id"])
        symbols = []
        for s in holdings:
            symbols.append(s["symbol"])
        return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
