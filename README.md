# Quiz Game Application

This is a simple quiz game application built using Streamlit. Participants can answer a series of questions and their responses are recorded for scoring.

## Project Structure

```
quiz-game-app
├── src
│   ├── app.py               # Main entry point of the Streamlit application
│   ├── questions.json       # JSON file containing quiz questions and answers
│   ├── responses.json       # JSON file storing participants' responses
│   └── utils.py             # Utility functions for loading questions and saving responses
├── requirements.txt         # List of dependencies required for the project
└── README.md                # Documentation for the project
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd quiz-game-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the Streamlit application:
   ```
   streamlit run src/app.py
   ```

## Usage

- Open the application in your web browser.
- In the first tab, enter your name and answer the questions presented.
- You will be asked a total of 6 unique questions.
- Your responses will be saved in `responses.json`.

## Scoring

- After all participants have completed the quiz, you can view the scores.
- Each correct answer earns 1 point, plus an additional base point, resulting in a maximum score of 7.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.