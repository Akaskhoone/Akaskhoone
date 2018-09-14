from django.contrib.auth import get_user_model

User = get_user_model()


def get_password_errors(e):
    errors = []
    for i in e.args[0]:
        if str(list(i)[0]).__contains__('similar'):
            errors.append("Similar")
        elif str(list(i)[0]).__contains__('short'):
            errors.append("Length")
        elif str(list(i)[0]).__contains__('numeric'):
            errors.append("Numeric")
        elif str(list(i)[0]).__contains__('common'):
            errors.append("Common")
    return errors


def get_user(request):
    username = request.query_params.get('username')
    if username:
        try:
            return User.objects.get(username=username)
        except:
            return None
    email = request.query_params.get('email')
    if email:
        try:
            return User.objects.get(email=email)
        except:
            return None
    return request.user


def has_permission(user, requested_user):
    if requested_user.profile.is_private:
        if requested_user.profile in user.profile.followings.all() or user == requested_user:
            return True
        else:
            return False
    return True
