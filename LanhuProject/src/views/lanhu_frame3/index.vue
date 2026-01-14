<template>
  <div class="page flex-col">
    <div class="section_1 flex-col justify-end">
      <span class="text_1">传感器EX1</span>
      <span class="text_2">型号：</span>
      <span class="text_3">测量对象：</span>
      <span class="text_4">量程：</span>
      <span class="text_5">安装位置：</span>
      <div class="box_1 flex-row">
        <span class="text_6">状态：</span>
        <div class="section_2 flex-col justify-between">
          <div class="box_2 flex-col"></div>
          <div class="box_3 flex-col"></div>
        </div>
        <div class="text-group_1 flex-col justify-between">
          <span class="text_7">正常</span>
          <span class="text_8">异常</span>
        </div>
      </div>
      <img
        class="image_1"
        referrerpolicy="no-referrer"
        src="./assets/img/FigmaDDSSlicePNGa85bd3a017e5c1a860666dac71f7d521.png"
      />
    </div>
  </div>
</template>
<script>
export default {
  data() {
    return {
      constants: {}
    };
  },
  methods: {}
};
</script>
<style scoped lang="css" src="./assets/index.css" />