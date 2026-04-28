import {createApp} from 'vue'
import App from './App.vue'
import router from './router'
import ElementPlus from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import scaleDirective from './assets/js/scaleDirective'
import '@/assets/css/global.css'
import axios from "axios";

const app = createApp(App)

app.use(router)
app.use(ElementPlus, {
    locale: zhCn,
})
app.directive('scale', scaleDirective);
app.mount('#app')
axios.defaults.baseURL = 'http://localhost:9090';
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}
