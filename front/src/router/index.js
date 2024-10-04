import {createRouter, createWebHistory} from 'vue-router';
import Login from '../components/UserLogin.vue';
import Register from '../components/UserRegister.vue';
import Chat from '../components/ChatHome.vue';

const routes = [
{
  path: '/login',
  name: 'Login',
  component: Login
},
{
  path: '/register',
  name: 'Register',
  component: Register
},
{
  path: '/home/ollama_chat',
  name: 'Chat',
  component: Chat,
}
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
