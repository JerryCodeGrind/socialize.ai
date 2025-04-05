# Socialize AI Agent

A real-time facial recognition AI agent that provides personalized social tips. This application uses your webcam to detect faces, performs reverse image search, and generates tailored conversation starters and socializing tips using AI.

## Features

- **Real-time Face Detection**: Uses Roboflow's face detection model
- **Image-based Person Recognition**: Performs reverse image search via Google
- **Content Analysis**: Extracts and processes information about detected individuals
- **AI-powered Social Intelligence**: Generates personalized socializing tips with OpenAI GPT-4o
- **Interactive Overlay Display**: Shows name, overview, and conversation tips in real-time

## Project Structure

The project follows a modular architecture:

- `main.py` - Main application entry point and webcam integration
- `config.py` - API keys and configuration settings
- `face_detection.py` - Face detection functionality
- `image_processing.py` - Image upload and reverse search capabilities
- `web_scraping.py` - Website content extraction
- `gpt_prompt.py` - AI prompt for generating personalized social tips
- `search.py` - Background search processing
- `ui.py` - User interface and display functionality

## Setup Instructions

1. **Clone the repository**
   ```
   git clone https://github.com/yourusername/Socialize.git
   cd Socialize
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

3. **API Keys Configuration**
   
   The application uses several API keys stored in the `config.py` file:
   - `ROBOFLOW_API_KEY` - For face detection (from Roboflow)
   - `SERPAPI_API_KEY` - For Google reverse image search
   - `IMGBB_API_KEY` - For temporary image hosting
   - `OPENAI_API_KEY` - For GPT-4o social intelligence generation

   For security, consider moving these to environment variables.

## Usage

Run the application:
```
python main.py
```

### Controls:
- Press `r` to analyze a detected face and get social information
- Press `h` to toggle the results overlay
- Press `q` to quit the application

## How It Works

1. The application captures video from your webcam and continuously detects faces
2. When you press `r` while a face is detected:
   - It extracts the detected face region
   - Uploads the image to ImgBB for temporary hosting
   - Performs a Google reverse image search via SerpAPI
   - Scrapes relevant websites for information about the person
   - Uses OpenAI GPT-4o to extract the person's name, a brief overview, and generate social tips
   - Displays all information as an overlay on the webcam feed

## Dependencies

Main dependencies include:
- OpenCV for image processing and UI
- Requests for API communication
- BeautifulSoup for web scraping
- OpenAI for AI-powered text generation
- SerpAPI for reverse image search
- Inference SDK for Roboflow integration

See `requirements.txt` for the complete list with versions.
