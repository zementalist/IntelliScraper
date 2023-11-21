<template>
  <div class="container h-100">
    <div class="row justify-content-center mt-3">
      <div class="col-12 text-center">
        <!-- <h2>Scheduled Jobs</h2> -->
      </div>
    </div>
    <div class="row">
        <div class="col-12 text-center">
            <Spinner size="6" :show-spinner="dataset.length == 0"></Spinner>
        </div>
    </div>
    <div class="row">
        <div class="col-12 text-center">
            <ExploreTable
            :title="'Scheduled Jobs'"
            :dataset="dataset"
            :allowSelection="true"
            :delete-action-endpoint="'/job/delete/'"
            v-if="dataset.length > 0"
            >
        </ExploreTable>
        </div>
    </div>
  </div>
</template>

<script setup>
import Spinner from "../components/Spinner.vue";
import ExploreTable from "../components/ExploreTable.vue";
import { onMounted, ref, getCurrentInstance, reactive } from "vue";

const axios = getCurrentInstance().appContext.config.globalProperties.axios;

let dataset = ref([])

onMounted(() => {
    let path = "/jobs"
    axios.get(path).then(response => {
        dataset.value = response.data.results
        console.log(dataset)
    })
})
</script>

<style scoped></style>
