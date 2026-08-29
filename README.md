# PathFinder: AI-Powered Career Roadmap Generator

**🚀 [Live Demo: PathFinder AI on Streamlit](https://hcl-hackathon-pathfinder-gykvnhfffnsvkhnaynycfr.streamlit.app/)**

### What PathFinder AI is
PathFinder AI is a Generative AI career roadmap generator. 

### The Problem it Solves
It helps students and professionals figure out exactly what skills they need to learn for their target careers without getting overwhelmed. By automatically calculating skill gaps and dependencies, it provides a perfectly structured, chronological learning path.

### How it was Built
This project was built using **Streamlit** (for the interactive frontend), **Python** (for the core backend engine), **Groq LLM** (for ultra-fast AI reasoning and dynamic video chapter extraction), and **NetworkX** (for mathematical graph sorting of learning prerequisites).

## Repository Contents
This repository contains the core algorithmic engine, the Streamlit web application, and the AI integration layer.
- **Streamlit App (`app.py` & `ui/`)**: Contains the interactive chat interface and the visual dashboards for the PathFinder engine.
- **JSON Seed Files**: Act as the primary Knowledge Base (Layer 1) for career skills, aliases, and learning dependencies (e.g., `careers.json`, `prerequisites.json`).
- **`requirements.txt`**: Contains the precise Python dependencies required to deploy the engine on Streamlit Cloud.

## Key Features & Updates 
- **Interactive AI Skill Assessments**: Dynamically generates multi-format questions (MCQ vs Text) to accurately test the user's skill levels before building the roadmap.
- **AI-Powered Grading & Feedback**: The LLM grades user answers out of 100. It acts as an interactive mentor, providing customized feedback for partial credit so users understand exactly why they got a question wrong.
- **Conversational Intent Parsing**: The AI is context-aware. If a user says "I know Python but I want to learn from scratch," it intelligently ignores the known skills and drops them at the start of the roadmap.
- **Responsive Dashboard UI**: A fully custom-styled, dark-mode Streamlit UI with animated elements, a beautiful metric-driven sidebar, and responsive scaling.
- **Enterprise-Grade Concurrency**: Fully safe multi-user support via Streamlit `session_state` and a completely stateless backend LLM architecture, allowing hundreds of users to take assessments simultaneously.

## Data Processing Pipeline

This project employs a robust data processing pipeline to convert massive raw datasets into lightning-fast, production-ready assets:

1. **Raw Data Extraction**: The system initially ingests the massive O*NET 29.0 Database (containing hundreds of thousands of rows of career and skill data).
   - **Source**: [Kaggle O*NET 29.0 Database](https://www.kaggle.com/datasets/emarkhauser/onet-29-0-database)
2. **Data Cleaning & Preprocessing**: The raw datasets are heavily processed using `pandas` to remove noise, normalize career titles, and map complex skill relationships.
3. **Parquet Conversion**: The processed data is then compressed into highly efficient `.parquet` files for rapid, localized querying.
4. **JSON Distillation**: The most critical career relationships, aliases, and prerequisite graphs are further distilled into ultra-lightweight `.json` seed files (`careers.json`, `prerequisites.json`) which act as the primary Knowledge Base (Layer 1).

*Note: The raw datasets and massive preprocessed `.parquet` files are **deliberately excluded** from this GitHub repository to keep the deployment incredibly lightweight and fast. The Streamlit engine seamlessly falls back to the distilled JSON seed files and the Groq LLM API to operate efficiently in production without needing the heavy local files.*

## Core Engine Notebooks

The foundational logic, data engineering, and AI architecture for this project were initially developed and tested inside Jupyter Notebooks. These notebooks serve as the "brain" behind the application and can be found in the `notebooks/` directory of this repository.

1. **`notebooks/cleaning+preprocessing.ipynb`**:
   - **Purpose**: Handles the entire data engineering lifecycle.
   - **Details**: This notebook ingests the raw Kaggle O*NET dataset and performs extensive data cleaning using `pandas`. It normalizes career titles, maps skill proficiencies, removes noisy columns, and converts the heavy raw data into optimized `.parquet` and `.json` seed files used by the production app.

2. **`notebooks/pathfinder_ai.ipynb`**:
   - **Purpose**: The core logic engine and AI prototyping environment.
   - **Details**: This notebook contains the original implementation of the `PathFinderEngine`. It is where the mathematical skill gap calculation, `networkx` prerequisite graph sorting, and Groq LLM API integrations were meticulously built and tested before being ported into the Streamlit web architecture for deployment.

## How the System Works

  **The Core Architecture: Independent Tri-Layer System**
  The system orchestrates a resilient fallback architecture combining three distinct and separate pillars:
  1. **Hand-Curated Seed Files (`JSON/CSV`)**: Custom-generated baseline data (`careers.json`, `skills.json`, `resources.csv`, `dynamic_careers.json`, `dynamic_skills.json`, `prerequisites.json`).
  2. **Massive Curated Databases (`Datasets`)**: Deep background datasets (e.g., O*NET) for extensive querying.
  3. **Generative AI (`API`)**: Groq LLM API for dynamic reasoning and fallback.
  
  When a user requests a career roadmap, the engine first attempts to map it against the lightning-fast, custom curated JSON dictionaries. If more depth is needed, it queries extended datasets. Finally, if the career is entirely unknown or highly specialized, it securely calls the Groq API to dynamically generate the exact skills and video timestamps required on the fly, ensuring the system never fails to produce a highly personalized roadmap.

The PathFinder engine uses a strictly layered architecture to ensure speed, accuracy, and logical progression:
1. **Conversational AI Assistant**: Interfaces with the Groq API (Qwen model) to chat with the user, extract their intent (target career and existing skills) into structured JSON, and dynamically extract relevant video chapters for long crash courses.
2. **Knowledge Base & Skill Gap Engine**: 
   - Leverages a prioritized fallback system to resolve career requirements. It first checks the local JSON seed files using exact, alias, and partial matching.
3. **Skill Dependency Graph**: Uses graph theory (`networkx`) to map out the prerequisite order of missing skills (e.g., ensuring Mathematics is learned before Machine Learning), guaranteeing a logical roadmap.
4. **Recommendation & Adaptive Progress Engine**: Matches the identified missing skills with curated learning resources, scores them based on quality and difficulty, and compiles a final, actionable milestone-driven roadmap.

## Installation & Setup

To run this project locally, you must set up a Python virtual environment. The virtual environment files are deliberately excluded from version control (GitHub) to keep the repository lightweight and system-agnostic.

### 1. Create a Virtual Environment
Open your terminal in the root directory of the project and run the following command to create a virtual environment named `venv`:

**For Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
Once your virtual environment is successfully activated (you should see `(venv)` at the beginning of your terminal prompt), install the required packages using the provided requirements file:

```bash
pip install -r requirements.txt
```

### 3. Understanding `requirements.txt`
The `requirements.txt` file tracks all the third-party libraries needed for the engine to function. When you run the pip install command, it downloads:
- `pandas`: For advanced data manipulation and processing of the skill datasets.
- `networkx`: For building and traversing the Directed Acyclic Graphs (DAGs) used to calculate complex skill prerequisites.
- `groq`: The official Python client for interacting with the Groq API (powering the ultra-fast Qwen LLM inferences).
- `python-dotenv`: For securely loading API keys from a local `.env` file into the environment.
- `streamlit`: For building the interactive web UI and dashboards.

### 4. API Integration (Groq LLM)
This project utilizes the **Groq API** to power the Generative AI features of the application. The API is securely integrated into the Streamlit deployment to handle:
- Natural language intent extraction from user chat inputs.
- Dynamic generation of career paths for unknown/new careers (LLM Fallback).
- Automated extraction of relevant video timestamps from massive YouTube crash courses.

*(Note: The API key is securely managed within Streamlit Community Cloud Secrets and is not exposed in this repository).*

## Usage
1. Ensure your virtual environment is activated.
2. Launch the Streamlit web application from your terminal:
   ```bash
   streamlit run app.py
   ```
3. Open the provided localhost URL in your browser.
4. Chat with the AI to generate your personalized learning roadmap!
