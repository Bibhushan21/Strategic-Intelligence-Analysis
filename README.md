# Strategic Intelligence App

A modern web application for strategic intelligence analysis, built with FastAPI and powered by advanced AI agents.

## Features

- **Best Practices Analysis**: Identify and analyze industry best practices
- **Scenario Planning**: Generate and evaluate strategic scenarios
- **Horizon Scanning**: Detect emerging trends and weak signals
- **Strategic Synthesis**: Combine insights into actionable intelligence
- **Modern UI**: Clean and intuitive user interface built with Tailwind CSS
- **RESTful API**: Well-documented API endpoints for integration

## Architecture

The application follows a modular architecture with the following components:

- **Agents**: Specialized AI agents for different types of analysis
- **Routers**: FastAPI routers for handling HTTP requests
- **Templates**: Jinja2 templates for rendering the UI
- **Data Storage**: JSON-based storage for projects and analysis results

## Getting Started

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/strategic-intelligence-app.git
cd strategic-intelligence-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

### Running the Application

1. Start the development server:
```bash
uvicorn app.main:app --reload
```

2. Open your browser and navigate to:
```
http://localhost:8000
```

## API Documentation

Once the application is running, you can access the API documentation at:
```
http://localhost:8000/docs
```

### Main Endpoints

- `GET /projects/`: List all projects
- `POST /projects/`: Create a new project
- `GET /agents/`: List all available agents
- `POST /agents/{agent_name}/process`: Process data with a specific agent
- `GET /analysis/`: List all analyses
- `POST /analysis/`: Create a new analysis

## Project Structure

```
strategic-intelligence-app/
├── app/
│   ├── agents/
│   │   ├── best_practices_agent.py
│   │   ├── scenario_planning_agent.py
│   │   ├── horizon_scan_agent.py
│   │   └── synthesis_agent.py
│   ├── routers/
│   │   ├── projects.py
│   │   ├── agents.py
│   │   └── analysis.py
│   ├── templates/
│   │   ├── projects.html
│   │   ├── agents.html
│   │   └── analysis.html
│   └── main.py
├── data/
│   ├── projects/
│   └── analysis/
├── requirements.txt
├── .env.example
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the web framework
- Tailwind CSS for the UI components
- OpenAI for the AI capabilities 