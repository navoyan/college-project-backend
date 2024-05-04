## How to run the service locally

1. Install and run [MongoDB server](https://www.mongodb.com/try/download/community) or run Docker compose using compose file in the root of the project
2. Install [Python 3.11.x](https://www.python.org/downloads/release/python-3119/)
3. Install [Poetry](https://python-poetry.org/docs/#installation)
4. Install all project dependencies into venv using `poetry install --no-root`
5. Run the service using `poetry run uvicorn src.main:app`

You can access service's API documentation (Swagger) from a browser by navigating to `/docs` endpoint
