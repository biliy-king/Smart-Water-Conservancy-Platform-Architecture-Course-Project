#!/usr/bin/env python
"""
创建超级用户并获取admin Token
"""

import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hydro_platform.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import UserProfile

# 创建或更新超级用户
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin123')
user.is_superuser = True
user.is_staff = True
user.save()

print(f"✓ 超级用户 {'创建' if created else '更新'} 成功: {user.username}")

# 创建或更新UserProfile，设置role为admin
profile, profile_created = UserProfile.objects.get_or_create(user=user)
profile.role = 'admin'
profile.save()

print(f"✓ 用户角色设置为: admin")

# 获取Token
try:
    response = requests.post('http://127.0.0.1:8000/api/users/login/', 
        json={'username': 'admin', 'password': 'admin123'})
    
    print(f"✓ 请求状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        token = data['tokens']['access']
        
        print(f"\n✓ Admin Token 获取成功:")
        print(f"\n{token}")
        print(f"\n复制上面的Token到APIPost的Header中：")
        print(f"  Key: Authorization")
        print(f"  Value: Bearer {token}")
    else:
        print(f"✗ 登录失败: {response.status_code}")
        print(f"响应: {response.json()}")
except Exception as e:
    print(f"✗ 错误: {e}")
    print(f"确保Django服务器正在运行 (python manage.py runserver)")
