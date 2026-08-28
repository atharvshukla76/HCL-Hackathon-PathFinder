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

## Data Sources
*Note: The raw datasets and preprocessed `.parquet` files are **not** included in this repository to keep it lightweight. The engine dynamically accesses them locally if present.*
- **Dataset Source**: [https://www.kaggle.com/datasets/emarkhauser/onet-29-0-database]

## How the System Works
The PathFinder engine uses a strictly layered architecture to ensure speed, accuracy, and logical progression:
1. **Conversational AI Assistant**: Interfaces with the Groq API (Qwen model) to chat with the user, extract their intent (target career and existing skills) into structured JSON, and dynamically extract relevant video chapters for long crash courses.
2. **Knowledge Base & Skill Gap Engine**: 
   - Leverages a prioritized fallback system to resolve career requirements. It first checks the local JSON seed files using exact, alias, and partial matching.
   - Once the career is resolved, it mathematically calculates the "gap" between the user's current proficiency and the career's required proficiency.
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

### 4. Environment Variables
To evaluate this project, you (the user/judge) will need to create a local `.env` file in the root directory and provide your own API key for the LLM features to function:
```env
GROQ_API_KEY=<INSERT_YOUR_GROQ_API_KEY>
```
*(⚠️ SECURITY WARNING: This is just an example format for the judges! Never write your actual API key in this README or upload your `.env` file to GitHub. The person reviewing the code must provide their own key to test it locally.)*

## Usage
1. Ensure your virtual environment is activated.
2. Launch the Streamlit web application from your terminal:
   ```bash
   streamlit run app.py
   ```
3. Open the provided localhost URL in your browser.
4. Chat with the AI to generate your personalized learning roadmap!
