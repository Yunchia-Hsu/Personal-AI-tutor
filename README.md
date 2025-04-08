

# MY-Own-AI-tutor
A language learning platform that integrates frontend web technologies with backend AI, using GPT-4o to deliver personalized learning advice, level assessments, and automatically generated practice materials, helping users effectively improve their English proficiency. 

## 1. Project Overview 
### Core Features
- Level Test Quiz: The frontend displays a customized quiz, while the backend (using Flask) grades responses and determines the user’s level.
<div style="text-align: center;">
<img src="https://github.com/Yunchia-Hsu/Personal-AI-tutor-/blob/main/screenshots/level%20quiz.png" alt="Game Screenshot" width="500"/>
  
- AI Advice: Generates personalized learning recommendations based on the user’s proficiency and preferences through GPT-4o.
<div style="text-align: center;">
<img src="https://github.com/Yunchia-Hsu/Personal-AI-tutor-/blob/main/screenshots/personal%20learning%20info.png" alt="Game Screenshot" width="500"/>
  
<div style="text-align: center;">
<img src="https://github.com/Yunchia-Hsu/Personal-AI-tutor-/blob/main/screenshots/AI%20suggestions.png" alt="Game Screenshot" width="500"/>
  
- Practice Material: Automatically creates reading/writing practice content based on the user’s level and learning style.
<div style="text-align: center;">
<img src="https://github.com/Yunchia-Hsu/Personal-AI-tutor-/blob/main/screenshots/practices.png" alt="Game Screenshot" width="500"/>
  
### Target Audience
- Users who want a personalized English learning experience powered by AI.


## 2. Key Features
### Level Test Quiz
- Quiz questions are stored in lessons.json. The backend automatically grades the answers and assigns users their respective level (Entry / Middle / Advanced).
### AI Advice
- Calls GPT-4 to generate personalized recommendations based on the user’s learning style, preferred teaching tone, and other details.
### Practice Generator
- Creates custom-tailored reading/writing practice content (~200 words) according to the user’s cluster and level.
### User Interaction Logging
- All quiz submissions and advice interactions are recorded via a `/log_interaction` API into an SQLite database
- Uses scikit-learn’s K-Means for clustering; future enhancements can deliver more personalized features based on these clusters.

## 3. Tech Stack / Architecture
### Frontend (HTML / CSS / JavaScript)
- Implements the interface with basic frontend technologies (HTML, CSS, JS), sending requests to the Flask backend via fetch.
- Dynamically loads quiz questions, displays quiz results, and shows AI-generated advice/practice materials.
### Backrend (Python)
- Provides RESTful APIs.
### AI Model / API
- Utilizes OpenAI’s GPT-4 (referred to as gpt-4o in the code) to produce learning suggestions and practice materials.
### Database (SQLite)
- Logs user interactions (quiz results, personal preferences, etc.) to enable K-Means clustering and further analysis.
### scikit-learn
- Applies K-Means to cluster users by learning style and level, providing more accurate course recommendations.

## 4.  Installation & Usage
### Clone the Repository
`git clone https://github.com/Yunchia-Hsu/Personal-AI-tutor-.git`
### install Dependencies 
- You can create a virtual environment (venv) or install packages directly in your system environment:
`pip install flask openai scikit-learn `
### Set Environment Variables 
- Add your OpenAI API key as an environment variable ( OPEN_API_KEY):
`export OPEN_API_KEY="YOUR_OPENAI_API_KEY"`


### Run the Flask Server
`python app.py` or `python3 app.py` depends on your systems
The server will start at http://0.0.0.0:5001 (or localhost:5001) by default.

### Access the Frontend
- Open index.html directly or visit http://localhost:5001/ in your browser.
- The page showcases the “Level Test Quiz,” “AI Suggestions,” and “Practice” features.

##  5. How to Use
### Quiz Feature
- When the page loads, quiz questions are automatically retrieved from json file.

- Click Submit Quiz to send answers. The system will return the score and level, then autofill “Your English Level.”


### Personalized Advice
- Fill in all personal learning information and click Get Advice. The system instantly calls GPT-4 to generate advice, which is displayed below.

  
- Click Gooooooo ~ to call /get_practice on the backend. The server provides a exercise tailored for you.


## 6. Roadmap 
- Expanded Question Bank: Generate an English question bank based on user needs (IELTS, TOEFL, oral proficiency tests, etc.).

- More Refined Clustering: K-Means clustering could incorporate quiz behavior and time spent on questions, aiding deeper learning analytics.

- Add User Login: Keep track of user IDs for recording historical input.

- Multi-language Interface: Support more languages to appeal to English learners worldwide.

