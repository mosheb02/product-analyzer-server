# Product Analysis Multi-Agent System

A sophisticated multi-agent system built with CrewAI for comprehensive product analysis. The system uses multiple specialized AI agents to analyze products from different perspectives, including user reviews and company reliability.

## Features

- CrewAI-based agent orchestration
- Specialized agents for review and company analysis
- Integration with Google's Gemini Pro
- Custom web search and scraping tools
- FastAPI-based REST API

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
GOOGLE_API_KEY=your_api_key
SERPER_API_KEY=your_serper_api_key
```

4. Run the application:
```bash
uvicorn app.main:app --reload
```

## Project Structure

```
.
├── app/
│   ├── agents/
│   │   └── orchestrator.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   └── google_ai.py
│   ├── tools/
│   │   └── crew_tools.py
│   └── main.py
├── tests/
├── requirements.txt
└── README.md
```

## API Endpoints

- POST `/analyze-product`: Submit a product for analysis
- GET `/analysis/{analysis_id}`: Get analysis results

## License

MIT 