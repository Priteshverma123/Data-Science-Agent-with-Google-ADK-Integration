# Data Analysis with Multiple Agents

## Agent Details
The key features of the Data Science Multi-Agent include:

| Feature | Description |
| --- | --- |
| **Interaction Type:** | Conversational |
| **Complexity:**  | Advanced |
| **Agent Type:**  | Multi Agent |
| **Components:**  | Tools, AgentTools, Session Memory, RAG |
| **Vertical:**  | All (Applicable across industries needing advanced data analysis) |

## Architecture Overview

The Data Science Multi-Agent System follows a sophisticated multi-layered architecture designed for comprehensive data analysis workflows:

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                          │
│                    (CLI / Web GUI)                            │
└─────────────────────┬───────────────────────────────────────────┘
                      │ User Query
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Orchestrator Agent                           │
│              (Main Coordination Layer)                         │
│  • Interprets user requests                                    │
│  • Routes queries to appropriate sub-agents                    │
│  • Coordinates multi-step workflows                           │
│  • Manages session memory and context                         │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Delegates Tasks
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Sub-Agent Layer                             │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Database Agent │  │Data Science Agent│  │   BQML Agent   │  │
│  │                 │  │                 │  │                 │  │
│  │ • NL2SQL        │  │ • NL2Python     │  │ • ML Training   │  │
│  │ • Query BigQuery│  │ • Data Analysis │  │ • Model Eval    │  │
│  │ • Data Retrieval│  │ • Visualization │  │ • RAG Enhanced  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────┬───────────────────────────────────────────┘
                      │ Executes Operations
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                         │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │    BigQuery     │  │ Code Interpreter│  │  Vertex AI RAG  │  │
│  │                 │  │                 │  │                 │  │
│  │ • SQL Execution │  │ • Python Runtime│  │ • BQML Reference│  │
│  │ • Data Storage  │  │ • Data Processing│  │ • Documentation │  │
│  │ • ML Models     │  │ • Visualization │  │ • Query Engine  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow Process

1. **User Query Reception**: User submits natural language query through CLI or Web GUI
2. **Orchestration**: Main orchestrator agent analyzes the query and determines the required workflow
3. **Task Delegation**: Based on query type, routes to appropriate sub-agent(s):
   - **Database queries** → Database Agent (NL2SQL translation)
   - **Data analysis/visualization** → Data Science Agent (NL2Python conversion)
   - **Machine learning tasks** → BQML Agent (ML model operations)
4. **Data Processing**: Sub-agents execute their specialized tasks
5. **Result Integration**: Orchestrator combines results from multiple agents if needed
6. **Response Generation**: Formatted response with data, visualizations, and explanations

### Agent Responsibilities

#### Orchestrator Agent
- **Primary Role**: Central coordination and workflow management
- **Capabilities**: 
  - Query interpretation and intent recognition
  - Multi-agent task coordination
  - Session state management
  - Result aggregation and formatting

#### Database Agent (NL2SQL)
- **Primary Role**: Natural language to SQL translation and database interaction
- **Capabilities**:
  - Converts natural language queries to SQL
  - Executes queries against BigQuery
  - Data extraction and initial processing
  - Schema understanding and query optimization

#### Data Science Agent (NL2Python)
- **Primary Role**: Data analysis and visualization
- **Capabilities**:
  - Python code generation from natural language
  - Statistical analysis and data manipulation
  - Chart and visualization generation
  - Data summarization and insights

#### BQML Agent
- **Primary Role**: Machine learning model management
- **Capabilities**:
  - BigQuery ML model training and evaluation
  - RAG-enhanced BQML documentation queries
  - Model recommendation and parameter tuning
  - ML workflow orchestration

### Key Features

*   **Multi-Agent Architecture:** Utilizes a top-level orchestrator that coordinates specialized sub-agents for different tasks
*   **Database Interaction (NL2SQL):** Employs a Database Agent to interact with BigQuery using natural language queries, translating them into SQL
*   **Data Science Analysis (NL2Python):** Includes a Data Science Agent that performs data analysis and visualization using Python, based on natural language instructions
*   **Machine Learning (BQML):** Features a BQML Agent that leverages BigQuery ML for training and evaluating machine learning models
*   **Code Interpreter Integration:** Supports the use of a Code Interpreter extension in Vertex AI for executing Python code, enabling complex data analysis and manipulation
*   **RAG Enhancement:** Uses Retrieval-Augmented Generation for BQML documentation and best practices
*   **ADK Web GUI:** Offers a user-friendly GUI interface for interacting with the agents
*   **Testability:** Includes a comprehensive test suite for ensuring the reliability of the agents

## Setup and Installation

### Prerequisites

*   **Google Cloud Account:** You need a Google Cloud account with BigQuery enabled
*   **Python 3.12+:** Ensure you have Python 3.12 or a later version installed
*   **uv:** Install uv by following the instructions on the official uv website: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
*   **Git:** Ensure you have git installed. If not, you can download it from [https://git-scm.com/](https://git-scm.com/) and follow the [installation guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

### Project Setup with uv

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/Priteshverma123/Data-Science-Agent-with-Google-ADK-Integration.git
    cd Data-Science-Agent-with-Google-ADK-Integration
    ```

2.  **Install Dependencies with uv:**

    ```bash
    uv sync
    ```

    This command reads the `pyproject.toml` file and installs all the necessary dependencies into a virtual environment managed by uv.

3.  **Activate the uv Environment:**

    ```bash
    source .venv/bin/activate
    ```

    Alternatively, you can run commands directly with uv without activating:

    ```bash
    uv run <command>
    ```

4.  **Set up Environment Variables:**
    Rename the file ".env.example" to ".env"
    Fill the below values:

    ```bash
    # Choose Model Backend: 0 -> ML Dev, 1 -> Vertex
    GOOGLE_GENAI_USE_VERTEXAI=1

    # ML Dev backend config. Fill if using Ml Dev backend.
    GOOGLE_API_KEY='YOUR_VALUE_HERE'

    # Vertex backend config
    GOOGLE_CLOUD_PROJECT='YOUR_VALUE_HERE'
    GOOGLE_CLOUD_LOCATION='YOUR_VALUE_HERE'
    ```

    Follow the following steps to set up the remaining environment variables.

5.  **BigQuery Setup:**
    These steps will load the sample data provided in this repository to BigQuery.
    For our sample use case, we are working on the Forecasting Sticker Sales data from Kaggle:

    _Walter Reade and Elizabeth Park. Forecasting Sticker Sales. https://kaggle.com/competitions/playground-series-s5e1, 2025. Kaggle._

    *   First, set the BigQuery project ID in the `.env` file. This can be the same GCP Project you use for `GOOGLE_CLOUD_PROJECT`,
        but you can use other BigQuery projects as well, as long as you have access permissions to that project.
        If you have an existing BigQuery table you wish to connect, specify the `BQ_DATASET_ID` in the `.env` file as well.
        Make sure you leave `BQ_DATASET_ID='forecasting_sticker_sales'` if you wish to use the sample data.

        Alternatively, you can set the variables from your terminal:

        ```bash
        export BQ_PROJECT_ID='YOUR-BQ-PROJECT-ID'
        export BQ_DATASET_ID='YOUR-DATASET-ID' # leave as 'forecasting_sticker_sales' if using sample data
        ```

        You can skip the upload steps if you are using your own data. We recommend not adding any production critical datasets to this sample agent.
        If you wish to use the sample data, continue with the next step.

    *   You will find the datasets inside 'data-science/data_science/utils/data/'.
        Make sure you are still in the working directory (`agents/data-science`). To load the test and train tables into BigQuery, run the following commands:
        ```bash
        uv run python data_science/utils/create_bq_table.py
        ```

6.  **BQML Setup:**
    The BQML Agent uses the Vertex AI RAG Engine to query the full BigQuery ML Reference Guide.

    Before running the setup, ensure your project ID is added in .env file: `"GOOGLE_CLOUD_PROJECT"`.
    Leave the corpus name empty in the .env file: `BQML_RAG_CORPUS_NAME = ''`. The corpus name will be added automatically once it's created.

    To set up the RAG Corpus for your project, run the methods `create_RAG_corpus()` and `ingest_files()` in
    `data-science/data_science/utils/reference_guide_RAG.py` by running the below command from the working directory:

    ```bash
    uv run python data_science/utils/reference_guide_RAG.py
    ```

7.  **Other Environment Variables:**

    *   `NL2SQL_METHOD`: (Optional) Either `BASELINE` or `CHASE`. Sets the method for SQL Generation. Baseline uses Gemini off-the-shelf, whereas CHASE uses [CHASE-SQL](https://arxiv.org/abs/2410.01943)
    *   `CODE_INTERPRETER_EXTENSION_NAME`: (Optional) The full resource name of
        a pre-existing Code Interpreter extension in Vertex AI. If not provided,
        a new extension will be created. (e.g.,
        `projects/<YOUR_PROJECT_ID>/locations/<YOUR_LOCATION>/extensions/<YOUR_EXTENSION_ID>`).
        Check the logs/terminal for the ID of the newly created Code Interpreter
        Extension and provide the value in your environment variables to avoid
        creating multiple extensions.

    From the terminal:

    ```bash
    export CODE_INTERPRETER_EXTENSION_NAME='projects/<YOUR_PROJECT_ID>/locations/us-central1/extensions/<YOUR_EXTENSION_ID>'
    ```

## Running the Agent

You can run the agent using the ADK command in your terminal.
from the working directory:

1.  **Run agent in CLI:**

    ```bash
    uv run adk run data_science
    ```

2.  **Run agent with ADK Web UI:**
    ```bash
    uv run adk web
    ```
    Select the data_science from the dropdown

### Example Agent Interaction

Here's a quick example of how a user might interact with the Data Science Multi-Agent System:

> **User:** Hi, What data do you have access to?

> **Agent:** I have access to two tables: `train` and `test`. Both tables contain sticker sales data with the following columns: `id`, `date`, `country`, `store`, `product`, and `num_sold`.

> **User:** I need more details on the train table. What countries exist? How many stores are there?

> **Agent:** Result: The train table contains data from Canada, Finland, Italy, Kenya, Norway, and Singapore. Each of these countries has 3 distinct stores.

> Explanation: The database agent executed a SQL query against the train table to find the distinct countries and the number of distinct stores within each country. The query grouped the results by country and counted the distinct store values.

> **User:** Please generate a plot with total sales per country.

> **Agent:** Result: A bar plot has been generated showing the total sales per country. The x-axis represents the country, and the y-axis represents the total sales.

> Explanation:
> 1. The database agent was first called to retrieve the total sales per country from the train table.
> 2. The data science agent was then called to generate a bar plot visualizing the results. The plot displays each country on the x-axis and its corresponding total sales on the y-axis.

> **User:** What kinds of forecasting models can I train in BQML?

> **Agent:** You can train several types of forecasting models in BQML, including ARIMA, Exponential Smoothing, and Temporal Fusion Transformer (TFT) models. Would you like to proceed with training a forecasting model?

> **User:** Yes

> **Agent:** Okay, before proceeding, let's confirm the project and dataset ID for BQML. We'll be using the `PROJECT_ID` project and the `forecasting_sticker_sales` dataset. Does that sound right?

> **User:** Yes

> **Agent:** The BQML supports `ARIMA_PLUS`, `ARIMA_PLUS_XREG`.

> To proceed, I need to know which model you'd like to use. I also need to know the following:
>
> *   The name of the column that provides the time points (e.g., 'date').
> *   The name of the column that contains the data to forecast (e.g., 'num_sold').
> *   Do you want to fit and forecast multiple time series using a single query? If so, what are the ID columns? (e.g., `country`, `store`, `product`)

## Benefits of Multi-Agent Architecture

- **Specialization**: Each agent focuses on its core competency (SQL, Python, ML)
- **Scalability**: Easy to add new specialized agents for different tasks
- **Maintainability**: Modular design allows independent updates to each agent
- **Flexibility**: Can handle complex workflows requiring multiple types of operations
- **Error Isolation**: Issues in one agent don't affect the entire system
- **Parallel Processing**: Multiple agents can work simultaneously on different aspects of a task