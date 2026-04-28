import { ElMessage } from 'element-plus';
import router from '../router';
import axios from 'axios';
import { API_BASE_URL } from './config';

const request = axios.create({
    baseURL: API_BASE_URL,
    timeout: 70000,
    withCredentials: true
});

request.interceptors.request.use(config => {
    return config;
}, error => {
    return Promise.reject(error);
});

request.interceptors.response.use(
    response => {
        let res = response.data;
        if (response.config.responseType === 'blob') {
            return res;
        }
        if (typeof res === 'string') {
            res = res ? JSON.parse(res) : res;
        }
        if (res.code === '401') {
            ElMessage.error(res.msg);
            router.push('/login');
        }
        return res;
    },
    error => {
        console.log('err', error);
        const serverMessage = error.response?.data?.msg || error.response?.data?.message || error.response?.data;
        if (serverMessage) {
            error.message = typeof serverMessage === 'string' ? serverMessage : JSON.stringify(serverMessage);
        }
        if (error.response && error.response.status === 500) {
            ElMessage.error(error.message || '服务器内部错误，请稍后再试');
        }
        return Promise.reject(error);
    }
);

export default request;
