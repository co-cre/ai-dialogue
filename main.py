from logging import getLogger
logger = getLogger(__name__)

try:
    from app import app
    logger.info("Starting Flask application from main.py")

    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000, debug=True)
except Exception as e:
    logger.error(f"Failed to start application: {str(e)}")
    raise