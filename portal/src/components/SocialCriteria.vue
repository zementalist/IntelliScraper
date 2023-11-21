<template>
    <div class="row justify-content-center">
        <div class="col-12 p-4 border border-2 rounded we-border-color">
            <h3 class="display-4 text-center">{{ title }} <font-awesome-icon :icon="icon.class" :color="icon.color" /></h3>
            <form action="">
                <div class="text-center mb-2">
                    <div class="form-check form-switch">
                        <input v-model="userCriteriaEnabled" @change="updateUserInput" class="form-check-input we-checked" type="checkbox" role="switch" id="flexSwitchCheckChecked" :checked="enabled">
                    </div>
                </div>
                <div class="mb-3 form-group">
                  <label for="tweets_count" class="form-label">{{ label }} Count</label>
                  <input type="number" v-model="userItemCount" @input="updateUserInput"  name="tweets_count" class="form-control" min="0" :max="maxItems">
                </div>
                <div class="mb-3 form-group" v-if="typeof selectedDate != 'undefined'">
                  <label for="until_date" class="form-label text-left">Until Publish Date</label>
                  <input type="date" v-model="userSelectedDate" @change="updateUserInput" name="until_date" class="form-control" :min="minDate" :max="maxDate" placeholder="Until Publish Date">
                </div>

            </form>
        </div>

    </div>
</template>

<script setup>
import {ref} from 'vue'
const props = defineProps({
    enabled: Boolean,
    selectedDate: String,
    title:String,
    maxItems: Number,
    label:String,
    minDate:String,
    itemCount: Number,
    icon:Object,
    index:Number
    })

let maxDate = new Date().toISOString().split("T")[0]

let userSelectedDate = ref(props.selectedDate)
let userItemCount = ref(props.itemCount)
let userCriteriaEnabled = ref(props.enabled)

const emits = defineEmits(['update-user-input'])

const updateUserInput = () => {
    let criteria = {
        index:props.index,
        selectedDate:userSelectedDate.value,
        itemCount:userItemCount.value,
        enabled:userCriteriaEnabled.value
    }
    emits("update-user-input", criteria);
}
</script>

<style scoped>
.form-switch {
    display: inline-block;
}
#flexSwitchCheckChecked {
    width: 50px;
    height: 25px;
}
</style>