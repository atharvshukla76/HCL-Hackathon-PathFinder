# PathFinder: AI-Powered Career Roadmap Generator

PathFinder is an intelligent, interactive engine designed to generate highly personalized, step-by-step learning roadmaps for users transitioning into technology careers (such as Machine Learning Engineering, Data Science, etc.). 

By combining structured knowledge bases (like O*NET career profiles and curated seed data) with the reasoning capabilities of Open-Domain Large Language Models (via Groq), PathFinder accurately assesses an individual's skill gaps and generates a dynamic learning path containing recommended resources and dynamically extracted video timestamps.

## Repository Contents
**GitHub Repository**: [https://github.com/atharvshukla76/HCL-Hackathon-PathFinder](https://github.com/atharvshukla76/HCL-Hackathon-PathFinder)

This repository focuses on the core algorithmic engine, data processing, and AI integration, accessed via interactive Jupyter Notebooks.
- **Jupyter Notebooks**: Contain the interactive chat interface and the complete execution pipeline for the PathFinder engine.
- **JSON Seed Files**: Act as the primary Knowledge Base (Layer 1) for career skills, aliases, and learning dependencies (e.g., `careers.json`, `prerequisites.json`).
- **`requirements.txt`**: Contains the precise Python dependencies required to execute the engine.

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
- `jupyter`: To launch and run the interactive notebook environment.

### 4. Environment Variables
To evaluate this project, you (the user/judge) will need to create a local `.env` file in the root directory and provide your own API key for the LLM features to function:
```env
GROQ_API_KEY=<INSERT_YOUR_GROQ_API_KEY>
```
*(⚠️ SECURITY WARNING: This is just an example format for the judges! Never write your actual API key in this README or upload your `.env` file to GitHub. The person reviewing the code must provide their own key to test it locally.)*

## Usage
1. Ensure your virtual environment is activated.
2. Launch Jupyter Notebook from your terminal:
   ```bash
   jupyter notebook
   ```
3. Open the interactive notebooks from the browser interface.
4. Run the cells sequentially to initialize the engine, chat with the AI, and generate your personalized learning roadmap!
