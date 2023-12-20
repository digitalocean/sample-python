# PlanetIX PY service

This project is a Python Flask application hosted on Digital Ocean App Platform that fetches data from Google BigQuery and saves it to a MySQL server every two hours.

## Prerequisites

- Python 3.9 or higher
- A Google Cloud account with a valid service account JSON key file
- A MySQL server with the appropriate credentials

## Setup

### 1. Clone the repository

Clone the project repository from GitHub to your local machine:

```bash
git clone https://github.com/myusername/my-python-app.git
```
Create and activate a virtual environment

### 2. Navigate to the project directory and create a virtual environment:

```
cd my-python-app
python -m venv venv
```
Activate the virtual environment:

On Unix-based systems (Linux/macOS):

```source venv/bin/activate```

On Windows:

```venv\Scripts\activate.bat```
### 3. Install the dependencies
   Install the required dependencies using the requirements.txt file:
```pip install -r requirements.txt```

### 4.Set up the environment variables
   Create a .env file in the project root directory and populate it with the necessary environment variables:

```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-gcp-credentials.json
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_database_name
```

## Running the project locally
### Running the Flask application
Run the Flask application with the following command:

```python main.py```

The Flask application will start running, and you can access it at http://localhost:5000.


## Running the project with Docker
Build the Docker images
Build the Docker images for the Flask application and the script:


```
docker build -t my-python-app
docker build -t my-python-app-script -f Dockerfile.script .
```
Run the Docker containers
Run the Docker containers for the Flask application and the script:

```
docker run -p 8000:8000 --name my-python-app-instance my-python-app
docker run --name my-python-app-script-instance my-python-app-script
```

The Flask application will be accessible at http://localhost:8000.