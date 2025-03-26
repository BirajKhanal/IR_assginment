# Project Documentation: How to Run the Project

## Prerequisites

Before running the project, ensure you have the following installed:

- **Python** 3.8+ (For running FastAPI and other Python dependencies)
- **PostgreSQL** (For the database)
- **pip** (For installing Python dependencies)

## 1. Setting Up the Environment

1. **Clone the Project**:
   
   ```bash
   git clone <project-repository-url>
   cd <project-directory>
   ```
2. **Create a Virtual Environment:** (optional but recommended)
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. **Install Dependencies:** Ensure all the required Python libraries are installed by running:
   
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a .env file:** Copy the contents of the .env.template file to a new .env file
   
   ```bash
   cp .env.template .env
   ```
   
   The .env file contains essential configuration like database connection details and other environment-specific variables. Edit it to match your setup.

## 2. Database Setup

1. **Database Creation**
   
   The application will automatically check if the database exists when it runs. If the database doesn't exist, it will be created.

   **Start the FastAPI Application:** In your project directory, run the following command to start the server
   
   ```bash
   uvicorn app.main:app --reload
   ```
   - app.main:app refers to the location of your FastAPI instance in your project (make sure it matches the file structure).
   - --reload allows auto-reloading of the server during development.
  
   **Database Connections**: The connection details (such as database URL, username, password, host and port) are stored in the .env file. The project reads these details to connect to the PostgreSQL database. The configuration might look like this in your .env file

   ```
   DB_NAME = ir_assignment
   DB_USER = 
   DB_PASS = 
   DB_HOST = 
   DB_PORT = 
   ```

   **Database Tables:** The application will also check if the required tables exist and create them automatically using SQLAlchemy ORM models. If they don’t exist, they will be created based on your model definitions.

2. **Restoring the Database** (Optional)
   
   If you have a database dump and wish to restore it, follow the steps below:

  - **Ensure PostgreSQL is running:** Make sure your PostgreSQL server is up and running.
  - **Restore the Database from Dump:** Assuming you have the database dump file (dump.sql), use the following command to restore it:
    
  ```bash
  psql -U <username> -d <database-name> --clean -f dump.sql
  ```

## 3. Running the Application
  **Start the FastAPI Application:** To run the FastAPI application, use the following command
  
  ```bash
  uvicorn app.main:app --reload
  ```

  **Access the API:** The FastAPI application will be running at http://127.0.0.1:8000. You can access the API or use the auto-generated documentation at:

  ```bash
  http://127.0.0.1:8000/docs
  ```

  **Useful docs urls**
  
  <img width="1482" alt="image" src="https://github.com/user-attachments/assets/f5325b4b-3b60-40fb-9cc8-2256705f579e" />

## 4. Additional Information

- **FastAPI Documentation**: Official documentation for FastAPI, used to build the backend API. [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- **BeautifulSoup Documentation**: Documentation for BeautifulSoup, used for web scraping. [https://www.crummy.com/software/BeautifulSoup/bs4/doc/](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- **PostgreSQL Full-Text Search Documentation**: Official PostgreSQL documentation for full-text search. [https://www.postgresql.org/docs/current/textsearch.html](https://www.postgresql.org/docs/current/textsearch.html)

### RSS Feed URLs

Here are the RSS feed URLs used for scraping news data for classification:

- **BBC Politics**: [https://feeds.bbci.co.uk/news/politics/rss.xml](https://feeds.bbci.co.uk/news/politics/rss.xml)
- **BBC Business**: [https://feeds.bbci.co.uk/news/business/rss.xml](https://feeds.bbci.co.uk/news/business/rss.xml)
- **BBC Health**: [https://feeds.bbci.co.uk/news/health/rss.xml](https://feeds.bbci.co.uk/news/health/rss.xml)

- **CNN Politics**: [http://rss.cnn.com/rss/cnn_allpolitics.rss](http://rss.cnn.com/rss/cnn_allpolitics.rss)
- **CNN Business**: [http://rss.cnn.com/rss/money_news_international.rss](http://rss.cnn.com/rss/money_news_international.rss)
- **CNN Health**: [http://rss.cnn.com/rss/cnn_health.rss](http://rss.cnn.com/rss/cnn_health.rss)

- **FOX Politics**: [https://moxie.foxnews.com/google-publisher/politics.xml](https://moxie.foxnews.com/google-publisher/politics.xml)
- **FOX Business**: [https://moxie.foxbusiness.com/google-publisher.xml](https://moxie.foxbusiness.com/google-publisher.xml)
- **FOX Health**: [https://moxie.foxnews.com/google-publisher/health.xml](https://moxie.foxnews.com/google-publisher/health.xml)


