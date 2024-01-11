# What's up, Duck? 
*A Web Application Healthcare Assistant Using Machine Learning Models*

## Project Description

In the growing landscape of digital health tools, "What's up, Duck?" is one of the aspiring and straightforward web applications that assist healthcare professionals in engaging with their diagnostics about the health conditions of their patients proactively. This work presents the development and functionalities of "What's up, Duck?" using the Python micro web framework, which is the Flask framework. At its core, the web application employs two machine learning models – Logistic regression and Linear regression – to address critical aspects of cardiovascular health. The first model estimates the likelihood of a patient developing a stroke disease based on inputted medical data, while the second predicts their cholesterol level. This gives users valuable insights into the risk factors and potential health outcomes. "What's up, Duck?" integrates interactive charts and visualizations to enhance user engagement and data comprehension. Bar charts depict predicted stroke probability, while line charts track predicted cholesterol levels by patients’ age. This visual representation of data empowers users to monitor their health trends according to age group and proactively seek medical guidance if needed. Furthering its practical utility, the web app seamlessly integrates data storage and retrieval capabilities. User inputs are securely stored in a MySQL database, allowing users to access their stored data through a readily accessible dashboard.

## Installation and Setup

Follow these steps to set up and install the project:

1. **Clone the repository**: Clone this repository to your local machine using `git clone https://github.com/Dioteng/ml-models-webapp.git`.

2. **Set up a virtual environment**: It's recommended to set up a virtual environment to isolate the project dependencies. You can do this with the following commands:

```bash
python -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
```

3. **Install the dependencies**: Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

4. **Set up the database**: Ensure that you have MySQL installed and running on your machine. Create a new database and update the SQLALCHEMY_DATABASE_URI configuration in the application with your database details.

5. **Import the dataset**: The project includes a CSV file in the `dataset` directory that you can use to populate your database. You can import this file into your MySQL database using the `LOAD DATA INFILE` command or a tool like phpMyAdmin. Here's an example of how you can do this with `LOAD DATA INFILE`:

```sql
LOAD DATA INFILE '/path/to/your/dataset/file.csv'
INTO TABLE your_table_name
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
```

6. **Run the application**: Start the Flask application with the following command:

```bash
flask run  # OR "python app.py"
```

The application will be available at http://localhost:5000.

## Usage

Once the application is running, you can use it to estimate the likelihood of a patient developing a stroke disease and predict their cholesterol level based on inputted medical data. The application provides interactive charts and visualizations, and stores user inputs in a MySQL database for future reference.