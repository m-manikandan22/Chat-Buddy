from flask import Flask, render_template, request, jsonify, session
from groq import Groq
from datetime import timedelta, datetime
from flask import Flask
from flask_session import Session

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


app.secret_key = 'myverysecretkeyhdfviudsahfiewkjfnkewhrewrefdfhsfhaiuowerkjewdfgiodf'

app.permanent_session_lifetime = timedelta(days=10)

API_KEY = "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"

client = Groq(api_key=API_KEY)

def chat_with_phi(chat_history):
    try:
        response = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",
            messages=chat_history,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def home():
    session.permanent = True
    if "chats" not in session:
        session["chats"] = []
    if "chat_history" not in session:
        session["chat_history"] = []
    return render_template("index.html", previous_chats=session["chats"])

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.form.get("user_input", "")
    chat_history = session.get("chat_history", [])

    chat_history.append({"role": "user", "content": user_input})

    bot_response = chat_with_phi(chat_history)

    chat_history.append({"role": "assistant", "content": bot_response})

    session["chat_history"] = chat_history

    return jsonify({"response": bot_response})

@app.route("/new_chat", methods=["POST"])
def new_chat():
    if "chat_history" in session and session["chat_history"]:
        title = session["chat_history"][0]["content"][:30]
        session["chats"].append({"title": title, "timestamp": datetime.now().isoformat(), "history": session["chat_history"]})
    session.pop("chat_history", None)
    session["chats"] = [chat for chat in session["chats"] if (datetime.now() - datetime.fromisoformat(chat["timestamp"])).days <= 10]
    return jsonify({"message": "New chat started!"})

if __name__== "__main__":
    app.run(debug=True)
