(function flexible(window, document) {
  function resetFontSize() {
    const clientWidth = document.documentElement.clientWidth;
    // 基准宽度改为更合理的值，让页面可以缩放适配
    const baseWidth = 2560;
    const scale = clientWidth / baseWidth;

    // 限制最小和最大缩放比例
    const minScale = 0.3;
    const maxScale = 1.2;
    const finalScale = Math.min(Math.max(scale, minScale), maxScale);

    const size = 37.5 * finalScale;
    document.documentElement.style.fontSize = size + 'px';
  }

  // reset root font size on page show or resize
  resetFontSize();
  window.addEventListener('pageshow', resetFontSize);
  window.addEventListener('resize', resetFontSize);
})(window, document);
