# Overview

An agentic system for discovering personalized activities and social event ideas. Built with Next.js, Python FastAPI, and OpenRouter LLM integration.

The core initial focus is to recommend activities between two locations to help two people who live in different areas to easily meet.

## Features

- 🤖 **AI Agent**: Conversational agent that understands your preferences and finds activities, executing tool calls as needed
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
  - `search_places_for_dates`: Google Maps Places API integration for finding date activities between locations
  - `get_weather_for_location`: Weather information for outdoor activity planning
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
source venv/bin/activate
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

6. (Optional) Set up Google Maps Places API:
   - In the same Google Cloud project, enable Places API and Geocoding API
   - Create an API key (or use the same one if you already have one)
   - Add `GOOGLE_MAPS_API_KEY` to your `.env` file

7. (Optional) Set up OpenWeatherMap API:
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Get your free API key
   - Add `OPENWEATHER_API_KEY` to your `.env` file

8. Run the backend:
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

3. (Optional) Set up environment variables:
   - Create `.env.local` if you need to customize the API URL
   - Default API URL is `http://localhost:8000/api` (no config needed)

4. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Usage

1. **Start with Chat**: Go to the home page and start chatting with the agent
   - Example: "Find me outdoor activities in San Francisco"
   - Example: "Show me date ideas under $50"

2. **Set Preferences**: Go to Preferences page to set your location, interests, and budget. There are predefined user preferences templates; you must choose one as the current user.

3. **Browse Activities**: Visit the Activities page to see a gallery of activities with a collapsible assistant

4. **Save to Sheets**: Ask the agent to save activities to Google Sheets
   - Example: "Save these activities to a Google Sheet"

## Project Structure

```
activities-agent/
├── frontend/             # Next.js frontend
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
│   │   ├── orchestrator.py  # Main agent orchestrator, acts as MCP client to call tools, stores tool list
│   │   └── tools/        # Tool implementations, like an MCP server providing Tool interfaces
│   ├── api/              # API routes
│   ├── data/             # Data to store a set of user preferences and chat histories that can be selected between
│   ├── docs/             # Documentation, including Backend Architecture
│   ├── models/           # Data models
│   ├── tests/            # Integration tests
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

For a detailed explanation of backend architectural decisions, see [backend/docs/ARCHITECTURE.md](backend/docs/ARCHITECTURE.md).

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

## Testing

### Running Backend Tests

The backend includes integration tests for the agent orchestrator and tool calling functionality.

1. Ensure you're in the backend directory with the virtual environment activated:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Run all tests:
```bash
pytest tests/ -v
```

3. Run a specific test file:
```bash
pytest tests/test_orchestrator.py -v
```

4. Run tests with more detailed output:
```bash
pytest tests/ -v -s
```

**Note**: Tests require an `OPENROUTER_API_KEY` environment variable to be set, as they make real API calls to test the orchestrator's tool calling functionality.

## Environment Variables

### Backend (.env)
- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `GOOGLE_MAPS_API_KEY`: (Optional) Google Maps API key for Places API integration. Get one at [Google Cloud Console](https://console.cloud.google.com/). Enable Places API and Geocoding API.
- `OPENWEATHER_API_KEY`: (Optional) OpenWeatherMap API key for weather information. Get one at [OpenWeatherMap](https://openweathermap.org/api). Free tier: 60 calls/minute.

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000/api)

## License

MIT
