# Strategic Intelligence App

A modern, AI-powered strategic intelligence analysis platform built with FastAPI and PostgreSQL. This comprehensive application provides advanced analytical capabilities with intelligent automation, smart templates, and sophisticated agent workflows for strategic decision-making.

## 🚀 Key Features

### **Core Analytics Platform**
- **9 Specialized AI Agents**: Advanced agent workflow for comprehensive strategic analysis
- **Real-time Streaming**: Live updates and progress tracking for long-running analyses
- **PostgreSQL Database**: Robust data storage with connection pooling and session tracking
- **PDF Report Generation**: Professional PDF reports with detailed formatting
- **Modern UI**: Clean, responsive interface built with Tailwind CSS and marked.js

### **🤖 AI-Powered Smart Template System**
- **Personalized Recommendations**: AI suggests templates based on your analysis history
- **Real-time Template Matching**: Intelligent suggestions as you type strategic questions
- **Save Analysis as Template**: Convert successful analyses into reusable templates
- **Usage-Based Learning**: System improves recommendations over time
- **Pattern Recognition**: Automatic domain and intent classification

### **⚡ Advanced Agent Workflow**
- **Orchestrator Agent**: Coordinates multi-agent workflows
- **Problem Explorer**: Deep-dive analysis of strategic challenges
- **Best Practices Agent**: Industry best practices identification
- **Horizon Scanning**: Emerging trends and weak signals detection
- **Scenario Planning**: Strategic scenario generation and evaluation
- **Research Synthesis**: Intelligent synthesis of multiple data sources
- **Strategic Action Planning**: Actionable strategic roadmaps
- **High Impact Initiatives**: Execution-ready implementation blueprints
- **Backcasting Agent**: Priority-based action item ranking

## 🏗️ Architecture

### **Technology Stack**
- **Backend**: FastAPI with Python 3.8+
- **Database**: PostgreSQL with SQLAlchemy 2.0+ and psycopg2-binary
- **AI Integration**: Mistral AI with LangChain framework
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS
- **PDF Generation**: ReportLab with advanced formatting
- **Real-time Features**: Server-sent events and WebSocket support

### **Database Schema**
- **Analysis Sessions**: Complete analysis tracking and storage
- **Agent Results**: Individual agent outputs and metadata
- **User Query Patterns**: Smart template learning and analytics
- **Analysis Templates**: Reusable template library
- **User Generated Templates**: Custom templates from successful analyses

### **Agent Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Orchestrator   │───▶│ Problem Explorer │───▶│ Best Practices  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Horizon Scanning│───▶│ Scenario Planning│───▶│Research Synthesis│
└─────────────────┘    └─────────────────┘    └─────────────────┘
          │                       │                       │
          ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│Strategic Action │───▶│ High Impact     │───▶│   Backcasting   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Getting Started

### **Prerequisites**
- Python 3.8 or higher
- PostgreSQL 12+ (not SQLite)
- pip (Python package manager)
- Virtual environment (recommended)

### **Installation**

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/strategic-intelligence-app.git
cd strategic-intelligence-app
```

2. **Create and activate virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your configuration:
# - MISTRAL_API_KEY=your_mistral_api_key
# - DATABASE_URL=postgresql://user:password@localhost/dbname
```

5. **Set up PostgreSQL database:**
```sql
-- Create database
CREATE DATABASE strategic_intelligence;

-- The application will automatically create tables on first run
```

### **Running the Application**

1. **Start the development server:**
```bash
uvicorn app.main:app --reload
```

2. **Access the application:**
```
http://localhost:8000
```

3. **API Documentation:**
```
http://localhost:8000/docs
```

## 📊 Smart Template System

### **How It Works**
The AI-powered template system learns from your analysis patterns to provide personalized suggestions:

1. **Pattern Tracking**: Every analysis builds your behavioral profile
2. **Domain Classification**: Automatic categorization (Market, Technology, Risk, etc.)
3. **Intent Recognition**: Identifies analysis purpose (Market Entry, Competitive Analysis, etc.)
4. **Smart Suggestions**: AI generates relevant templates based on your history
5. **Real-time Recommendations**: Templates appear as you type strategic questions

### **Key Features**
- **🎯 Personalized AI Suggestions**: Based on your unique analysis patterns
- **⚡ Real-time Recommendations**: Intelligent matching as you type
- **💾 Save Analysis as Template**: Convert successful analyses into reusable templates
- **📊 Usage Analytics**: Track patterns and improve recommendations
- **🧠 Continuous Learning**: System gets smarter with every use

### **Domain Classification**
- **Market**: Customer, competitor, market analysis
- **Technology**: Digital transformation, AI, innovation
- **Finance**: Investment, budget, ROI analysis
- **Risk**: Security, compliance, threat assessment
- **Strategy**: Planning, vision, direction
- **Operations**: Process, efficiency, supply chain
- **Geopolitical**: Regulatory, policy, regional analysis

## 🔧 API Reference

### **Core Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/start-analysis` | POST | Start a new strategic analysis |
| `/analysis-status/{session_id}` | GET | Check analysis progress |
| `/analysis-results/{session_id}` | GET | Get complete analysis results |
| `/generate-pdf` | POST | Generate PDF report |

### **Smart Template Endpoints**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai-template-suggestions/{user_id}` | GET | Get personalized AI suggestions |
| `/api/get-template-recommendations` | POST | Get real-time template recommendations |
| `/api/save-analysis-as-template` | POST | Save analysis as reusable template |
| `/api/track-query-pattern` | POST | Track user query patterns |
| `/api/user-analytics/{user_id}` | GET | Get user behavior analytics |
| `/api/popular-query-patterns` | GET | Get trending analysis patterns |

### **Agent Management**
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/agents` | GET | List all available agents |
| `/agents/{agent_name}/process` | POST | Process data with specific agent |
| `/agent-status` | GET | Get agent health and status |

## 📁 Project Structure

```
strategic-intelligence-app/
├── app/
│   ├── agents/                    # AI Agents
│   │   ├── base_agent.py         # Base agent class
│   │   ├── orchestrator_agent.py # Workflow coordination
│   │   ├── problem_explorer_agent.py
│   │   ├── best_practices_agent.py
│   │   ├── horizon_scan_agent.py
│   │   ├── scenario_planning_agent.py
│   │   ├── research_synthesis_agent.py
│   │   ├── strategic_action_agent.py
│   │   ├── high_impact_agent.py
│   │   └── backcasting_agent.py
│   ├── database/                  # Database layer
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── database.py           # Database connection
│   │   └── database_service.py   # Business logic
│   ├── static/                   # Frontend assets
│   │   ├── css/main.css         # Tailwind CSS styles
│   │   └── js/analysis.js       # JavaScript functionality
│   ├── templates/               # HTML templates
│   │   └── analysis.html        # Main interface
│   └── main.py                  # FastAPI application
├── data/                        # Data storage
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── run.py                      # Application runner
└── README.md                   # This file
```

## 🎯 Agent Details

### **High Impact Agent**
Creates exactly **3 comprehensive initiatives**:
- **Near-Term Initiative**: 0-2 years, immediate strategic actions
- **Medium-Term Initiative**: 2-5 years, strategic positioning
- **Long-Term Initiative**: 5-10 years, transformational changes

Each initiative includes:
- Descriptive title based on actual high-priority actions
- Strategic importance explanation
- Stakeholder impact analysis
- Resource requirements estimation
- Success metrics (3+ indicators)
- Immediate implementation tasks (5 tasks)

### **Strategic Action Agent**
Generates comprehensive action plans with:
- **Structured parsing** of strategic ideas
- **Priority classification** (High/Medium/Low)
- **Time horizon organization** (Near/Medium/Long-term)
- **Action item extraction** with detailed descriptions
- **Enhanced parsing patterns** for accurate content extraction

### **Backcasting Agent**
Prioritizes action items using:
- **Urgency assessment** (immediate impact)
- **Impact evaluation** (strategic value)
- **Feasibility analysis** (implementation difficulty)
- **JSON-structured output** with rankings and justifications

## 🔧 Recent Major Fixes

### **PDF Generation (✅ Fixed)**
- **Issue**: 500 Internal Server Error when generating PDFs
- **Root Cause**: Missing ReportLab imports (`A4`, `colors`)
- **Solution**: Added proper imports and enhanced error handling
- **Status**: ✅ Working perfectly - generates professional PDF reports

### **High Impact Agent (✅ Fixed)**
- **Issue**: Generic output with only 1 initiative showing
- **Root Cause**: Parsing issues and incorrect data flow
- **Solution**: Fixed data extraction, parsing logic, and output formatting
- **Status**: ✅ Creates exactly 3 meaningful initiatives per time horizon

### **Agent Data Flow (✅ Fixed)**
- **Issue**: Agents not finding high-priority items
- **Root Cause**: Strategic Action Agent parsing and status handling
- **Solution**: Enhanced parsing patterns and proper status returns
- **Status**: ✅ All agents communicate properly with structured data

## 📊 Performance Analytics

### **System Capabilities**
- **Processing Speed**: Handles complex multi-agent workflows in 60-120 seconds
- **Scalability**: PostgreSQL backend supports concurrent users
- **Reliability**: Comprehensive error handling with graceful fallbacks
- **Learning**: Template system improves with usage patterns

### **Usage Metrics**
- **Template Suggestions**: AI-generated based on behavioral patterns
- **Pattern Recognition**: Automatic domain and intent classification
- **Success Tracking**: Analysis completion rates and template reuse
- **Performance Monitoring**: Agent response times and success rates

## 🔮 Future Enhancements

### **Planned Features**
- **🌐 Multi-user Collaboration**: Team workspaces and shared templates
- **📱 Mobile Optimization**: Responsive design for mobile devices
- **🔗 External Integrations**: API connectors for data sources
- **📊 Advanced Analytics**: Deeper insights and trend analysis
- **🤖 Enhanced AI Models**: More sophisticated prediction algorithms

### **AI Improvements**
- **Natural Language Processing**: Better question understanding
- **Predictive Analytics**: Proactive strategic suggestions
- **Multi-language Support**: Global accessibility
- **Advanced Learning**: Cross-user pattern recognition (privacy-protected)

## 🛡️ Security & Privacy

- **Data Encryption**: Sensitive information protection
- **Anonymous Tracking**: Privacy-first analytics approach
- **User Consent**: Opt-in data collection policies
- **Secure APIs**: Authentication and authorization controls
- **Database Security**: PostgreSQL security best practices

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes** with proper testing
4. **Commit your changes**: `git commit -am 'Add feature'`
5. **Push to the branch**: `git push origin feature-name`
6. **Submit a pull request**

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation for changes
- Ensure PostgreSQL compatibility

## 📞 Support

### **Common Issues**
- **Database Connection**: Ensure PostgreSQL is running and credentials are correct
- **Agent Timeouts**: Check Mistral API key and network connectivity
- **PDF Generation**: Verify ReportLab installation and imports
- **Template System**: Clear browser cache for JavaScript updates

### **Getting Help**
- **Technical Issues**: Check application logs and console output
- **Feature Requests**: Submit through GitHub issues
- **Documentation**: Refer to API docs at `/docs`
- **Community**: Join developer discussions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Powerful, open-source relational database
- **Mistral AI**: Advanced language model capabilities
- **Tailwind CSS**: Utility-first CSS framework
- **ReportLab**: Professional PDF generation
- **SQLAlchemy**: Python SQL toolkit and ORM

---

**🎉 Your Strategic Intelligence App is ready to transform decision-making with AI-powered insights and intelligent automation!**

**🌐 Access at: http://localhost:8000**

## Features

- **Multi-Agent Strategic Analysis**: Coordinated analysis using specialized AI agents
- **Interactive Dashboard**: Real-time monitoring and analytics
- **Analysis History**: Track and review past strategic assessments
- **Performance Analytics**: Monitor agent effectiveness and response times
- **Template System**: Reusable analysis configurations
- **PDF Export**: Professional reports generation
- **Agent Rating System**: User feedback and evaluation system for agent outputs

## Rating System

The application includes a comprehensive rating system that allows users to evaluate and provide feedback on agent outputs:

### Features
- **5-Star Rating System**: Rate each agent's analysis from 1-5 stars
- **Detailed Reviews**: Optional text reviews and feedback
- **Helpful Aspects**: Tag what was most valuable (clarity, depth, actionable insights, etc.)
- **Improvement Suggestions**: Provide specific feedback for enhancement
- **Recommendation System**: Indicate whether you'd recommend the agent to others
- **Rating Analytics**: View aggregated ratings and trends
- **Agent Performance Metrics**: Track agent effectiveness over time

### API Endpoints
- `POST /ratings/submit` - Submit a rating for an agent result
- `GET /ratings/agent/{agent_name}` - Get ratings for a specific agent
- `GET /ratings/session/{session_id}` - Get all ratings for an analysis session
- `GET /ratings/summaries` - Get rating summaries for all agents
- `GET /ratings/analytics` - Get rating analytics and trends
- `GET /ratings/top-rated` - Get top-rated agents

### Usage
After completing an analysis, users can:
1. Rate each agent's output using the star rating system
2. Provide detailed written feedback
3. Select helpful aspects from predefined categories
4. Suggest improvements
5. Indicate recommendation status
6. View aggregated ratings and analytics

The rating system helps improve agent performance and provides valuable insights for users selecting agents for future analyses. 

Default Admin Credentials:
Username: admin
Email: admin@strategicai.com
Password: admin123






