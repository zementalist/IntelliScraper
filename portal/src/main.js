import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import "bootstrap/dist/css/bootstrap.min.css"

/* import font awesome icon component */

import "bootstrap"
import axios from 'axios';
// import {VueWow} from 'vue-wow'; 

import './assets/main.css'
import { library } from '@fortawesome/fontawesome-svg-core'

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faSort, faGlobe, faIndustry, faMapLocationDot } from '@fortawesome/free-solid-svg-icons'
import {faYoutube, faTwitter} from '@fortawesome/free-brands-svg-icons'
library.add(faSort, faGlobe, faIndustry, faYoutube, faTwitter, faMapLocationDot)

const app = createApp(App)

const axiosConfig = {
    // baseURL: 'http://10.16.27.41:8000',
    baseURL: "http://127.0.0.1:8000",
    timeout: 60*60*60*1,
  };
  
const axiosInstance = axios.create(axiosConfig)

app.use(router)
// app.use(VueWow)
// app.component("u-animate-container",UAnimateContainer).component("u-animate",UAnimate)

app.config.globalProperties.axios = axiosInstance;
app.component('font-awesome-icon', FontAwesomeIcon);
app.mount('#app')


/*
TASKS
- Database Design
- Job Scheduling
- Scraping Limitations
- Clustering
- Scraping Configuration save

*/