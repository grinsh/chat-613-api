from flask import Flask, request, jsonify, Response, redirect
from openai import OpenAI
import os
from dotenv import load_dotenv
from json_convert import make_utf8_json_response
import httpx




load_dotenv()  
api_key = os.getenv("OPENAI_API_KEY")  
client = OpenAI(
    api_key=api_key,
    http_client=httpx.Client(verify=False)
)  # או השתמשי ב־os.getenv("OPENAI_API_KEY")


app = Flask(__name__)


# תיאור התחום
DOMAIN_DESCRIPTION = "הצ'אט מתמקד במתמטיקה לתלמידי בית ספר יסודי בלבד."

# פונקציה לבדיקת אם השאלה רלוונטית למתמטיקה יסודית
def is_valid_math_question(question):
    keywords = ['חיבור', 'חיסור', 'כפל', 'חילוק', 'שברים', 'אחוזים', 'מספרים טבעיים', 'בעיות מילוליות', 'גאומטריה בסיסית']
    return any(keyword in question for keyword in keywords)

# תחליף לתשובה מ-GPT לצורך דוגמה
def get_mock_gpt_response(question):
    return make_utf8_json_response(f"שאלה מצוינת על מתמטיקה יסודית: {question}.\nפתרון: (תשובה לדוגמה)")

def get_gpt_response(question):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "אסור לך באיסור חמור לענות על שאלות שלא קשורות באופן ישיר למתמטיקה יסודית, בנוסף אסור לך לתת דוגמאות שאינן מספריות.  את היכול רק לפרט דוגמאות מספריות ולא דוגמאות שקשורות למנושאים שאינם מתמטיקה"},
            {"role": "user", "content": question}
        ],
        max_tokens=30
    )
    return(response.choices[0].message.content)

# נקודת קצה לקבלת תיאור התחום
@app.route('/api/domain', methods=['GET'])
def get_domain():
    return make_utf8_json_response({"domain": DOMAIN_DESCRIPTION})

# נקודת קצה לשליחת שאלה וקבלת תשובה
@app.route('/api/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data.get("question", "")

    # if not is_valid_math_question(question):
    #     return make_utf8_json_response({"error": "השאלה לא קשורה למתמטיקה לבית ספר יסודי"}), 400

    # כאן אפשר לשלב קריאה אמיתית ל-GPT אם רוצים
    answer = get_gpt_response(question)

    return make_utf8_json_response({"question": question, "answer": answer})

# נקודת קצה לתיעוד ה-API
@app.route('/api/docs', methods=['GET'])
def api_docs():
    return make_utf8_json_response({
        "endpoints": {
            "/api/domain": {
                "method": "GET",
                "description": "קבלת תיאור התחום שבו עוסק הצ'אט"
            },
            "/api/ask": {
                "method": "POST",
                "description": "שליחת שאלה וקבלת תשובה (רק מתמטיקה ליסודי)",
                "body": {
                    "question": "string"
                }
            },
            "/api/docs": {
                "method": "GET",
                "description": "קבלת תיעוד של נקודות הקצה"
            }
        }
    })

@app.route('/api/docs/html', methods=['GET', 'POST'])
def api_docs_html():
    answer = ''
    question = ''
    if request.method == 'POST':
        question = request.form.get('question', '')
        if question:
            try:
                answer = get_gpt_response(question)
            except Exception as e:
                answer = f"שגיאה: {e}"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="he">
    <head>
        <meta charset="UTF-8">
        <title>📘 תיעוד ונסיון API</title>
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; background-color: #f9f9f9; padding: 20px; }}
            h1 {{ color: #333; }}
            .section {{ margin-bottom: 40px; }}
            .form-container {{ background-color: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            input[type=text] {{ width: 70%; padding: 10px; margin-bottom: 10px; }}
            button {{ padding: 10px 15px; }}
            .answer-box {{ background: #f1f1f1; padding: 15px; border-radius: 8px; }}
            .endpoint {{ margin-top: 30px; background-color: #fff; padding: 15px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
            pre {{ background: #f8f8f8; padding: 10px; border-radius: 5px; direction: ltr; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="section form-container">
            <h1>🧮 התנסות חיה - שאל שאלה במתמטיקה</h1>
            <form method="post">
                <input type="text" name="question" placeholder="הקלידו שאלה כאן..." required>
                <button type="submit">שלח</button>
            </form>
            {f"<div class='answer-box'><strong>שאלה:</strong> {question}<br><strong>תשובה:</strong> {answer}</div>" if question else ""}
        </div>

        <div class="section">
            <h1>📘 תיעוד ה־API</h1>

            <div class="endpoint">
                <h2>GET /api/domain</h2>
                <p>מתאר את תחום הפעילות של ה־API.</p>
                <pre>{{
    "domain": "הצ'אט מתמקד במתמטיקה לתלמידי בית ספר יסודי בלבד."
}}</pre>
            </div>

            <div class="endpoint">
                <h2>POST /api/ask</h2>
                <p>שולח שאלה ומחזיר תשובה.</p>
                <pre>{{
    "question": "כמה זה 8 כפול 7?"
}}</pre>
                <p><strong>תגובה לדוגמה:</strong></p>
                <pre>{{
    "question": "כמה זה 8 כפול 7?",
    "answer": "שאלה מצוינת על מתמטיקה יסודית: כמה זה 8 כפול 7?.\\nפתרון: (תשובה לדוגמה)"
}}</pre>
            </div>

            <div class="endpoint">
                <h2>GET /api/docs</h2>
                <p>מחזיר את תיעוד ה־API בפורמט JSON.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return Response(html_content, content_type='text/html; charset=utf-8')
@app.route('/')
def redirect_to_docs():
    return redirect('/api/docs/html')



if __name__ == '__main__':
    app.run(debug=True)
