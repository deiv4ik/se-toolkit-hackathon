# 🤖 InnoSient - Scientific Guide to Innopolis

AI-powered web application that helps tourists discover scientific facts about Innopolis landmarks with audio narration.

## Demo

[!Main Page](assets/1.png)
[!Generation Data](assets/2.png)
[!Result](assets/3.png)

## Product Context

### End Users
- Tourists and visitors of Innopolis
- Students and university staff
- Conference attendees
- Science and technology enthusiasts

### Problem
Visitors to Innopolis lack an engaging, personalized way to learn about the scientific and technological significance of local landmarks. Traditional guidebooks are static and do not offer interactive or AI-driven experiences.

### Solution
An intelligent web guide that:
- Identifies nearby landmarks based on coordinates
- Generates unique scientific facts using GigaChat AI
- Provides audio narration via Text-to-Speech (TTS)
- Displays a dynamic "Popular Places" rating based on user analytics

## Features

### ✅ Implemented
- **Geolocation Search**: Finds landmarks within a 300m radius.
- **AI Fact Generation**: GigaChat creates unique scientific explanations (Physics, Biology, History).
- **Audio Narration**: Automatic MP3 generation via gTTS.
- **Popularity Rating**: Real-time analytics of the most visited/requested places (PostgreSQL).
- **Web Interface**: Responsive design for mobile and desktop.
- **Database**: PostgreSQL for storing landmarks, prompts, and user analytics.
- **Dockerized**: Full containerization for easy deployment (Web + DB).

### 🚧 Not Yet Implemented
- User authentication / Personal accounts
- Offline mode
- Multi-language support (currently Russian only)
- Interactive map (Leaflet integration)

## Usage

### Via Web Interface
1. Open `http://10.93.26.27:8080` in your browser.
2. Click on any landmark card.
3. Read the generated scientific fact and listen to the audio narration.
4. Check the **"🔥 Popular Now"** section to see trending spots.

### Available Landmarks
- 🏛 Innopolis University
- 🏭 A.S. Popov Technopark
- ⚽ Sports Complex
- 🤖 Robotics Laboratory
- 🎨 ArtSpace Cultural Center

## Deployment

### System Requirements
- **OS**: Ubuntu 24.04 (or Windows with WSL/Docker)
- **RAM**: 512MB+
- **Storage**: 1GB+ (for PostgreSQL)
- **Docker**: Installed and running

### Step-by-Step Deployment

#### 1. Clone the repository
```bash
git clone https://github.com/deiv4ik/se-toolkit-hackathon.git
cd se-toolkit-hackathon
```

#### 2. Configure Environment
Create a `.env` file in the root directory:
```env
# GigaChat API Credentials
GIGACHAT_AUTH_KEY=your_gigachat_auth_key_here
GIGACHAT_SCOPE=GIGACHAT_API_PERS
```

#### 3. Run with Docker (Recommended)
This command starts both the Web App and the PostgreSQL database automatically.

```bash
docker compose up -d
```

*   **Database**: Initializes automatically on the first run.
*   **Web App**: Available at **http://10.93.26.27:8080**.

#### 4. Stop Application
```bash
docker compose down
```

## Project Structure

```text
InnoSient/
├── bot.py                    # Flask backend & API routes
├── database.py               # PostgreSQL connection & queries
├── geo_utils.py              # Haversine distance calculation
├── gigachat_api.py           # GigaChat AI integration
├── templates/
│   └── index.html            # Frontend (HTML/CSS/JS)
├── init.sql                  # Database initialization script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (secrets)
├── Dockerfile                # Backend container config
└── docker-compose.yml        # Multi-container orchestration
```

## Architecture

### Components
1.  **Backend (Flask)**: Handles REST API requests, business logic, and TTS generation.
2.  **Database (PostgreSQL)**: Stores landmarks, prompts, user request history, and caches facts.
3.  **Frontend (HTML/JS)**: Responsive UI that communicates with the backend via Fetch API.
4.  **AI Services**:
    *   **GigaChat**: LLM for generating scientific content.
    *   **gTTS**: Google Text-to-Speech for audio.

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main Web Interface |
| `/api/get_fact` | POST | Get fact & audio for coords |
| `/api/popular` | GET | Get top rated landmarks |
| `/api/places` | GET | Get all landmarks list |
| `/audio/<file>`| GET | Serve audio files |
=======
# se-toolkit-hackathon
