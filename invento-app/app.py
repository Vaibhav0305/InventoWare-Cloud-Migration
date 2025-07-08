from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    flash,
    g,
)
from flask_wtf.csrf import CSRFProtect, generate_csrf
import sqlite3
import os
import logging
import time
import traceback
import socket
from werkzeug.security import generate_password_hash, check_password_hash
from html import escape
from functools import wraps
import platform

app = Flask(__name__)
app.secret_key = os.urandom(32)  # Secure random key for production
app.config["PERMANENT_SESSION_LIFETIME"] = 1800  # 30 minutes session timeout
app.config["SESSION_PERMANENT"] = True

# Configure CSRF protection
csrf = CSRFProtect(app)


# Custom logging filter to provide default values for client_ip and user_id
class ContextFilter(logging.Filter):
    def filter(self, record):
        record.client_ip = getattr(record, "client_ip", "unknown")
        record.user_id = getattr(record, "user_id", "system")
        return True


# Configure logging with rotation
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("app.log", maxBytes=1000000, backupCount=5)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(handler)
logger.addFilter(ContextFilter())


# Session timeout decorator
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            log_message(logging.INFO, "Redirecting to login: No active session")
            return redirect(url_for("login"))
        if (
            "last_activity" in session
            and time.time() - session["last_activity"]
            > app.config["PERMANENT_SESSION_LIFETIME"]
        ):
            log_message(logging.INFO, f"Session timed out for user {g.user_id}")
            session.clear()
            flash("Session timed out. Please log in again.", "error")
            return redirect(url_for("login"))
        session["last_activity"] = time.time()
        return f(*args, **kwargs)

    return decorated_function


# Add request context to logging and log CSRF token
@app.before_request
def add_request_context():
    g.client_ip = request.remote_addr
    g.user_id = session.get("user_id", "anonymous")
    if request.method == "POST":
        log_message(
            logging.DEBUG, f"CSRF token in form: {request.form.get('csrf_token')}"
        )


def log_message(level, message):
    client_ip = getattr(g, "client_ip", "unknown")
    user_id = getattr(g, "user_id", "system")
    logger.log(
        level,
        f"{message} - IP:{client_ip} - User:{user_id}",
        extra={"client_ip": client_ip, "user_id": user_id},
    )


def is_file_locked(filepath):
    try:
        os.rename(filepath, filepath)
        return False
    except OSError:
        return True


def get_locking_process_info(filepath):
    """Attempt to identify processes locking the file (Windows only)."""
    if platform.system() != "Windows":
        return "Non-Windows platform: Use 'lsof' or similar tools to find locking processes."
    try:
        import psutil

        for proc in psutil.process_iter(["pid", "name", "open_files"]):
            try:
                if proc.info["open_files"]:
                    for file in proc.info["open_files"]:
                        if file.path.lower() == filepath.lower():
                            return f"Process: {proc.info['name']} (PID: {proc.info['pid']})"
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue
        return "No specific process identified. Check SQLite viewers, antivirus, or other Python instances."
    except ImportError:
        return "psutil not installed. Install with 'pip install psutil' or check manually with Resource Monitor."


def init_db(first=False, retries=3, delay=2):
    for attempt in range(retries):
        try:
            if not os.access(os.getcwd(), os.W_OK):
                log_message(logging.ERROR, "No write permission in current directory")
                raise PermissionError("No write permission in current directory")
            db_path = os.path.abspath("inventory.db")
            if first and os.path.exists(db_path):
                if is_file_locked(db_path):
                    process_info = get_locking_process_info(db_path)
                    log_message(
                        logging.WARNING,
                        f"Database file {db_path} is locked by another process: {process_info}. Attempting to use existing database.",
                    )
                    print(
                        f"Warning: {db_path} is locked by another process ({process_info}). Using existing database. Close any programs accessing it (e.g., SQLite viewers, antivirus)."
                    )
                    # Skip deletion and try using existing database
                else:
                    os.remove(db_path)
                    log_message(
                        logging.INFO, "Removed existing database for re-initialization"
                    )
            with sqlite3.connect(db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                c = conn.cursor()
                c.execute(
                    """CREATE TABLE IF NOT EXISTS inventory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        quantity INTEGER NOT NULL CHECK(quantity >= 0),
                        price REAL NOT NULL CHECK(price >= 0))"""
                )
                c.execute(
                    """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL CHECK(role IN ('admin', 'worker')))"""
                )
                c.execute(
                    """CREATE TABLE IF NOT EXISTS requests (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        item_name TEXT NOT NULL,
                        quantity INTEGER NOT NULL CHECK(quantity > 0),
                        status TEXT NOT NULL CHECK(status IN ('pending', 'approved', 'rejected')),
                        user_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id))"""
                )
                c.execute("SELECT COUNT(*) FROM inventory")
                if c.fetchone()[0] == 0:
                    initial_inventory = [
                        ("Steel Rods", 100, 99.99),
                        ("Copper Sheets", 50, 149.50),
                        ("Aluminum Pipes", 75, 75.25),
                    ]
                    c.executemany(
                        "INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)",
                        initial_inventory,
                    )
                    log_message(logging.INFO, "Initialized inventory with default data")
                c.execute("SELECT COUNT(*) FROM users")
                if c.fetchone()[0] == 0:
                    initial_users = [
                        ("admin", generate_password_hash("admin123"), "admin"),
                        ("worker1", generate_password_hash("worker123"), "worker"),
                        ("worker2", generate_password_hash("worker123"), "worker"),
                        ("worker3", generate_password_hash("worker123"), "worker"),
                    ]
                    c.executemany(
                        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                        initial_users,
                    )
                    log_message(logging.INFO, "Initialized users with default data")
                conn.commit()
            with sqlite3.connect(db_path) as conn:
                result = conn.execute("PRAGMA integrity_check").fetchone()[0]
                if result != "ok":
                    log_message(
                        logging.ERROR, f"Database integrity check failed: {result}"
                    )
                    raise sqlite3.DatabaseError(
                        f"Database integrity check failed: {result}"
                    )
            log_message(logging.INFO, "Database initialization completed successfully")
            return True
        except (sqlite3.Error, PermissionError, OSError) as e:
            log_message(
                logging.ERROR,
                f"Database initialization failed (attempt {attempt+1}/{retries}): {str(e)}",
            )
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise
    return False


def check_db_schema():
    try:
        with sqlite3.connect("inventory.db") as conn:
            c = conn.cursor()
            required_tables = ["inventory", "users", "requests"]
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in c.fetchall()]
            missing_tables = [
                table for table in required_tables if table not in existing_tables
            ]
            return missing_tables
    except sqlite3.Error as e:
        log_message(logging.ERROR, f"Table check failed: {str(e)}")
        return required_tables


def get_db_connection():
    try:
        conn = sqlite3.connect("inventory.db")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.row_factory = sqlite3.Row
        log_message(logging.DEBUG, "Database connection established")
        return conn
    except sqlite3.Error as e:
        log_message(logging.ERROR, f"Database connection failed: {str(e)}")
        return None


@app.errorhandler(500)
def internal_error(error):
    log_message(
        logging.ERROR, f"Internal server error: {str(error)}\n{traceback.format_exc()}"
    )
    return (
        render_template(
            "error.html", error_message="Internal server error. Please try again later."
        ),
        500,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    csrf_token = None
    conn = None
    if request.method == "POST":
        username = escape(request.form.get("username")).strip()
        password = request.form.get("password")
        role = request.form.get("role")
        if (
            not all([username, password, role])
            or role not in ["admin", "worker"]
            or len(username) > 50
        ):
            flash("Invalid or missing login details", "error")
            log_message(
                logging.WARNING, f"Invalid login attempt with username: {username}"
            )
            return render_template("login.html", csrf_token=csrf_token)
        conn = get_db_connection()
        if not conn:
            flash("Unable to connect to database.", "error")
            log_message(logging.ERROR, "Database connection failed")
            return render_template("login.html", csrf_token=csrf_token)
        try:
            with conn:
                c = conn.cursor()
                c.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
                )
                if not c.fetchone():
                    log_message(logging.ERROR, "Users table does not exist")
                    flash("Database setup error.", "error")
                    return render_template("login.html", csrf_token=csrf_token)
                c.execute("SELECT * FROM users WHERE username = ?", (username,))
                user = c.fetchone()
                if (
                    user
                    and check_password_hash(user["password"], password)
                    and user["role"] == role
                ):
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    session["role"] = user["role"]
                    session["last_activity"] = time.time()
                    log_message(logging.INFO, f"User {username} logged in as {role}")
                    return redirect(url_for("index"))
                flash("Invalid username, password, or role", "error")
                log_message(
                    logging.WARNING,
                    f"Failed login attempt for username: {username}, role: {role}",
                )
        except sqlite3.Error as e:
            log_message(logging.ERROR, f"Login query failed: {str(e)}")
            flash(f"Database error: {str(e)}.", "error")
        finally:
            if conn:
                conn.close()
    csrf_token = generate_csrf()
    return render_template("login.html", csrf_token=csrf_token)


@app.route("/logout", methods=["GET", "POST"])
def logout():
    user_id = session.get("user_id", "anonymous")
    session.clear()
    log_message(logging.INFO, f"User {user_id} logged out")
    return redirect(url_for("login"))


@app.route("/")
@require_login
def index():
    conn = get_db_connection()
    if not conn:
        log_message(logging.ERROR, "Failed to connect to database")
        flash("Unable to connect to database. Please try again later.", "error")
        return redirect(url_for("login"))
    try:
        with conn:
            c = conn.cursor()
            c.execute("SELECT * FROM inventory")
            inventory = {
                row["id"]: {
                    "name": row["name"],
                    "quantity": row["quantity"],
                    "price": row["price"],
                }
                for row in c.fetchall()
            }
            try:
                c.execute(
                    "SELECT r.*, u.username FROM requests r JOIN users u ON r.user_id = u.id"
                )
                requests = [
                    {
                        "id": row["id"],
                        "item_name": row["item_name"],
                        "quantity": row["quantity"],
                        "status": row["status"],
                        "username": row["username"],
                    }
                    for row in c.fetchall()
                ]
            except sqlite3.Error:
                requests = []
                log_message(
                    logging.WARNING, "Failed to fetch requests, returning empty list"
                )
    except sqlite3.Error as e:
        log_message(logging.ERROR, f"Database query failed in index: {str(e)}")
        flash("Error accessing database", "error")
        inventory = {}
        requests = []
    finally:
        conn.close()
    user_role = session.get("role", "worker")
    return render_template(
        "index.html", inventory=inventory, requests=requests, user_role=user_role
    )


@app.route("/items", methods=["POST"])
@require_login
def add_item():
    if session.get("role") != "admin":
        log_message(logging.WARNING, "Unauthorized attempt to add item")
        return jsonify({"error": "Unauthorized"}), 403
    name = escape(request.form.get("name")).strip()
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    if not all([name, quantity, price]) or len(name) > 100:
        log_message(logging.WARNING, "Missing or invalid fields for item addition")
        return jsonify({"error": "Missing or invalid fields"}), 400
    try:
        quantity = int(quantity)
        price = round(float(price), 2)  # Round to 2 decimal places
        if quantity < 0 or price < 0:
            log_message(
                logging.WARNING, f"Invalid quantity {quantity} or price {price}"
            )
            return jsonify({"error": "Quantity and price must be non-negative"}), 400
    except ValueError:
        log_message(
            logging.WARNING, f"Invalid input format: quantity={quantity}, price={price}"
        )
        return jsonify({"error": "Invalid quantity or price format"}), 400
    conn = get_db_connection()
    if not conn:
        log_message(logging.ERROR, "Database connection failed")
        return jsonify({"error": "Database error"}), 500
    try:
        with conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)",
                (name, quantity, price),
            )
            conn.commit()
            log_message(logging.INFO, f"Added item: {name}")
            flash("Item added successfully", "success")
            return redirect(url_for("index"))
    except sqlite3.Error as e:
        log_message(logging.ERROR, f"Item addition failed: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()


@app.route("/items/<int:item_id>/delete", methods=["POST"])
@require_login
def delete_item(item_id):
    if session.get("role") != "admin":
        log_message(
            logging.WARNING, f"Unauthorized attempt to delete item ID: {item_id}"
        )
        return jsonify({"error": "Unauthorized"}), 403
    conn = get_db_connection()
    if not conn:
        log_message(logging.ERROR, "Database connection failed")
        return jsonify({"error": "Database error"}), 500
    try:
        with conn:
            c = conn.cursor()
            c.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
            if c.rowcount == 0:
                log_message(logging.WARNING, f"Item ID {item_id} not found")
                return jsonify({"error": "Item not found"}), 404
            conn.commit()
            log_message(logging.INFO, f"Deleted item ID: {item_id}")
            flash("Item deleted successfully", "success")
            return redirect(url_for("index"))
    except sqlite3.Error as e:
        log_message(logging.ERROR, f"Item deletion failed for ID {item_id}: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()


@app.route("/requests", methods=["POST"])
@require_login
def add_request():
    if "user_id" not in session:
        log_message(logging.WARNING, "Unauthorized attempt to create request")
        return jsonify({"error": "Unauthorized"}), 403
    item_name = escape(request.form.get("item_name")).strip()
    quantity = request.form.get("quantity")
    if not all([item_name, quantity]) or len(item_name) > 100:
        log_message(logging.WARNING, "Missing or invalid fields for request")
        return jsonify({"error": "Missing or invalid fields"}), 400
    try:
        quantity = int(quantity)
        if quantity <= 0:
            log_message(logging.WARNING, f"Invalid quantity: {quantity}")
            return jsonify({"error": "Quantity must be positive"}), 400
    except ValueError:
        log_message(logging.WARNING, f"Invalid quantity format: {quantity}")
        return jsonify({"error": "Invalid quantity format"}), 400
    conn = get_db_connection()
    if not conn:
        log_message(logging.ERROR, "Database connection failed")
        return jsonify({"error": "Database error"}), 500
    try:
        with conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO requests (item_name, quantity, status, user_id) VALUES (?, ?, ?, ?)",
                (item_name, quantity, "pending", session["user_id"]),
            )
            conn.commit()
            log_message(logging.INFO, f"Added request for item: {item_name}")
            flash("Request submitted successfully", "success")
            return redirect(url_for("index"))
    except sqlite3.Error as e:
        log_message(logging.ERROR, f"Request addition failed: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        conn.close()


@app.route("/requests/<int:request_id>/<action>", methods=["POST"])
@require_login
def handle_request(request_id, action):
    if session.get("role") != "admin":
        log_message(
            logging.WARNING, f"Unauthorized attempt to {action} request ID {request_id}"
        )
        return jsonify({"error": "Unauthorized"}), 403
    action = action.lower()
    log_message(
        logging.DEBUG, f"Received action: {action} for request ID: {request_id}"
    )
    status_map = {"approve": "approved", "reject": "rejected"}
    if action not in status_map:
        log_message(logging.ERROR, f"Invalid action received: {action}")
        return jsonify({"error": "Invalid action"}), 400
    db_status = status_map[action]
    conn = get_db_connection()
    if not conn:
        log_message(logging.ERROR, "Database connection failed")
        return jsonify({"error": "Unable to connect to database"}), 500
    try:
        with conn:
            c = conn.cursor()
            c.execute(
                "SELECT item_name, quantity, user_id FROM requests WHERE id = ?",
                (request_id,),
            )
            req = c.fetchone()
            if not req:
                log_message(logging.ERROR, f"Request ID {request_id} not found")
                return jsonify({"error": "Request not found"}), 404
            c.execute("SELECT id FROM users WHERE id = ?", (req["user_id"],))
            if not c.fetchone():
                log_message(
                    logging.ERROR,
                    f"User ID {req['user_id']} not found for request ID {request_id}",
                )
                return jsonify({"error": "Invalid user ID for request"}), 400
            conn.execute("BEGIN")
            if action == "approve":
                price = request.form.get("price")
                if not price:
                    log_message(
                        logging.WARNING,
                        f"No price provided for request ID {request_id}",
                    )
                    return jsonify({"error": "Price is required for approval"}), 400
                try:
                    price = round(float(price), 2)  # Round to 2 decimal places
                    if price < 0:
                        log_message(logging.WARNING, f"Invalid price: {price}")
                        return jsonify({"error": "Price must be non-negative"}), 400
                except ValueError:
                    log_message(logging.WARNING, f"Invalid price format: {price}")
                    return jsonify({"error": "Invalid price format"}), 400
                c.execute(
                    "SELECT id, quantity FROM inventory WHERE name = ?",
                    (req["item_name"],),
                )
                item = c.fetchone()
                if item:
                    new_quantity = item["quantity"] + req["quantity"]
                    c.execute(
                        "UPDATE inventory SET quantity = ?, price = ? WHERE id = ?",
                        (new_quantity, price, item["id"]),
                    )
                    log_message(
                        logging.DEBUG,
                        f"Updated inventory item {req['item_name']} to quantity {new_quantity}, price ${price}",
                    )
                else:
                    c.execute(
                        "INSERT INTO inventory (name, quantity, price) VALUES (?, ?, ?)",
                        (req["item_name"], req["quantity"], price),
                    )
                    log_message(
                        logging.DEBUG,
                        f"Inserted new inventory item {req['item_name']} with price ${price}",
                    )
            c.execute(
                "UPDATE requests SET status = ? WHERE id = ?", (db_status, request_id)
            )
            conn.commit()
            log_message(logging.INFO, f"Request ID {request_id} {action}d successfully")
            flash(f"Request {action}d successfully", "success")
            return redirect(url_for("index"))
    except sqlite3.Error as e:
        conn.rollback()
        log_message(
            logging.ERROR,
            f"Request handling failed for ID {request_id}, action {action}: {str(e)}",
        )
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        conn.rollback()
        log_message(
            logging.ERROR,
            f"Unexpected error in request handling for ID {request_id}, action {action}: {str(e)}",
        )
        return jsonify({"error": "Unexpected server error"}), 500
    finally:
        conn.close()


def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


if __name__ == "__main__":
    with app.app_context():
        try:
            port = 5000
            if is_port_in_use(port):
                raise RuntimeError(
                    f"Port {port} is already in use. Close the process using it (e.g., run 'lsof -i :{port}' on Linux/Mac or 'netstat -aon' on Windows to find the process) or start the app with a different port (e.g., 'app.run(port=5001)')."
                )
            missing_tables = check_db_schema()
            if missing_tables or not os.path.exists("inventory.db"):
                log_message(
                    logging.INFO,
                    f"Missing tables: {', '.join(missing_tables)} or no DB file. Initializing database.",
                )
                if not init_db(first=True):
                    raise RuntimeError(
                        "Failed to initialize database after retries. Check if 'inventory.db' is locked by another process (e.g., Python, SQLite viewer, antivirus). Close locking processes or use the existing database by setting first=False in init_db."
                    )
            else:
                with sqlite3.connect("inventory.db") as conn:
                    result = conn.execute("PRAGMA integrity_check").fetchone()[0]
                    if result != "ok":
                        log_message(
                            logging.ERROR, f"Database integrity check failed: {result}"
                        )
                        raise sqlite3.DatabaseError(
                            f"Database integrity check failed: {result}"
                        )
                    conn.execute("PRAGMA foreign_keys = ON")
                    log_message(logging.INFO, "Database integrity verified")
            app.run(host="0.0.0.0", port=port, debug=False)
        except Exception as e:
            process_info = (
                get_locking_process_info(os.path.abspath("inventory.db"))
                if "locked" in str(e).lower()
                else ""
            )
            log_message(
                logging.ERROR,
                f"Application startup failed: {str(e)}\n{traceback.format_exc()}\n{process_info}",
            )
            print(
                f"Failed to start application: {str(e)}. Check app.log for details. If 'inventory.db' is locked, close processes accessing it ({process_info}). On Windows, use Resource Monitor or 'netstat -aon' to check. If port {port} is in use, close the conflicting process or use a different port."
            )
            
