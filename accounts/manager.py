from django.contrib.auth.base_user import BaseUserManager



class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, user_id, password=None, **extra_fields):
        if not user_id:
            raise ValueError('User_id is Required')
        
        user_id = self.normalize_email(user_id)
        user = self.model(user_id=user_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, user_id, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Not a superuser')
        
        return self.create_user(user_id, password, **extra_fields)