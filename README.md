# InsightReview
Merchant Review Management System integrates DeepResearch-driven RAG, sentiment analysis, bot detection, and summarization to revolutionize review analysis. By leveraging advanced NLP and AI, it ensures precise sentiment detection, spam filtering, and insightful summarization

1. Install Dependencies
In the project root directory, use the following command to install the required Python dependencies:
```bash
pip install -r requirements.txt
```
3. Initialize Docker Compose (PostgreSQL)
The project uses Docker Compose to manage the PostgreSQL database. Ensure that you have installed Docker and Docker Compose, and then run the following command in the project root directory to start the PostgreSQL service:
```bash
docker-compose up -d
```
This will download and start the PostgreSQL container and store the data in the local postgres_data volume.

4. Initialize the Database
After starting the PostgreSQL service, you need to initialize the database table structure. You can write corresponding SQL scripts or use Python scripts to connect to the database and create the required tables.

5. Initialize Data
Import the review data into the PostgreSQL database. You can use the pandas library to read the data file and the psycopg2 library to insert the data into the database table. The sample code is as follows:
```python
运行
import pandas as pd
from server.database.postgres_client import PostgresClient

# Read the data file
data = pd.read_csv('path/to/your/data.csv')

# Initialize the database client
client = PostgresClient()

# Insert data into the database
client.insert_dataframe('your_table_name', data)
```
5. Process and Update Data
According to business requirements, regularly process and update the review data, such as recalculating sentiment scores and updating bot detection results.

6. Run the Frontend
Enter the frontend project directory, install the frontend dependencies, and start the development server:
```bash
cd system_code/server/fd/frontend
npm install
npm start
```
7. Run the Backend
In the project root directory, run the backend service:
```bash
python path/to/your/backend/server.py
```
8. Access the Website
Open your browser and visit http://localhost:3000 (the default port for the frontend) to enter the user interface of the InsightReview system.
