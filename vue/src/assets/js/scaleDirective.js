/**
 * scaleDirective
 * @author Feiqi
 * @date 2025/1/10  15:49
 */
// src/directives/scaleDirective.js

export default {
    beforeMount(el, binding) {
        const baseWidth = 1920; // 设计宽度
        const updateScale = () => {
            const browserWidth = window.innerWidth; // 浏览器可视宽度
            const zoomValue = browserWidth / baseWidth; // 缩放比例计算
            el.style.transform = `scale(${zoomValue}, ${zoomValue})`;
        };

        updateScale(); // 初始化时设置缩放

        // 监听窗口尺寸变化
        window.addEventListener('resize', updateScale);

        // 组件销毁时移除事件监听
        el._resizeHandler = updateScale;
    },
    unmounted(el) {
        window.removeEventListener('resize', el._resizeHandler);
    }
};
