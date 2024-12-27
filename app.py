import os
import logging
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app first
app = Flask(__name__)

# Configure app
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Import models after db initialization
from models import Dialogue, Message
from ai_service import generate_personas, generate_dialogue

# Create tables within app context
def init_db():
    try:
        logger.info("Creating database tables...")
        with app.app_context():
            db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

# Initialize database
init_db()

@app.route("/")
def index():
    logger.debug("Rendering index page")
    return render_template("index.html")

@app.route("/start_dialogue", methods=["POST"])
def start_dialogue():
    theme = request.json.get("theme")
    if not theme:
        logger.warning("No theme provided in request")
        return jsonify({"error": "Theme is required"}), 400

    try:
        logger.info(f"Generating personas for theme: {theme}")
        personas = generate_personas(theme)

        logger.info("Creating new dialogue in database")
        dialogue = Dialogue(
            theme=theme,
            persona_a_name=personas["persona_a"]["name"],
            persona_b_name=personas["persona_b"]["name"],
            persona_a_description=personas["persona_a"]["description"],
            persona_b_description=personas["persona_b"]["description"],
            started_at=datetime.utcnow()
        )
        db.session.add(dialogue)
        db.session.commit()
        logger.info(f"Created dialogue with ID: {dialogue.id}")

        return jsonify({
            "dialogue_id": dialogue.id,
            "personas": personas
        })
    except Exception as e:
        logger.error(f"Error starting dialogue: {str(e)}")
        return jsonify({"error": "Failed to start dialogue"}), 500

@app.route("/generate_message", methods=["POST"])
def generate_message():
    dialogue_id = request.json.get("dialogue_id")
    last_messages = request.json.get("last_messages", [])
    current_speaker = request.json.get("current_speaker")

    logger.info(f"Generating message for dialogue {dialogue_id}, speaker: {current_speaker}")
    try:
        next_message = generate_dialogue(last_messages, current_speaker)

        message = Message(
            dialogue_id=dialogue_id,
            speaker=current_speaker,
            content=next_message,
            timestamp=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        logger.info(f"Saved message for dialogue {dialogue_id}")

        return jsonify({
            "message": next_message,
            "speaker": current_speaker
        })
    except Exception as e:
        logger.error(f"Error generating message: {str(e)}")
        return jsonify({"error": "Failed to generate message"}), 500

@app.route("/get_dialogue/<int:dialogue_id>")
def get_dialogue(dialogue_id):
    logger.info(f"Fetching dialogue {dialogue_id}")
    try:
        dialogue = Dialogue.query.get_or_404(dialogue_id)
        messages = Message.query.filter_by(dialogue_id=dialogue_id).order_by(Message.timestamp).all()

        return jsonify({
            "theme": dialogue.theme,
            "persona_a": {
                "name": dialogue.persona_a_name,
                "description": dialogue.persona_a_description
            },
            "persona_b": {
                "name": dialogue.persona_b_name,
                "description": dialogue.persona_b_description
            },
            "messages": [{
                "speaker": msg.speaker,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            } for msg in messages]
        })
    except Exception as e:
        logger.error(f"Error fetching dialogue {dialogue_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch dialogue"}), 500

if __name__ == "__main__":
    logger.info("Starting Flask application...")
    app.run(host="0.0.0.0", port=5000, debug=True)