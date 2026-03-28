from django.shortcuts import render,redirect,get_object_or_404
from .models import CustomUser,Classroom,ClassroomStudent
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth import logout
import base64
import os
import numpy as np
import cv2
from deepface import DeepFace
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


def analyze_emotion_with_retry(img):
    try:
        return DeepFace.analyze(
            img,
            actions=["emotion"],
            enforce_detection=False,
            detector_backend="opencv"
        )
    except Exception as e:
        error_message = str(e)
        weights_path = "/opt/render/.deepface/weights/facial_expression_model_weights.h5"

        if "facial_expression_model_weights.h5" not in error_message:
            raise

        if os.path.exists(weights_path):
            os.remove(weights_path)

        return DeepFace.analyze(
            img,
            actions=["emotion"],
            enforce_detection=False,
            detector_backend="opencv"
        )



@csrf_exempt
@login_required
def kick_student(request):

    if request.method == "POST":

        data = json.loads(request.body)
        username = data.get("username")

        try:
            student = CustomUser.objects.get(username=username)

            student.is_active_student = False
            student.save()

            return JsonResponse({"status": "kicked"})

        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "Student not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def detect_emotion(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    try:
        data = json.loads(request.body)
        image_data = data.get("image")

        if not image_data:
            return JsonResponse({"error": "No image received"}, status=400)

        # Remove base64 header
        imgstr = image_data.split(",")[1]
        img_bytes = base64.b64decode(imgstr)

        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Resize for faster processing
        img = cv2.resize(img, (224, 224))

        # DeepFace emotion analysis
        result = analyze_emotion_with_retry(img)

        emotion = result[0]["dominant_emotion"]

        return JsonResponse({"emotion": emotion})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# def detect_emotion(request):
#
#     if request.method == "POST":
#         data = json.loads(request.body)
#         image_data = data.get("image")
#
#         # Remove base64 header
#         format, imgstr = image_data.split(';base64,')
#         img_bytes = base64.b64decode(imgstr)
#
#         np_arr = np.frombuffer(img_bytes, np.uint8)
#         img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#
#         try:
#             result = DeepFace.analyze(img,actions=['emotion'],enforce_detection=False)
#
#             emotion = result[0]['dominant_emotion']
#
#             return JsonResponse({"emotion": emotion})
#
#         except Exception as e:
#             return JsonResponse({"error": str(e)})
#
#     return JsonResponse({"error": "Invalid request"})

def student_register(request):

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('student_register')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('student_register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists!")
            return redirect('student_register')

        user = CustomUser.objects.create_user(username=username,email=email,password=password,role='student',is_active_student=True)
        
        return redirect('student_dashboard')

    return render(request, 'reg.html')
@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('student_dashboard')

    if request.method == "POST":
        title = request.POST['title']
        code = request.POST['code']
        Classroom.objects.create(title=title,code=code,teacher=request.user)

    classrooms = Classroom.objects.filter(teacher=request.user)
    return render(request, "teacher_dashboard.html", {"classrooms": classrooms})

@login_required
def teacher_room(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    if request.user != classroom.teacher:
        return redirect('teacher_dashboard')

    students = ClassroomStudent.objects.filter(classroom=classroom)

    return render(request, 'teacher_room.html', {'classroom': classroom,'students': students})

@login_required
def student_dashboard(request):
    classrooms = Classroom.objects.all()
    return render(request, "student_dashboard.html", {"classrooms": classrooms})


@login_required
def join_class(request, class_id):
    classroom = get_object_or_404(Classroom, id=class_id)

    if not request.user.is_active_student:
        return redirect('student_dashboard')

    if request.method == "POST":
        code = request.POST['code']
        if code == classroom.code:

            if not ClassroomStudent.objects.filter(classroom=classroom,student=request.user).exists():
                ClassroomStudent.objects.create(classroom=classroom,student=request.user)

                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    f"classroom_{classroom.id}",
                    {
                        'type': 'student_joined',
                        'username': request.user.username
                    }
                )

            return redirect('student_room', classroom_id=classroom.id)

    return redirect('student_dashboard')

@login_required
def student_room(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id)

    # Check if student joined this classroom
    if not ClassroomStudent.objects.filter(classroom=classroom,student=request.user).exists():
        return redirect('student_dashboard')

    return render(request, 'student_room.html', {'classroom': classroom})

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    return redirect('login')

def logout_view(request):
    logout(request)
    return redirect('login')
