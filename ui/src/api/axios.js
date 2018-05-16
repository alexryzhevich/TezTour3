import axios from 'axios';

const BASE_URL = 'http://192.168.25.19:11980/api';

const instance = axios.create({
  baseURL: BASE_URL
});

export default instance;
