import {createApp} from 'vue';
import axios from 'axios';
import VueAxios from 'vue-axios';

import App from './App.vue';
import * as config from './lib/config';

const Vue = createApp(App);

// Loads plugins
Vue.use(VueAxios, axios)

// Configures plugins
Vue.axios.defaults.baseURL = config.REST_API_BASE_URL;

// Initializes the app
Vue.mount('#app');

