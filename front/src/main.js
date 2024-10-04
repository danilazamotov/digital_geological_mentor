import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

import PrimeVue from 'primevue/config';
import Button  from 'primevue/button';
import InputText from 'primevue/inputtext';
import Password  from 'primevue/password';
import ToastService from 'primevue/toastservice';

import 'primevue/resources/themes/saga-blue/theme.css';
import 'primevue/resources/primevue.min.css';
import 'primeicons/primeicons.css';
import 'primeflex/primeflex.css';

const app = createApp(App);
app.use(PrimeVue);
app.use(ToastService);
app.component('LoginButton', Button);
app.component('InputText', InputText);
app.component('UserPassword', Password );


app.use(router).mount('#app');
