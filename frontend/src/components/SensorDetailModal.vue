<template>
  <div class="sensor-modal-overlay" @click.self="closeModal">
    <div class="page flex-col">
      <div class="section_1 flex-col justify-end">
        <span class="text_1">{{ sensorName }}</span>
        <span class="text_2">型号：</span>
        <span class="text_3">测量对象：</span>
        <span class="text_4">量程：</span>
        <span class="text_5">安装位置：</span>
        <div class="box_1 flex-row">
          <span class="text_6">状态：</span>
          <div class="section_2 flex-col justify-between">
            <div class="box_2 flex-col" :class="{ active: status === 'normal' }"></div>
            <div class="box_3 flex-col" :class="{ active: status === 'abnormal' }"></div>
          </div>
          <div class="text-group_1 flex-col justify-between">
            <span class="text_7">正常</span>
            <span class="text_8">异常</span>
          </div>
        </div>
        <img
          class="image_1"
          referrerpolicy="no-referrer"
          src="https://lanhu-oss-2537-2.lanhuapp.com/FigmaDDSSlicePNGa85bd3a017e5c1a860666dac71f7d521.png"
          alt="Sensor"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sensorName: {
    type: String,
    default: '传感器EX1'
  },
  status: {
    type: String,
    default: 'normal'
  }
})

const emit = defineEmits(['close'])

function closeModal() {
  emit('close')
}
</script>

<style scoped>
.sensor-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.page {
  position: relative;
  width: 819px;
  height: 1161px;
  overflow: hidden;
}

.section_1 {
  background-color: rgba(255, 252, 214, 1);
  border-radius: 30px;
  width: 819px;
  height: 1161px;
  border: 5px solid rgba(247, 226, 88, 1);
}

.text_1 {
  width: 288px;
  height: 104px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 64px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 64px;
  margin: 53px 0 0 266px;
}

.text_2 {
  width: 120px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 64px 0 0 83px;
}

.text_3 {
  width: 200px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 27px 0 0 83px;
}

.text_4 {
  width: 120px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 27px 0 0 83px;
}

.text_5 {
  width: 200px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin: 27px 0 0 75px;
}

.box_1 {
  width: 303px;
  height: 136px;
  margin: 27px 0 0 83px;
}

.text_6 {
  width: 120px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
}

.section_2 {
  width: 33px;
  height: 104px;
  margin: 10px 0 0 39px;
}

.box_2 {
  background-color: rgba(217, 217, 217, 1);
  border-radius: 50%;
  width: 33px;
  height: 33px;
  transition: background-color 0.3s;
}

.box_2.active {
  background-color: rgba(109, 236, 97, 1);
}

.box_3 {
  background-color: rgba(217, 217, 217, 1);
  border-radius: 50%;
  width: 33px;
  height: 33px;
  margin-top: 38px;
  transition: background-color 0.3s;
}

.box_3.active {
  background-color: rgba(255, 82, 39, 1);
}

.text-group_1 {
  width: 80px;
  height: 136px;
  margin-left: 31px;
}

.text_7 {
  width: 80px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
}

.text_8 {
  width: 80px;
  height: 65px;
  overflow-wrap: break-word;
  color: rgba(0, 0, 0, 1);
  font-size: 40px;
  font-family: 'Baloo Bhai 2', 'Inter', sans-serif;
  font-weight: normal;
  text-align: left;
  white-space: nowrap;
  line-height: 40px;
  margin-top: 6px;
}

.image_1 {
  width: 252px;
  height: 243px;
  margin: 193px 0 0 546px;
}

/* Flexbox utility classes */
.flex-col {
  display: flex;
  flex-direction: column;
}

.flex-row {
  display: flex;
  flex-direction: row;
}

.justify-between {
  justify-content: space-between;
}

.justify-end {
  justify-content: flex-end;
}
</style>
