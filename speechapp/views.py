from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from openai import OpenAI
from groq import Groq
from .models import SpeechHistory

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

client = Groq(
    api_key="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"
)

def correct_text(request):

    corrected = ""
    text = ""

    if request.method == "POST":

        text = request.POST.get("text", "").strip()

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Correct the grammar and punctuation of the following text.
Return only the corrected text.
Do not add explanations or extra sentences.

Text: {text}
"""
                }
            ]
        )

        corrected = response.choices[0].message.content
        SpeechHistory.objects.create(
    user=request.user,
    original_text=text,
    corrected_text=corrected
)

    return render(request, 'home.html', {
        'corrected': corrected,
        'original_text': text
    })

def chatbot(request):

    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    if request.method == "POST":

        message = request.POST.get("message")

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

           messages=[

 {
    "role": "system",

    "content": """

You are VoiceScript AI Assistant.

Behave like ChatGPT.

Give human-like, smart, modern and practical answers.

Abilities:
- General conversation
- Gujarati ↔ English translation
- Coding help and error solving
- HTML, CSS, JavaScript, Python, Django
- Resume and interview help
- Grammar correction
- Speech-to-text project help

Rules:
- Answer naturally like a real AI assistant
- Avoid robotic/template answers
- Give practical examples
- Keep answers short if question is simple
- Give detailed answers if needed
- Explain step by step when required
- Translate Gujarati correctly
- Be friendly and professional
- Understand normal human language
- Solve coding errors properly

"""
},

    {
        "role": "user",
        "content": message
    }

]
        )

        answer = response.choices[0].message.content

        chat_history = request.session["chat_history"]

        chat_history.append({
            "user": message,
            "bot": answer
        })

        request.session["chat_history"] = chat_history

    return render(request,"home.html",{
        "chat_history": request.session["chat_history"]
    })

def home(request):
    return render(request, "home.html")

def login_user(request):

    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            auth_login(request, user)

            return redirect('/')

    return render(request, "login.html")

def register_user(request):

    if request.method == "POST":

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('/login/')

    return render(request, "register.html")

def logout_user(request):

    logout(request)

    return redirect('/login/')

def download_pdf(request):

    text = request.GET.get('text')

    response = HttpResponse(content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename="corrected_text.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica", 14)

    p.drawString(100, 750, "Corrected Text:")

    p.drawString(100, 720, text)

    p.save()

    return response
