<template>
  <div
    class="row justify-content-center text-center mt-3 pt-3 pb-3"
    v-if="showSpinner"
  >
    <div class="col-12">
      <div
        class="spinner-grow text-we"
        :style="`width: ${size}rem; height: ${size}rem`"
        role="status"
      >
        <span class="sr-only">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
    showSpinner:Boolean,
    size:Number
})
</script>

<style scoped></style>
