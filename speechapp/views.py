from urllib import request
from django.shortcuts import render
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from openai import OpenAI
from groq import Groq
from .models import SpeechHistory
from .models import SpeechHistory, ChatHistory
from django.contrib.auth.decorators import login_required 
import PyPDF2

client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1",
)

client = Groq(api_key="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")

@login_required(login_url="/login/")
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
Return only corrected text.

Text: {text}
""",
                }
            ],
        )

        corrected = response.choices[0].message.content
        request.session["pdf_text"] = text

        SpeechHistory.objects.get_or_create(
            user=request.user, original_text=text, corrected_text=corrected
        )
        return render(
            request,
            "home.html",
            {
                "corrected": corrected,
                "original_text": text,
                "chat_history": request.session.get("chat_history", []),
            },
        )
    
@login_required(login_url="/login/")
def chatbot(request):

    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    if request.method == "POST":

        message = request.POST.get("message")

        chat_history = request.session.get("chat_history", [])

        messages = [
            {
                "role": "system",
                "content": """

You are VoiceScript AI Assistant.

Behave like ChatGPT.

Rules:
- Answer naturally
- Give short answers for simple questions
- Give detailed answers for coding questions
- Translate Gujarati and English properly
- Remember previous conversation
- Give proper formatted code only when user asks for code
- If user asks normal text or paragraph, NEVER give code
- For coding answers:
  - Give file structure
  - Separate HTML/CSS/JS/Python properly
  - Use clean formatting

""",
            }
        ]

        recent_chats = chat_history[-5:]

        for chat in recent_chats:

            messages.append({"role": "user", "content": chat["user"]})

            messages.append({"role": "assistant", "content": chat["bot"]})

        messages.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=messages
        )

        answer = response.choices[0].message.content

        chat_history.append({"user": message, "bot": answer})

        ChatHistory.objects.create(
            user=request.user, user_message=message, bot_reply=answer
        )

        request.session["chat_history"] = chat_history

    return render(
        request,
        "home.html",
        {
            "chat_history": request.session["chat_history"],
            "original_text": request.session.get("pdf_text", ""),
        },
    )

@login_required(login_url="/login/")
def home(request):

    if not request.user.is_authenticated:
        return redirect("/login/")

    total_speeches = SpeechHistory.objects.filter(user=request.user).count()

    total_chats = ChatHistory.objects.filter(user=request.user).count()

    return render(
        request,
        "home.html",
        {
            "original_text": request.session.get("pdf_text", ""),
            "chat_history": request.session.get("chat_history", []),
            "total_speeches": total_speeches,
            "total_chats": total_chats,
            "total_pdfs": 0,
        },
    )


def login_user(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:

            auth_login(request, user)

            return redirect("/")

    return render(request, "login.html")

def register_user(request):

    if request.method == "POST":

        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        User.objects.create_user(username=username, email=email, password=password)

        return redirect("/login/")

    return render(request, "register.html")

@login_required(login_url="/login/")
def logout_user(request):

    logout(request)

    return redirect("/login/")

@login_required(login_url="/login/")
def download_pdf(request):

    text = request.GET.get("text")

    response = HttpResponse(content_type="application/pdf")

    response["Content-Disposition"] = 'attachment; filename="corrected_text.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica", 14)

    p.drawString(50, 800, "Corrected Text:")

    text_object = p.beginText(50, 770)

    text_object.setFont("Helvetica", 12)

    words = text.split()

    line = ""

    for word in words:

        test_line = line + word + " "

        if len(test_line) < 80:

            line = test_line

        else:

            text_object.textLine(line)

            line = word + " "

    text_object.textLine(line)

    p.drawText(text_object)

    p.save()

    return response

@login_required(login_url="/login/")
def history_page(request):

    search = request.GET.get("search")

    records = SpeechHistory.objects.filter(user=request.user)

    if search:

        records = records.filter(original_text__icontains=search)

    records = records.order_by("-created_at")

    return render(request, "history.html", {"records": records})

@login_required(login_url="/login/")
def delete_history(request, id):

    record = SpeechHistory.objects.get(id=id, user=request.user)

    record.delete()

    return redirect("/history/")

@login_required(login_url="/login/")
def chat_history_page(request):

    search = request.GET.get("search")

    records = ChatHistory.objects.filter(user=request.user)

    if search:

        records = records.filter(user_message__icontains=search)

    records = records.order_by("-created_at")

    return render(request, "chat_history.html", {"records": records})

@login_required(login_url="/login/")
def delete_chat(request, id):

    record = ChatHistory.objects.get(id=id, user=request.user)

    record.delete()

    return redirect("/chat-history/")

@login_required(login_url="/login/")
def upload_pdf(request):

    print("VIEW CALLED")

    extracted_text = ""

    if request.method == "POST":

        print("POST RECEIVED")

        pdf_file = request.FILES.get("pdf_file")

        print(pdf_file)

        if pdf_file:

            reader = PyPDF2.PdfReader(pdf_file)

            for page in reader.pages:

                text = page.extract_text()

                print(text)

                extracted_text += text + "\n"
                request.session["pdf_text"] = extracted_text

                return render(
                    request,
                    "home.html",
                    {
                        "original_text": request.session.get("pdf_text", ""),
                        "chat_history": request.session.get("chat_history", []),
                    },
                )
