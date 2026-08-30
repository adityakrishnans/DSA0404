# Cricket Research Lab

Cricket Research Lab is a historical cricket analytics platform built to transform raw, ball-by-ball match data from the Cricsheet open dataset into a structured, queryable, and interactively explorable research environment.

## Architecture

The platform operates on a strict six-layer architecture:
1. Data Source Layer
2. Data Acquisition Layer
3. ETL Layer
4. Analytics Layer
5. Visualization Layer (Dashboard)
6. User Layer

The dataset boundary between ETL and Analytics guarantees reproducibility.

## Setup
1. Create a virtual environment: `python -m venv venv`
2. Activate the environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. Install dependencies: `pip install -r requirements.txt`

_Additional setup instructions (like data ingestion) will be added as implementation progresses._
