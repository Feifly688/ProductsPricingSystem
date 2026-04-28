import {fileURLToPath, URL} from 'node:url'

import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'
// 导入对应包
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers'

import ElementPlus from 'unplugin-element-plus/vite'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [
        vue(),
        AutoImport({
            resolvers: [ElementPlusResolver(
                {importStyle: 'sass'}
            )],
        }),
        Components({
            resolvers: [ElementPlusResolver(
                {importStyle: 'sass'}
            )],
        }),
        AutoImport({
            imports: ['vue', 'vue-router', 'pinia'], // 自动引入 Vue、Vue Router 和 Pinia 的 API
            resolvers: [ElementPlusResolver()], // 自动引入 Element Plus 的组件
            dts: 'src/auto-imports.d.ts', // 生成类型声明文件
        }),

        // 按需定制主题配置
        ElementPlus({
            useSource: true,
        }),
    ],
    server: {
        // host: '0.0.0.0',
        port: '9091',
        open: false,
        proxy: {
            '/api': {
                target: 'http://121.41.129.169:9090/',
                ws: true,
                changeOrigin: true,
                pathRewrite: {
                    '^/api': '/'
                }
            }
        }
    },
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url))
        }
    },
    css: {
        preprocessorOptions: {
            scss: {
                // 自动导入定制化样式文件进行样式覆盖
                additionalData: `
          @use "@/assets/css/index.scss" as *;
        `,
            }
        }
    }
})
