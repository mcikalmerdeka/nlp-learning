# 📊 Agno Data Analyst Agent

An intelligent data analysis assistant powered by OpenAI and built with [Agno](https://github.com/agno-ai/agno). Upload CSV or Excel files and ask natural language questions to get instant insights, visualizations, and analysis.

## Features

- 🤖 **AI-Powered Analysis**: Uses GPT-4.1-mini to understand and answer complex data questions
- 📁 **Multi-Format Support**: Works with both CSV and Excel files
- 🔍 **Intelligent Preprocessing**: Automatic date parsing, numeric conversion, and data cleaning
- 💬 **Natural Language Interface**: Ask questions in plain English
- 📊 **Pandas Integration**: Leverages pandas for powerful data manipulation
- 🎨 **Clean UI**: Built with Streamlit for an intuitive user experience

## Installation

### Prerequisites

- Python 3.11 or higher
- OpenAI API key

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd agno-data-analyst-agent
```

2. Install dependencies using `uv` (recommended) or `pip`:

```bash
# Using uv
uv sync

# Or using pip
pip install -r requirements.txt
```

Dependencies include:
- `agno>=2.2.6` - AI agent framework
- `streamlit>=1.51.0` - Web interface
- `pandas>=2.3.3` - Data manipulation
- `openai>=2.6.1` - OpenAI API client
- `openpyxl>=3.1.5` - Excel file support
- `faker>=37.12.0` - Sample data generation

## Usage

### Running the App

1. Start the Streamlit app:
```bash
streamlit run main.py
```

2. Open your browser (usually at `http://localhost:8501`)

3. Enter your OpenAI API key in the sidebar

4. Upload a CSV or Excel file

5. Ask questions about your data in natural language

### Example Queries

- "What are the top 5 products by total sales?"
- "Show me the average salary by department"
- "Which region has the highest revenue?"
- "Calculate the correlation between experience and performance rating"
- "What's the distribution of order status?"

## Project Structure

```
agno-data-analyst-agent/
├── main.py                      # Streamlit app entry point
├── utils.py                     # File preprocessing utilities
├── random_data_generator.py     # Sample dataset generator
├── data/                        # Sample datasets
│   ├── sales_data.csv          # Sales transactions
│   ├── employee_data.csv       # Employee records
│   ├── employee_data.xlsx      # Employee records (Excel)
│   └── ecommerce_data.csv      # E-commerce orders
├── pyproject.toml              # Project dependencies
└── README.md                   # This file
```

## Generating Sample Data

The project includes a data generator script to create realistic sample datasets:

```bash
python random_data_generator.py
```

This generates three datasets:

### Sales Data (1000 records)
- Transaction ID, Date, Product, Category
- Quantity, Unit Price, Total Price
- Customer Name, Region, Sales Rep
- Payment Method, Discount Applied

### Employee Data (200 records)
- Employee ID, Name, Email
- Department, Position, Hire Date
- Salary, Age, City
- Years of Experience, Performance Rating

### E-commerce Data (500 records)
- Order ID, Order Date, Customer ID
- Product Name, Category, Price
- Quantity, Shipping Cost, Status
- Delivery Date, Rating

## How It Works

1. **File Upload**: Upload CSV or Excel files through the Streamlit interface

2. **Preprocessing**: The `preprocess_and_save()` function:
   - Detects and parses date columns
   - Converts numeric strings to numbers
   - Handles missing values
   - Properly quotes string fields

3. **Agent Initialization**: Creates an Agno agent with:
   - OpenAI GPT-4.1-mini model
   - PandasTools for dataframe operations
   - Pre-loaded context about your dataset

4. **Query Processing**: Your natural language queries are:
   - Interpreted by the AI agent
   - Converted to pandas operations
   - Executed on your data
   - Returned with clear insights

5. **Response Display**: Results are shown in both:
   - Streamlit UI with markdown formatting
   - Terminal output for detailed logs

## Configuration

### Model Selection

Change the model in `main.py`:

```python
model=OpenAIChat(id="gpt-4.1-mini", api_key=st.session_state.openai_key)
# Options: gpt-4, gpt-4-turbo, gpt-3.5-turbo, etc.
```

### Agent Instructions

Customize the agent's behavior by modifying the instructions list in `main.py`:

```python
instructions=[
    f"You are an expert data analyst.",
    # Add your custom instructions here
]
```

## Tips

- 💡 Check the terminal for clearer, formatted output
- 📊 The agent works best with structured, clean data
- 🔄 You can ask follow-up questions about the same dataset
- 🎯 Be specific in your queries for better results

## Troubleshooting

**"Please enter your OpenAI API key"**
- Enter a valid OpenAI API key in the sidebar

**"Error processing file"**
- Ensure your file is a valid CSV or Excel format
- Check for encoding issues in CSV files

**"Error generating response from the agent"**
- Verify your API key is correct
- Try rephrasing your query
- Check that column names in your query match the dataset

## License

MIT License (or your chosen license)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Built with [Agno](https://github.com/agno-ai/agno) AI agent framework
- Powered by [OpenAI](https://openai.com/) GPT models
- UI created with [Streamlit](https://streamlit.io/)

