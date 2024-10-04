<template>
  <div class="login-container">
    <div class="login-card">
      <h2>Вход</h2>
      <form @submit.prevent="login">
        <div class="p-field p-mb-3">
          <label for="username">Логин</label>
          <InputText v-model="username" id="username" placeholder="Введите логин" required />
        </div>
        <div class="p-field p-mb-3">
          <label for="password">Пароль</label>
          <Password v-model="password" id="password" toggleMask placeholder="Введите пароль" required />
        </div>
        <Button label="Войти" icon="pi pi-check" type="submit" class="p-mt-3" />
      </form>
      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script>

import InputText from 'primevue/inputtext';
import Password from 'primevue/password';
import Button from 'primevue/button';
import axios from '@/axios';

export default {
  name: 'UserLogin',
  components: {
    InputText,
    Password,
    Button
  },
  data() {
    return {
      username: '',
      password: '',
      message: ''
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('http://localhost:8000/auth/api/login/', {
          username: this.username,
          password: this.password,
        });

        if (response.status === 200) {
          localStorage.setItem('access_token', response.data.access);
          localStorage.setItem('refresh_token', response.data.refresh);
          this.message = "Вход успешен!";
        await this.$router.push('/home/ollama_chat');
        } else {
          this.message = "Ошибка входа";
        }
      } catch (error) {
        console.error('Ошибка:', error);
        this.message = 'Ошибка входа';
      }
    }
  }
};
</script>

<style scoped>

.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #2c3e50;
}

.login-card {
  width: 400px;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  margin-bottom: 20px;
}

button {
  width: 100%;
}

input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
}

label {
  margin-bottom: 5px;
  text-align: left;
}
</style>
