import {fileURLToPath, URL} from 'node:url'

import {defineConfig, loadEnv} from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import {ElementPlusResolver} from 'unplugin-vue-components/resolvers'
import ElementPlus from 'unplugin-element-plus/vite'

export default defineConfig(({mode}) => {
    const env = loadEnv(mode, process.cwd(), '')
    const devPort = Number(env.VITE_DEV_SERVER_PORT || 9091)
    const proxyTarget = env.VITE_DEV_PROXY_TARGET || env.VITE_API_BASE_URL?.replace(/\/api$/, '')

    return {
        plugins: [
            vue(),
            AutoImport({
                imports: ['vue', 'vue-router'],
                resolvers: [ElementPlusResolver({importStyle: 'sass'})],
                dts: 'src/auto-imports.d.ts',
            }),
            Components({
                resolvers: [ElementPlusResolver({importStyle: 'sass'})],
            }),
            ElementPlus({
                useSource: true,
            }),
        ],
        server: {
            port: devPort,
            open: false,
            proxy: {
                '/api': {
                    target: proxyTarget,
                    ws: true,
                    changeOrigin: true,
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
                    additionalData: `
          @use "@/assets/css/index.scss" as *;
        `,
                }
            }
        }
    }
})
