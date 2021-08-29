import {createApp} from 'vue';
import axios from 'axios';
import 'bulma/css/bulma.css';
import VueAxios from 'vue-axios';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';

import './add-icons';
import App from './App.vue';

const Vue = createApp(App);

// Loads plugins
Vue.use(VueAxios, axios);
Vue.component('font-awesome-icon', FontAwesomeIcon);

// Initializes the app
Vue.mount('#app');

