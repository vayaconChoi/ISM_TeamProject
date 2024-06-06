from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserDB

def join_index(req):
    if req.method == "POST":
        account = req.POST.get('account')
        print(account)

        if account == 'create':
            user_first_name = req.POST.get('inputFirstName')
            print(user_first_name)
            user_last_name = req.POST.get('inputLastName')
            user_email = req.POST.get('inputEmail')
            user_id = req.POST.get('userid')
            user_password = req.POST.get('password')
            user_password_check = req.POST.get('password_check')
            # 예외처리 1 (ID or PASSWORD 가 완성되지 않음)
            if not user_id or not user_password:
                return render(req, 'registration/signup.html', {'error_msg': '아이디 또는 비밀번호를 입력하세요.'})

            # 예외처리 2 (PASSWORD 확인에서의 error)
            elif user_password != user_password_check:
                return render(req, 'registration/signup.html', {'error_msg': '비밀번호가 서로 같지 않습니다.'})

            # 예외처리 3 (ID 중복)
            elif UserDB.objects.filter(username=user_id).exists():
                return render(req, 'registration/signup.html', {'error_msg': '이미 사용중인 아이디입니다.'})

            # no exception (이상 없음)
            new_users = UserDB.objects.create_user(username=user_id, password=user_password, first_name=user_first_name, last_name=user_last_name, email=user_email)
            new_users.save()
        else:
            pass
        return redirect('users:login')

    return render(req, 'registration/signup.html')