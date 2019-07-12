# import app
from app import create_app

app = create_app()

if __name__ == '__main__':
    # run the app
    app.run(port=5000 or 80)
