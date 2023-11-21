<template>
  <div class="about">
    <h1>This is an about page</h1>
  </div>
</template>

<style>
@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}
</style>

<script setup>
import {inject, onMounted} from 'vue';
const axios = inject("$axios");
onMounted(async () => {
  try {
    console.log(axios);
    const response = await axios.get('http://10.16.27.41:8000/api/endpoint');
    console.log(response);
  } catch (error) {
    console.error(error);
  }
});
</script>