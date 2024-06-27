from flask import Flask, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import json

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process():
    if 'csvData' not in request.form or 'question' not in request.form:
        return jsonify({'error': 'CSV data or question not provided'}), 400

    # Deserialize the JSON string into a DataFrame
    csv_data_str = request.form['csvData']
    csv_data = json.loads(csv_data_str)
    df = pd.DataFrame(csv_data)

    # Get the question
    question = request.form['question']

    response = handle_question(question, df)

    return jsonify(response)

def handle_question(question, df):
    question = question.strip().lower()
    if 'line' in question:
        return generate_line_plot(df)
    elif 'scatter' in question:
        return generate_scatter_plot(df)
    elif 'dataframe' in question:
        return generate_dataframe_sample(df)
    elif 'top' in question or 'first' in question:
        return generate_n_rows(df, n=extract_number(question, default=5), position='top')
    elif 'tail' in question or 'last' in question:
        return generate_n_rows(df, n=extract_number(question, default=5), position='tail')
    elif 'row' in question or 'rows' in question or 'row count' in question or 'number of rows' in question:
        return get_row_count(df)
    elif 'column names' in question or 'columns name' in question or 'columns names' in question or 'column name' in question:
        return get_column_names(df)
    elif 'column' in question or 'columns' in question or 'number of columns' in question:
        return get_number_of_columns(df)
    else:
        return {'error': f'Unhandled question type: {question}'}

def generate_line_plot(df):
    # Generate a simple line plot
    plt.figure()
    sns.lineplot(data=df)
    return save_plot_to_base64()

def generate_scatter_plot(df):
    # Generate a simple scatter plot
    plt.figure()
    if len(df.columns) < 2:
        return {'error': 'Scatter plot requires at least 2 columns'}
    sns.scatterplot(x=df.columns[0], y=df.columns[1], data=df)
    return save_plot_to_base64()

def generate_dataframe_sample(df):    #correct
    return df.head().to_dict()

def generate_n_rows(df, n, position):   #correct
    if position == 'top':
        return df.head(n).to_dict()
    elif position == 'tail':
        return df.tail(n).to_dict()

def get_row_count(df):      #correct
    return {'Total number of rows': len(df)}

def get_number_of_columns(df):      #correct
    return {'Total number of columns': df.shape[1]}

def get_column_names(df):     #correct
    return {'Column names': df.columns.tolist()}

def save_plot_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close()
    return {'plot': img_base64}

def extract_number(question, default=5):
    words = question.split()
    for word in words:
        if word.isdigit():
            return int(word)
    return default

if __name__ == '__main__':
    app.run(port=5000)
