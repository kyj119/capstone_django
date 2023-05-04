DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', #사용할 엔진 설정
        'NAME': 'test', #연동할 MySQL의 데이터베이스 이름
        'USER': 'root', #DB접속 계정명
        'PASSWORD': 'password', #해당DB접속 계정 비밀번호
        'HOST': 'localhost', #실제 DB 주소
        'PORT': '3306' #포트 번호
    }
}
SECRET_KEY ='django-insecure-6go7df$dt(xlrf%7)7a6cy9+_)$%^4c4ytl0=drt&^d*9l)*pt'