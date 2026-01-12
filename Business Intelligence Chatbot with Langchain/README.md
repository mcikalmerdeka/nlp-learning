# Business Intelligence Chatbot with Langchain

![Project Header](https://raw.githubusercontent.com/mcikalmerdeka/NLP-Learning/refs/heads/main/Business%20Intelligence%20Chatbot%20with%20Langchain/assets/Project%20Header.jpg)

This repo is for using LLMs to chat with your SQL database. Inspired by this [Gemini Chatbot repo](https://github.com/ardyadipta/gemini_chatbot_sql). Instead of using MySQL I used PostgreSQL and instead of using Google Gemini model series, I experimented using OpenAI (GPT-4.1 and GPT-4o) and Anthropic (Claude 3.7 Sonnet and Claude Sonnet 4) models which I am more familiar with and `also later` wanted to try experiment with local models usage such as Deepseek-r1:1.5b and Qwen3:1.7b that is installed in my PC.

## 🎯 Objective and Project Origin

Around February 2025, I was quite curious if there was a way where we can retrieve data in a database without having to write sql queries, but only using natural language. So initially I tried to search online and the first thing I found was using a library called PandasAI. But there are major limitations on the usage limits in using the API on the free tier and upgrading to another tier costs way too much (around 200 euro per month as of May 2025). So I need to find another way to do database chat but with a more manageable cost and full control over the platform's behavior. But I couldn't find it at that time.

On April, when I was starting to learn about Langchain Framework from the beginning in a more structured way, I learned about the document loader method that can upload content from csv (haven't learned about chunking, embedding, or retrieval at that time) and immediately tried a brute force approach by calling the OpenAI and Anthropic models to analyze the data, and it turns out that it can understand simple lookup questions, but when it comes to data aggregation the model messed up quite bad. That was really dumb experimentation actually but it kinda gives an idea of how the behavior and limitations of the model are when trying to understand tabular data that is being transformed into text.

One month later, I watched the [conference talk](https://youtu.be/wN3T5NCTSAY?t=16827) from Ardya Dipta (Head of Data Science Kalbe Group) at DevFest Jakarta 2024 and was quite interested in trying the approach explained in the demo. The main idea is that the output of the LLM will actually be the SQL query, and how the LLM understand the our database is not by storing all the data per row (like how I did before) because in reality company data have millions of rows and several hundred of columns in total so this will burn out all the token usage fast and the cost will definitely explode. So instead, we just feed it with our database schema information and the secret strategy here is that the schema information need to be as complete as possible like from the column descriptions, relationship to other table in the database, data expected behaviour and example values in a column, and so on.

And in this project we will try to implement that approach.

## 📁 Project Structure

The project has been refactored with a professional, modular structure:

```
Business Intelligence Chatbot with Langchain/
│
├── src/
│   └── app/                           # Main application package
│       ├── __init__.py
│       │
│       ├── config/                    # Configuration and settings
│       │   ├── __init__.py
│       │   ├── settings.py            # App settings and environment variables
│       │   ├── models.py              # LLM model initialization
│       │   └── prompts/               # Prompt templates
│       │       ├── __init__.py
│       │       └── templates.py
│       │
│       ├── core/                      # Core business logic
│       │   ├── __init__.py
│       │   ├── database.py            # Database connection and queries
│       │   ├── llm_client.py          # LLM interaction handling
│       │   └── rag.py                 # RAG implementation for schema retrieval
│       │
│       ├── utils/                     # Utility scripts
│       │   ├── __init__.py
│       │   ├── database_setup_single_table.py
│       │   └── database_setup_multiple_tables.py
│       │
│       ├── db/                        # Database-related utilities
│       │   └── __init__.py
│       │
│       ├── app_single_basic.py        # Single table - Basic approach
│       ├── app_single_rag.py          # Single table - With RAG
│       ├── app_multi_basic.py         # Multiple tables - Basic approach
│       └── app_multi_rag.py           # Multiple tables - With RAG
│
├── datasets/
│   ├── dataset_single_table/          # Sales data CSV
│   └── dataset_multiple_tables/       # Olist e-commerce datasets
│
├── pyproject.toml
├── requirements.txt
├── .env
└── README.md
```

### Application Variants

**Single Table Approach** - Sales data analysis:

- `app_single_basic.py`: Simple approach with full schema loaded
- `app_single_rag.py`: RAG-enhanced (note: minimal benefit for single table)

**Multiple Tables Approach** - E-commerce (Olist) data analysis:

- `app_multi_basic.py`: Full schema loaded approach
- `app_multi_rag.py`: RAG-enhanced for better context retrieval

## 🚀 Features

- **Natural Language to SQL Conversion**: Convert plain English queries into SQL statements
- **RAG-Enhanced Architecture**: Uses retrieval-augmented generation to improve contextual understanding of database schema
- **Multi-Table Support**: Analyze data across multiple related tables (Olist e-commerce dataset)
- **Single Table Analysis**: Simpler analysis for sales data scenarios
- **Streamlit UI**: User-friendly interface for interacting with the database
- **Multiple LLM Support**: Compatible with OpenAI (GPT-4o, GPT-4.1), Anthropic (Claude 3.7 Sonnet, Claude Sonnet 4), and potential support for local models
- **Detailed Response Generation**: Formats query results into natural, conversational responses
- **Conversational Memory**: Maintains chat history to support follow-up questions and contextual conversations
- **Clear Chat Functionality**: Easily reset conversations with a "Clear Chat History" button in the sidebar
- **Chat Interface**: Modern chat-style UI for a more natural conversation experience

## 🔧 Setup and Installation

### Prerequisites

- Python 3.11+
- PostgreSQL database
- OpenAI API key and/or Anthropic API key

### Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/Business-Intelligence-Chatbot-with-Langchain.git
   cd Business-Intelligence-Chatbot-with-Langchain
   ```

2. Install dependencies:

   Using pip:

   ```
   pip install -e .
   ```

   Using uv package manager (recommended):

   ```
   uv pip install -e .
   ```

   Required dependencies (from pyproject.toml):

   - faiss-cpu>=1.11.0
   - langchain>=0.3.25
   - langchain-anthropic>=0.3.13
   - langchain-community>=0.3.24
   - langchain-openai>=0.3.16
   - numpy>=2.2.5
   - openai>=1.78.0
   - pandas>=2.2.3
   - psycopg2>=2.9.10
   - python-dotenv>=1.1.0
   - streamlit>=1.45.0

3. Create a `.env` file in the project root with your API and database credentials:

   ```
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   DB_USER=your_database_username
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=your_database_port
   ```

4. Set up the database:

   For single table approach:

   ```
   python src/app/utils/database_setup_single_table.py
   ```

   For multiple tables approach:

   ```
   python src/app/utils/database_setup_multiple_tables.py
   ```

## 💻 Usage

### Single Table Approach

1. Launch the application:

   Basic version (recommended):

   ```
   streamlit run src/app/app_single_basic.py
   ```

   Or with RAG:

   ```
   streamlit run src/app/app_single_rag.py
   ```

2. Access the application at `http://localhost:8501`
3. Configure your database connection in the sidebar
4. Start asking questions in natural language about your sales data!

Example queries for sales data:

- "What were the total sales in 2003 and 2004?"
- "Show me the top 5 customers by revenue"
- "What is the phone number of customer name Toys of Finland, Co.?"
- "Which product line has the highest average order value?"
- "What about for 2005?" (follow-up question example)
- "Which of them had the highest growth?" (contextual follow-up)

### Multiple Tables Approach

1. Launch the application:

   Basic version:

   ```
   streamlit run src/app/app_multi_basic.py
   ```

   Or with RAG (recommended for multi-table):

   ```
   streamlit run src/app/app_multi_rag.py
   ```

2. Access the application at `http://localhost:8501`
3. Configure your database connection in the sidebar
4. Start asking questions in natural language about the Olist e-commerce data!

Example queries for Olist e-commerce data:

- "What is the average monthly active user count for each year?"
- "Show me the number of customers who made more than one purchase (repeat orders) for each year!"
- "What are the top product categories by revenue per month?"
- "Displays detailed information on the amount of usage for each type of payment for each year!"
- "Which one showed the most significant increase?" (follow-up question)
- "Break down those results by customer location" (contextual follow-up)

## ⚙️ How It Works

### Without RAG (Basic Approach)

```mermaid
sequenceDiagram
    participant User
    participant Streamlit UI
    participant LLMClient
    participant Database

    User->>Streamlit UI: Submit natural language query
    Streamlit UI->>Streamlit UI: Load full schema description
    Streamlit UI->>LLMClient: Send query + full schema + chat history
    LLMClient->>LLMClient: Generate SQL query
    LLMClient-->>Streamlit UI: Return SQL query
    Streamlit UI->>Database: Execute SQL query
    Database-->>Streamlit UI: Return query results
    Streamlit UI->>LLMClient: Send results + question + history
    LLMClient->>LLMClient: Generate human-friendly response
    LLMClient-->>Streamlit UI: Return formatted response
    Streamlit UI-->>User: Display response
```

**Flow:**

1. User submits a natural language query
2. Full database schema is loaded from file/configuration
3. LLM converts query to SQL using complete schema information
4. SQL query is executed against the database
5. Results are passed back to LLM for human-friendly response generation
6. Conversation context is maintained for follow-up questions

### With RAG (Enhanced Approach)

```mermaid
sequenceDiagram
    participant User
    participant Streamlit UI
    participant RAGEngine
    participant FAISS Index
    participant LLMClient
    participant Database

    Note over RAGEngine,FAISS Index: Initialization Phase
    RAGEngine->>RAGEngine: Load schema description
    RAGEngine->>RAGEngine: Chunk schema into segments
    RAGEngine->>FAISS Index: Embed and store chunks

    Note over User,Database: Query Phase
    User->>Streamlit UI: Submit natural language query
    Streamlit UI->>RAGEngine: Request relevant schema
    RAGEngine->>FAISS Index: Similarity search (k=5)
    FAISS Index-->>RAGEngine: Return top 5 relevant chunks
    RAGEngine-->>Streamlit UI: Return retrieved schema
    Streamlit UI->>LLMClient: Send query + retrieved schema + history
    LLMClient->>LLMClient: Generate SQL query
    LLMClient-->>Streamlit UI: Return SQL query
    Streamlit UI->>Database: Execute SQL query
    Database-->>Streamlit UI: Return query results
    Streamlit UI->>LLMClient: Send results + question + history
    LLMClient->>LLMClient: Generate human-friendly response
    LLMClient-->>Streamlit UI: Return formatted response
    Streamlit UI-->>User: Display response
```

**Flow:**

1. **Initialization**: Database schema descriptions are embedded and stored in a FAISS vector index
2. User submits a natural language query
3. RAG engine retrieves only the most relevant schema chunks via similarity search
4. Context-enriched schema information is sent to LLM for SQL generation
5. Generated SQL is executed against the database
6. Results are formatted into natural language response
7. Chat history provides context for follow-up questions

**Key Difference**: RAG approach only sends relevant schema portions to the LLM, improving accuracy and reducing token usage for large schemas with multiple tables.

## 🔮 Future Improvements

- Support for more complex database schemas and relationships
- Integration with additional LLM providers and local models (Deepseek-r1:1.5b and Qwen3:1.7b)
- Advanced data visualization of query results
- Fine-tuning models for improved SQL generation accuracy
- Support for database operations beyond querying (e.g., inserts, updates)
- Enhanced conversation memory management for longer discussions
- User authentication and personalized query history

## 📧 Contact

For questions or feedback, please contact: mcikalmerdeka@gmail.com

## Project Screenshots

In this demo I used the multi-table approach using RAG implementation. The screenshots showcase how the Business Intelligence Chatbot interacts with a complex database schema using natural language processing and SQL generation capabilities.

### Database Connect, Initial Question, and Context Retrieval

![Part 1](./assets/Project%20Screenshot%201.png)

_The interface allows users to connect to their database and begin querying immediately. After establishing the connection, the system retrieves and processes the database schema information, allowing users to ask specific questions about the data in natural language without needing to write SQL queries manually._

### Query Generation and Model Response

![Part 2](./assets/Project%20Screenshot%202.png)
![Part 3](./assets/Project%20Screenshot%203.png)

_The AI assistant retrieves relevant schema context and automatically generates the appropriate SQL query based on the user's natural language question. The query is executed against the database, and results are returned in both raw format and a user-friendly interpretation. The LLM analyzes the query results and presents them with meaningful insights, transforming complex data into actionable business intelligence._

### Follow-up Question Capabilities

![Part 4](./assets/Project%20Screenshot%204.png)
![Part 5](./assets/Project%20Screenshot%205.png)

_The system implements conversational memory to maintain context between interactions, enabling natural follow-up questions. Users can ask for additional details, different breakdowns of the same data, or comparative analysis without repeating their original query context. This creates a more intuitive and efficient data exploration experience that mimics talking with a human data analyst._
