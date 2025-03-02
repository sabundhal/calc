<template>
  <div class="container-fluid px-3">
    <div class="row justify-content-center">
      <div class="col-12 col-md-6 col-lg-4">
        <h1 class="text-center mb-3">Регистрация</h1>
        <hr class="mb-4">
        <alert :message="message" v-if="showMessage"></alert>
        <form @submit.prevent="handleRegisterSubmit">
          <!-- Поле имени пользователя -->
          <div class="mb-3">
            <label for="registerUsername" class="form-label">Имя пользователя:</label>
            <input
              type="text"
              class="form-control"
              :class="{ 'is-invalid': errors.username }"
              id="registerUsername"
              v-model="registerForm.username"
              placeholder="Введите имя пользователя"
              @input="clearError('username')"
            />
            <div v-if="errors.username" class="invalid-feedback">{{ errors.username }}</div>
            <div class="form-text text-muted">
              Допустимые символы: буквы (A-Z, a-z), цифры (0-9), дефисы (-) и подчёркивания (_)
            </div>
          </div>

          <!-- Поле email -->
          <div class="mb-3">
            <label for="registerEmail" class="form-label">Email:</label>
            <input
              type="email"
              class="form-control"
              :class="{ 'is-invalid': errors.email }"
              id="registerEmail"
              v-model="registerForm.email"
              placeholder="Введите email"
              @input="clearError('email')"
            />
            <div v-if="errors.email" class="invalid-feedback">{{ errors.email }}</div>
            <div class="form-text text-muted">Пример: user@example.com</div>
          </div>

          <!-- Поле пароля -->
          <div class="mb-3">
            <label for="registerPassword" class="form-label">Пароль:</label>
            <input
              type="password"
              class="form-control"
              :class="{ 'is-invalid': errors.password }"
              id="registerPassword"
              v-model="registerForm.password"
              placeholder="Введите пароль"
              @input="clearError('password')"
            />
            <div v-if="errors.password" class="invalid-feedback">{{ errors.password }}</div>
            <div class="form-text text-muted">
              Требования: 8-30 символов, Допустимые символы: буквы (A-Z, a-z), цифры (0-9), дефисы (-) и подчёркивания (_)
            </div>
          </div>

          <!-- Подтверждение пароля -->
          <div class="mb-3">
            <label for="registerConfirmPassword" class="form-label">Подтвердите пароль:</label>
            <input
              type="password"
              class="form-control"
              :class="{ 'is-invalid': errors.confirmPassword }"
              id="registerConfirmPassword"
              v-model="registerForm.confirmPassword"
              placeholder="Подтвердите пароль"
              @input="clearError('confirmPassword')"
            />
            <div v-if="errors.confirmPassword" class="invalid-feedback">{{ errors.confirmPassword }}</div>
          </div>

          <!-- Кнопки -->
          <div class="d-grid gap-2">
            <button type="submit" class="btn btn-primary">Зарегистрироваться</button>
            <button type="button" class="btn btn-outline-secondary" @click="handleRegisterCancel">Отмена</button>
          </div>

          <p class="text-center mt-4">
            Если вы уже зарегистрированы,
            <router-link to="/login" class="text-primary text-decoration-none">Войдите</router-link>
          </p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import router from '@/router';
import Alert from './Alert.vue';

export default {
  data() {
    return {
      registerForm: {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      },
      errors: {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      },
      message: '',
      showMessage: false,
    };
  },
  components: {
    alert: Alert,
  },
  methods: {
    validateForm() {
      this.errors = { username: '', email: '', password: '', confirmPassword: '' };
      let isValid = true;

      // Валидация имени пользователя
      if (!this.registerForm.username.trim()) {
        this.errors.username = 'Имя пользователя обязательно';
        isValid = false;
      } else if (this.registerForm.username.length < 3 || this.registerForm.username.length > 30) {
        this.errors.username = 'Имя должно быть от 3 до 30 символов';
        isValid = false;
      } else if (!/^[a-zA-Z0-9_-]+$/.test(this.registerForm.username)) {
        this.errors.username = 'Недопустимые символы в имени';
        isValid = false;
      }

      // Валидация email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!this.registerForm.email.trim()) {
        this.errors.email = 'Email обязателен';
        isValid = false;
      } else if (!emailRegex.test(this.registerForm.email)) {
        this.errors.email = 'Неверный формат email';
        isValid = false;
      }

      // Валидация пароля
      const passwordRegex = /^[a-zA-Z0-9_-]{8,30}$/;
      if (!this.registerForm.password) {
        this.errors.password = 'Пароль обязателен';
        isValid = false;
      } else if (!passwordRegex.test(this.registerForm.password)) {
        this.errors.password = 'Пароль не соответствует требованиям';
        isValid = false;
      }

      // Подтверждение пароля
      if (!this.registerForm.confirmPassword) {
        this.errors.confirmPassword = 'Подтвердите пароль';
        isValid = false;
      } else if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.errors.confirmPassword = 'Пароли не совпадают';
        isValid = false;
      }

      return isValid;
    },

    async handleRegisterSubmit() {
      if (!this.validateForm()) return;

      try {
        const payload = {
          username: this.registerForm.username,
          email: this.registerForm.email,
          password: this.registerForm.password
        };

        const response = await axios.post('/api/register', payload);

        if (response.status === 201) {
          this.message = 'Регистрация успешна!';
          this.showMessage = true;
          setTimeout(() => router.push({ name: 'Login' }), 1500);
        }
      } catch (error) {
        if (error.response) {
          const { status, data } = error.response;
          if (status === 409) {
            if (data.message.includes('Username')) {
              this.errors.username = 'Имя пользователя уже занято';
            } else if (data.message.includes('Email')) {
              this.errors.email = 'Этот email уже зарегистрирован';
            }
          } else {
            this.message = 'Ошибка сервера. Попробуйте позже.';
            this.showMessage = true;
          }
        } else {
          this.message = 'Ошибка сети. Проверьте соединение.';
          this.showMessage = true;
        }
      }
    },

    clearError(field) {
      this.errors[field] = '';
      this.showMessage = false;
    },

    handleRegisterCancel() {
      this.resetForm();
      router.go(-1);
    },

    resetForm() {
      this.registerForm = {
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      };
      this.errors = {
        username: '',
        email: '',
        password: '',
        confirmPassword: ''
      };
      this.message = '';
      this.showMessage = false;
    }
  }
};
</script>

<style scoped>
.invalid-feedback {
  display: block;
}
.form-text {
  font-size: 0.875em;
}
</style>