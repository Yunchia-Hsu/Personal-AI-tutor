let quizData = [];

// 當頁面載入時，從 /get_quiz 取得題目
window.onload = async function() {
    const response = await fetch("/get_quiz");
    const data = await response.json();
    quizData = data.quiz;
    renderQuiz();
};

// 根據 quizData 動態生成 quiz 區塊
function renderQuiz() {
    const quizSection = document.getElementById("quizSection");
    quizSection.innerHTML = ""; // 清空區塊
    quizData.forEach((item, index) => {
        const div = document.createElement("div");
        div.innerHTML = `<p>${index + 1}. ${item.question}</p>`;
        item.options.forEach((option, idx) => {
            div.innerHTML += `
                <input type="radio" name="q${index}" value="${option}" id="q${index}_o${idx}">
                <label for="q${index}_o${idx}">${option}</label><br>
            `;
        });
        quizSection.appendChild(div);
    });
}

// 提交 quiz 並呼叫 /take_quiz API
async function submitQuiz() {
    const answers = [];
    for (let i = 0; i < quizData.length; i++) {
        const selected = document.querySelector(`input[name="q${i}"]:checked`);
        if (selected) {
            answers.push(selected.value);
        } else {
            alert("Please answer all quiz questions.");
            return;
        }
    }
    // 呼叫 /take_quiz API 並取得結果
    const response = await fetch("/take_quiz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answers: answers })
    });
    const data = await response.json();

    // 顯示分數與等級，並自動填入建議表單的等級欄位
    document.getElementById("quizResult").innerText = 
        "Your level is: " + data.level + " (Score: " + data.score + ")";
    document.getElementById("level").value = data.level;
    
    // 紀錄 quiz 互動
    await logQuizInteraction(answers, data.level, data.score);
}

// 呼叫 /log_interaction 紀錄 quiz 互動
async function logQuizInteraction(answers, level, score) {
    await fetch("/log_interaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            action_type: "quiz_submit",
            data: {
                answers: answers,
                user_level: level,
                score: score
            }
        })
    });
}

// 取得學習建議
async function getAdvice() {
    const levelInput = document.getElementById("level").value;
    const questionInput = document.getElementById("question").value;
    const userlanguage = document.getElementById("language").value;
    const userlearningstyle = document.getElementById("learningstyle").value;
    const userinstructorpreference = document.getElementById("instructor").value;

    const response = await fetch("/get_advice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_level: levelInput,
            user_question: questionInput,
            user_learningstyle: userlearningstyle,
            user_instructor_preference: userinstructorpreference,
            user_language: userlanguage
        })
    });

    const data = await response.json();
    document.getElementById("adviceBox").innerText = data.advice;
    
    // 紀錄 advice 互動
    await logAdviceInteraction(
        levelInput,
        questionInput,
        userlearningstyle,
        userinstructorpreference,
        userlanguage
    );
}

// 專門負責把建議的互動記錄到 /log_interaction 的函式
async function logAdviceInteraction(level, question, learningstyle, instructorPreference, language) {
    await fetch("/log_interaction", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            action_type: "advice_request",
            data: {
                user_level: level,
                user_question: question,
                user_learningstyle: learningstyle,
                user_instructor_preference: instructorPreference,
                user_language: language
            }
        })
    });
}

async function requestPractice() {
    const level = document.getElementById("level").value;
    const learningstyle = document.getElementById("learningstyle").value;
    const userinstructorpreference = document.getElementById("instructor").value;
    const questionInput = document.getElementById("question").value;

    // const response = await fetch("/get_practice", {
    //     method: "POST",
    //     headers: { "Content-Type": "application/json" },
    //     body: JSON.stringify({
    //         user_level: level,
    //         user_learningstyle: learningstyle,
    //         user_instructor_preference: userinstructorpreference,
    //         user_question: questionInput
    //     })
    // });
    // const data = await response.json();
    // document.getElementById("practiceBox").innerText = data.practice || "No practice generated.";
    try {
        const response = await fetch("/get_practice", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                user_level: level,
                user_learningstyle: learningstyle,
                user_instructor_preference: userinstructorpreference,
                user_question: questionInput
            })
        });
        
        const data = await response.json();
        console.log("Practice API response:", data);
        document.getElementById("practiceBox").innerText = data.practice || "No practice generated.";
    } catch (error) {
        console.error("Error in requestPractice:", error);
        document.getElementById("practiceBox").innerText = "Error fetching practice data.";
    }
}