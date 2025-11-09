# Activities Agent

An AI-powered agent system for discovering personalized activities and date ideas. Built with Next.js, Python FastAPI, and OpenRouter LLM integration.

## Features

- 🤖 **AI Agent**: Conversational agent that understands your preferences and finds activities
- 🔍 **Web Scraping**: Scrapes activity websites to find fun things to do
- 📊 **Google Sheets Integration**: Export activities to Google Sheets
- 💬 **Chat Interface**: Modern chat UI using assistant-ui.com patterns
- 🎨 **Airbnb-inspired UI**: Clean, modern design with activity cards
- ⚙️ **Preferences Management**: Set location, interests, budget, and time preferences
- 📱 **Responsive Design**: Works on desktop and mobile

## Architecture

### Frontend
- **Next.js 16** with TypeScript
- **Tailwind CSS** for styling
- **Axios** for API calls
- Chat interface with activity cards

### Backend
- **FastAPI** Python server
- **Agent Orchestrator**: LLM agent with tool calling
- **MCP-style Tools**:
  - `scrape_activities`: Web scraping for activities
  - `save_to_sheets`: Google Sheets integration
  - `get_user_preferences`: Retrieve user preferences
  - `update_user_preferences`: Update user preferences
- **OpenRouter API**: Multi-provider LLM access

## Setup

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+
- OpenRouter API key ([get one here](https://openrouter.ai/))
- Google Cloud Project with Sheets API enabled (for Google Sheets feature)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY
```

5. Set up Google Sheets API:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Sheets API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` and place it in the `backend` directory

6. Run the backend:
```bash
python main.py
# Or: uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local if needed (default should work)
```

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Start with Chat**: Go to the home page and start chatting with the agent
   - Example: "Find me outdoor activities in San Francisco"
   - Example: "Show me date ideas under $50"

2. **Set Preferences**: Go to Preferences page to set your location, interests, and budget

3. **Browse Activities**: Visit the Activities page to see a gallery of activities with a collapsible assistant

4. **Save to Sheets**: Ask the agent to save activities to Google Sheets
   - Example: "Save these activities to a Google Sheet"

## Project Structure

```
activities-agent/
├── frontend/              # Next.js frontend
│   ├── app/              # App router pages
│   │   ├── page.tsx      # Main chat page
│   │   ├── preferences/  # Preferences page
│   │   └── activities/   # Activities gallery page
│   ├── components/       # React components
│   │   ├── chat/         # Chat components
│   │   └── ui/           # UI components
│   └── lib/              # Utilities and API client
├── backend/              # Python FastAPI backend
│   ├── agents/           # Agent system
│   │   ├── orchestrator.py  # Main agent orchestrator
│   │   └── tools/        # Tool implementations
│   ├── api/              # API routes
│   ├── models/           # Data models
│   └── main.py           # FastAPI app entry point
└── README.md
```

## Learning Outcomes

This project demonstrates:

- **MCP-style Tool Patterns**: Tool definitions and execution without separate MCP server process
- **Agent Orchestration**: LLM agent with function calling
- **Tool Routing**: Routing LLM decisions to appropriate tools
- **Web Scraping**: Scraping as a tool capability
- **Google Sheets API**: Integration with Google services
- **Next.js + Python**: Full-stack architecture
- **Modern Chat UI**: Conversational interface patterns

## API Endpoints

- `POST /api/chat` - Chat with the agent
- `GET /api/preferences/{user_id}` - Get user preferences
- `PUT /api/preferences/{user_id}` - Update user preferences
- `GET /api/activities` - Get activities (with query, location, user_id params)

## Development

### Backend Development

The agent system uses a merged architecture where:
- Tools are defined with MCP-style schemas
- Orchestrator directly calls tool functions (no separate MCP process)
- OpenRouter API handles LLM function calling

### Frontend Development

- Uses Next.js App Router
- Client components for interactivity
- Server-side rendering where appropriate
- Tailwind CSS for styling

## Environment Variables

### Backend (.env)
- `OPENROUTER_API_KEY`: Your OpenRouter API key

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000/api)

## License

MIT
