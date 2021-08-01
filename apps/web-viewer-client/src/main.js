import {createApp} from 'vue';
import axios from 'axios';
import 'bulma/css/bulma.css';
import VueAxios from 'vue-axios';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import './add-icons';
import App from './App.vue';
import * as config from './lib/config';

const Vue = createApp(App);

// Loads plugins
Vue.use(VueAxios, axios);
Vue.component('font-awesome-icon', FontAwesomeIcon);

// Configures plugins
Vue.axios.defaults.baseURL = config.REST_API_BASE_URL;

// Initializes the app
Vue.mount('#app');

