# app.py
import os
import sqlite3
from datetime import datetime
from openai import OpenAI
from flask import render_template
import json
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np


# init database
def init_db():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            action_type TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()


init_db()

import os
#init client
api_key = os.getenv("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=api_key)



from flask import Flask, request, jsonify


app = Flask(__name__)
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)


# read lesson.json
with open('lessons.json', 'r', encoding='utf-8') as f:
    lesson_data = json.load(f)

# provide quiz data API
@app.route("/get_quiz", methods=["GET"])
def get_quiz():
    quiz = lesson_data.get("quiz", [])
    return jsonify({"quiz": quiz})

# add /take_quiz API (for test result)
@app.route("/take_quiz", methods=["POST"])
def take_quiz():
    data = request.get_json()
    user_answers = data.get("answers", [])
    
    # read  quiz questions from lesson_data 
    quiz = lesson_data.get("quiz", [])
    score = 0
    for i, item in enumerate(quiz):
        correct_answer = item.get("answer")
        if i < len(user_answers) and user_answers[i] == correct_answer:
            score += 1

    quiz_count = len(quiz)
    # according to corection rate to decide the user language level
    if quiz_count > 0:
        ratio = score / quiz_count
        if ratio < 0.5:
            computed_level = "Entry"
        elif ratio < 0.8:
            computed_level = "Middle"
        else:
            computed_level = "Advanced"
    else:
        computed_level = "Entry"
    
    return jsonify({"level": computed_level, "score": score})

@app.route("/log_interaction", methods=["POST"])
def log_interaction():
    data = request.get_json()
    action_type = data.get("action_type", "unknown")
    details = data.get("data", {})  # here data to save detail
     # save all the records in details 
    details = {
        "user_question": details.get("user_question", ""),
        "user_learningstyle": details.get("user_learningstyle", ""),
        "user_instructor_preference": details.get("user_instructor_preference", ""),
        "user_language": details.get("user_language", ""),
        "answers": details.get("answers", ""),  
        "level": details.get("user_level", ""),
        "score": details.get("score", "")
    }   
    # retrieve time
    timestamp = datetime.utcnow().isoformat()

    # save in SQLite
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_interactions (timestamp, action_type, data)
        VALUES (?, ?, ?)
    ''', (timestamp, action_type, json.dumps(details, ensure_ascii=False)))
    conn.commit()
    conn.close()

    return jsonify({"status": "success"})



# router test
@app.route("/")
def home_page():
    return render_template("index.html")
# get lessons.json
with open("lessons.json", "r", encoding="utf-8") as f:
    lessons_data = json.load(f)


# get personal sugesstion API
@app.route("/get_advice", methods=["POST"])
def get_advice():
    data = request.get_json()  
    user_question = data.get("user_question", "I want to improve my English grammar.")
    user_learningstyle = data.get("user_learningstyle", "prefer and watch videos.")
    user_instructor_preference = data.get("user_instructor_preference", "always use positive words to encourage students.")
    user_language = data.get("user_language","traditional Chinese")
    user_level = data.get("user_level", "entry")
    score = data.get("score", "0")



    # GPT Prompt
    prompt_text = f"""
You are the worldclass language tutor for a student with {user_level} language proficiency.
The student has this concern or question: {user_question}
The student's learning style is {user_learningstyle}  and preference of the instructor is  {user_instructor_preference}

Based on user's English level, learning needs and learning preference, please use {user_language} to provide around 50 words and helpful pieces of advice or learning plans.
please list your reply or even with emojis.
"""


    # 呼叫 OpenAI GPT API (gpt-3.5-turbo)
    response = client.chat.completions.create(model="gpt-4o",
    messages=[{"role": "system", "content": "You are the best English tutor who can reply in any language and help students to learn English well."},
              {"role": "user", "content": prompt_text}],
    temperature=0.7,
    max_tokens=200)

    # retrieve response
    advice = response.choices[0].message.content.strip()

    
    return jsonify({
        "level": user_level,
        "score": score,
        "advice": advice
    })


def update_clusters():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    # 1. read all interaction records
    cursor.execute("SELECT id, data FROM user_interactions")
    rows = cursor.fetchall()
    
    user_ids = []
    levels = []
    learning_styles = []
    
    for row in rows:
        record_id = row[0]
        data_json_str = row[1]
        
        # parse JSON
        try:
            data_dict = json.loads(data_json_str)
        except:
            continue  
        
        # get level & user_learningstyle
        level = data_dict.get("level", "Entry")
        user_learningstyle = data_dict.get("user_learningstyle", "")
        
        user_ids.append(record_id)
        levels.append(level)
        learning_styles.append(user_learningstyle)
    
    if len(user_ids) < 2:
        conn.close()
        return []
    
    # 2. code level 
    level_map = {"Entry": 0, "Middle": 1, "Advanced": 2}
    level_encoded = [level_map.get(lv, 0) for lv in levels]
    
    # 3. use TfidfVectorizer turn learning_style to vector
    vectorizer = TfidfVectorizer(stop_words='english')
    learningstyle_tfidf = vectorizer.fit_transform(learning_styles)  # shape = (n_samples, n_features)
    
    # 4. 為了把 level 也合併到向量，可以把 level_encoded 轉成 2D，然後跟 TF-IDF 矩陣合併
    #    這裡做個簡單示範：將 level 視為單一維度加在 TF-IDF 後面 (hstack)
    level_encoded_np = np.array(level_encoded).reshape(-1, 1)  # shape (n_samples, 1)
    
    from scipy.sparse import hstack
    X = hstack([learningstyle_tfidf, level_encoded_np])  # shape = (n_samples, n_features+1)
    
    # 5. use KMeans to group ，eg: k=3
    k = 3
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(X)
    
    # get group label
    cluster_labels = kmeans.labels_  # 長度 = n_samples
    
    # 6.（可選）將 cluster_label 更新回 DB
    #    因為我們 database schema 沒有專門的欄位存 cluster_label，
    #    這裡示範把它加進 data JSON 的 "cluster_label" 裡再存回去
    for i, uid in enumerate(user_ids):
        label = int(cluster_labels[i])
        
        # extract  data id
        cursor.execute("SELECT data FROM user_interactions WHERE id=?", (uid,))
        row = cursor.fetchone()
        if not row:
            continue
        
        old_data_str = row[0]
        try:
            old_data_dict = json.loads(old_data_str)
        except:
            old_data_dict = {}
        
        old_data_dict["cluster_label"] = label  
        new_data_str = json.dumps(old_data_dict, ensure_ascii=False)
        
        cursor.execute("UPDATE user_interactions SET data=? WHERE id=?", (new_data_str, uid))
    
    conn.commit()
    conn.close()
    
    return cluster_labels


@app.route("/update_recommendation", methods=["GET"])
def update_recommendation():
    labels = update_clusters()
    return jsonify({"message": "Clusters updated", "labels": labels.tolist() if len(labels)>0 else []})

@app.route("/get_practice", methods=["POST"])
def get_practice():
    data = request.get_json()
    user_level = data.get("user_level", "")
    user_learningstyle = data.get("user_learningstyle", "")
    user_instructor_preference = data.get("user_instructor_preference", "")
    user_question = data.get("user_question", "")
    cluster_label = 0  
    practice_prompt_text = ""
    
    if cluster_label == 0:
        practice_prompt_text = f"""
You are an English learning material creator. The user is an Entry-level English learner who prefers {user_learningstyle}.
Please provide a short real learning material not just learning suggestions which meets {user_instructor_preference}  or exercise (~200 words). If the material is about videos, please provide the material link (e.g., 'https://youtu.be/fake1234') and all need  to solve {user_question}.
It should be easy to follow.
"""
    elif cluster_label == 1:
        practice_prompt_text = f"""
You are an English learning material creator. The user is a Middle-level English learner who prefers {user_learningstyle}.
Please provide a short real learning material not just learning suggestions which meets {user_instructor_preference} (~200 words) with moderate complexity, some new vocabulary and reading comprehension questions..
If the material is about videos, please provide the material link (e.g., 'https://youtu.be/fake1234') and all need  to solve {user_question}
"""
    else:
        practice_prompt_text = f"""
You are an English learning material creator. The user is an Advanced-level English learner who prefers {user_learningstyle}.
Please provide  a short real learning material not just learning suggestions which meets {user_instructor_preference} (~200 words) with advanced vocabulary, critical thinking questions, or creative writing tasks to solve {user_question}.
If the material is about videos, please provide the material link (e.g., 'https://youtu.be/fake1234')
"""
    
    # 3. call OpenAI 
    response = client.chat.completions.create(
        model="gpt-3.5-turbo", 
        messages=[{"role": "system", "content": "You are an English teacher."},
                  {"role": "user", "content": practice_prompt_text}],
        temperature=0.7,
        max_tokens=350
    )
    
    practice_text = response.choices[0].message.content.strip()
    
    return jsonify({"practice": practice_text})



if __name__ == "__main__":
    # 執行 Flask 伺服器
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=5001)
