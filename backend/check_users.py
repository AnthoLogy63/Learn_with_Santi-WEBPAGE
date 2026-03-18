from users.models import User
user = User.objects.first()
if user:
    print(f'User: {user.usu_cod}, DNI: {user.usu_dni}')
else:
    print('No users found')
