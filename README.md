# Board Game Guru

## Project Overview
This application allows the user to upload board game rules for any game, and then run a Q&A Session with the board game docs, for learning how to play, getting answers to tricky rules, or learning about strategy. 

This is a Question Answering (QA) system powered by OpenAI's GPT-based models, built with Python and Flask. The application reads various types of files (including `.txt`, `.md`, `.docx`, and `.pdf`), converts them into embeddings using OpenAI's model, and stores them in a chroma vector database embedded in a docker container. Users can interact with the system via a Flask API, posing questions that are answered based on the stored embeddings.

## Installation

1. Ensure you have Python 3.6+ installed.
2. Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```
(Note: You should create a `requirements.txt` file that lists all the required Python packages.)

## Configuration

Before running the application, set up your environment:

1. Create a `.env` file in the root directory.
2. Add the `OPENAI_API_KEY` variable with your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Running the Application

Run the Flask application by executing:

```bash
python app.py
```

The application runs by default on `localhost:5000`.

## Usage

### Obtaining an API token

Send a GET request to the `/api/token` endpoint with your admin username and password to obtain an API token:

```bash
curl "http://localhost:5000/api/token?username=admin&password=password"
```

The server will respond with a JSON object that contains your token:

```json
{
  "token": "your_token_here",
  "duration": 3600
}
```

### Using the chat API

Send a POST request to the `/api/chat` endpoint with your game and prompt in the request body:

```bash
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer your_token_here" -d '{"game":"game_name", "prompt":"your_prompt_here"}' http://localhost:5000/api/chat
```

The server will respond with a JSON object that contains the AI's response:

```json
{
  "response": "AI's response"
}
```

## Project Structure

This project consists of three main parts:

1. `CreateVectorDb.py`: Contains code for processing files of various formats and storing their embeddings in a database.

2. `bgQA.py`: Contains code for interacting with the API of OpenAI's GPT-based models to generate responses based on user prompts and the stored embeddings.

3. `app.py`: A Flask application that provides an interface to the chatbot. It supports authenticating with a token, generating a token, and interacting with the chatbot via the `/api/chat` endpoint.

Note: You may want to periodically delete processed files to prevent unnecessary usage of storage space.

## Flask UI

The provided HTML code sets up an interactive chat interface for a Board Game Helper application. The application allows users to select a board game from a dropdown menu and type their questions into a chat input. The application then sends the selected game and question to a server endpoint, and appends the server's response to the chat box. 

## Key Features of the Code

1. **HTML Structure:** The basic structure of the webpage is defined in HTML. The body of the page contains a heading, dropdown menu for game selection, chat box, and input field for users to enter their questions.

2. **CSS Styling:** CSS rules are defined within the style section inside the head. These rules are used to style the HTML elements, such as the color of the text and the layout of the page.

3. **JavaScript Functionality:** The behavior of the webpage is controlled with JavaScript, included within script tags. The script uses the jQuery library to make HTTP requests to the server and update the Document Object Model (DOM) with the responses.

4. **Server Communication:** An AJAX function is included in the JavaScript to send a POST request to the '/api/chat' endpoint on the server. This includes the selected game and the user's query as data. This function then appends the server's response to the chat box. If the server returns an authorization error, it also re-fetches an authorization token.

## Considerations and Recommendations

- Security: The code currently retrieves an authentication token by sending an admin username and password directly in the code. For enhanced security, especially in a production environment, sensitive data should be handled more securely.

- Endpoint Specifications: The server endpoints utilized in the JavaScript code, specifically '/api/token' and '/api/chat', serve as placeholders. They should be replaced with the actual URLs for your API endpoints.

- Chat History: The chat box content is entirely replaced each time a new message is sent. It may be beneficial to append new messages to the existing chat history, preserving the conversation's flow.

- Templating: The code uses a templating syntax (`{% for string in games %}`) for populating the dropdown menu. Depending on the server-side framework, a templating engine such as Jinja2 (for Flask) or Django's templating engine might be required.


## Contributions

Contributions, issues, and feature requests are welcome. Feel free to check the [issues page](link-to-issues-page) if you want to contribute.

## License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## Contact

For any question, you can contact the author at: [your-email](mailto:your-email@example.com)

## Disclaimer

The content provided by this application is based on the machine learning model's ability to understand the input files and may not always be accurate or reliable. Always verify the information before using it.
