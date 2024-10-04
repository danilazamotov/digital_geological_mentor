<template>
  <div class="register-wrapper">
    <div class="p-card p-p-3 p-shadow-3">
      <h1 class="p-text-center">Регистрация</h1>
      <form @submit.prevent="register">
        <div class="p-field p-mb-3">
          <label for="username">Логин</label>
          <InputText v-model="username" id="username" type="text" placeholder="Введите логин" required />
        </div>
        <div class="p-field p-mb-3">
          <label for="email">Email</label>
          <InputText v-model="email" id="email" type="email" placeholder="Введите email" required />
        </div>
        <div class="p-field p-mb-3">
          <label for="password">Пароль</label>
          <Password v-model="password" id="password" toggleMask feedback placeholder="Введите пароль" required />
        </div>
        <div class="p-field p-mb-3">
          <label for="password2">Повторите пароль</label>
          <Password v-model="password2" id="password2" toggleMask placeholder="Повторите пароль" required />
        </div>
        <Button label="Зарегистрироваться" icon="pi pi-check" type="submit" class="p-mt-3 p-button-rounded p-button-primary" />
      </form>
      <p class="p-mt-3 p-text-center">{{ message }}</p>
    </div>
  </div>
</template>

<script>
import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import axios from '@/axios';

export default {
  components: {
    InputText,
    Password,
    Button,
  },
  data() {
    return {
      username: '',
      email: '',
      password: '',
      password2: '',
      message: '',
    };
  },
  methods: {
    async register() {
      try {
        const response = await axios.post('http://localhost:8000/auth/api/register/', {
          username: this.username,
          email: this.email,
          password: this.password,
          password2: this.password2,
        });
        if (response.status === 201) {
          this.message = 'Пользователь успешно зарегистрирован!';
        } else {
          this.message = 'Ошибка регистрации';
        }
      } catch (error) {
        console.error('Ошибка:', error);
        this.message = 'Ошибка регистрации';
      }
    },
  },
};
</script>

<style scoped>
.register-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2c3e50;
}

.p-card {
  max-width: 400px;
  width: 100%;
  padding: 2rem;
}

.p-field {
  display: flex;
  flex-direction: column;
}

.p-text-center {
  text-align: center;
}
</style>
