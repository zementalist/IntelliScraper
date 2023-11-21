<template>
  <div>
    <div class="row">
      <div class="col-12">
        <div class="card">
          <div class="card-body text-center">
            <h3 class="card-title m-b-0">{{ title }}</h3>
          </div>
          <form class="m-2">
              <input
                v-model="searchKeywords"
                @input="search"
                type="text"
                name="search"
                id="search"
                class="form-control text-center fw-bolder border border-1 border-secondary"
                placeholder="Search"
              />
            </form>
          <div class="table-responsive" v-if="data instanceof Array && data.length > 0">
            <table class="table table-striped table-responsive table-hover">
              <thead class="thead-dark">
                <tr>
                  <th  v-if="allowSelection">
                    <label class="custom-checkbox">
                      <input
                        type="checkbox"
                        id="mainCheckbox"
                        class="listCheckbox"
                        @change="toggleAllCheckboxes"
                      />
                    </label>
                  </th>
                  <th 
                    
                    class="th-title"
                    v-for="key in Object.keys(data[0] ?? {})"
                    @click="sortBy(key)"
                  >
                    {{ key }}
                    <span class="arrow"
                      ><font-awesome-icon :icon="['fas', 'sort']"
                    /></span>
                  </th>
                  <th>    
                    Actions                 
                  </th>
                </tr>
              </thead>
              <tbody class="custom-table">
                <tr v-for="item in dataMirror">
                  <td :class="item.country"  v-if="allowSelection">
                    <label class="custom-checkbox">
                      <input
                        :checked="selectedItems.includes(item)"
                        type="checkbox"
                        @change="toggleSingleCheckbox(item)"
                        class="listCheckbox we-checked checkbox-child"
                      />
                    </label>
                  </td>
                  <td v-for="(val, key) in item" >
                    <img v-if="String(val).includes('.jpg')||String(val).includes('.png')" :src="val" height="100">
                    <a :href="val" target="_blank" v-else-if="String(val).startsWith('http')">{{ key }} URL</a>
                    <span v-else-if="(new RegExp(/\d{4}-\d{2}-\d{2}/).exec(String(val)))">
                      {{ new Date(String(val)).toLocaleDateString() }} 
                      {{ new Date(String(val)).toLocaleTimeString()  }}
                    </span>
                    <span v-else>{{ val }}</span>
                    
                  </td>

                  <td>
                    <form v-if="deleteActionEndpoint" :action="deleteActionEndpoint" method="post"></form>
                      <button
                        type="checkbox"
                        @click="actionDelete(item.id)"
                        class="btn btn-danger"
                        >Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <nav aria-label="Page navigation example sticky-left">
              <span class="row justify-content-center p-2">Showing {{ Math.min(rows_per_page, dataMirror.length) }} of {{ data.length }} items</span>
              <ul class="pagination justify-content-center">
                <li class="page-item">
                  <a class="page-link" href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                </li>
                <li
                  class="page-item"
                  @click="updatePage(i)"
                  :key="i"
                  v-for="i in pages_count"
                  :class="i == 1 ? 'active' : ''"
                >
                  <a class="page-link">{{ i }}</a>
                </li>
                <li class="page-item">
                  <a class="page-link" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, getCurrentInstance } from "vue";

let props = defineProps({dataset:Array, title:String, allowSelection:Boolean, deleteActionEndpoint:String})
let emits = defineEmits(['update-selected-rows'])
// let data = ref([
//   { country: "India", browsing: "Chrome OS", platform: "Linux", engine: 76 },
//   { country: "A", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "B", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "C", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "D", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "E", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "F", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "G", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "H", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "I", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "J", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "K", browsing: "Firefox", platform: "Windows", engine: 35 },
//   { country: "L", browsing: "Firefox", platform: "Windows", engine: 35 },
// ]);
let data = ref(props.dataset);

let dataMirror = ref([]);
let allIsSelected = ref(false);
let searchKeywords = ref("");
let selectedItems = ref([]);
let ascendingSort = ref(false);
let currentPage = ref(1);
let rows_per_page = 5;
let pages_count = ref(!(data.value instanceof Array) ? 0 : Math.ceil(data.value.length / rows_per_page));

let updatePage = (page_number) => {
  currentPage.value = page_number;
  let startIndex = currentPage.value * rows_per_page - rows_per_page;
  let stopIndex = page_number * rows_per_page;
  let result = data.value.slice(startIndex, stopIndex);
  dataMirror.value = result;
  if(searchKeywords.value.trim() != "") search();
};

let updateSelectedRow = () => {
  emits("update-selected-rows", selectedItems.value.map(item => {return item.id}))
}

let search = () => {
  console.log(searchKeywords.value);
  let keywords = searchKeywords.value.toLocaleLowerCase();
  if (keywords.trim() == "") {
    updatePage(currentPage.value);
  } else {
    let searchResult = data.value.filter((item) => {
      let itemValues = Object.values(item).join(" ").toLocaleLowerCase();
      if (itemValues.includes(keywords)) {
        console.log("FOund " + item.country);
        return item;
      }
    });
    dataMirror.value = searchResult;
  }
};

let sortBy = (key) => {
  ascendingSort.value = !ascendingSort.value;
  dataMirror.value = dataMirror.value.sort((itemA, itemB) => {
    if (itemA[key] > itemB[key]) return ascendingSort.value ? 1 : -1;
    else if (itemA[key] == itemB[key]) return 0;
    else return ascendingSort.value ? -1 : 1;
  });
};
let toggleAllCheckboxes = () => {
  document.querySelectorAll(".checkbox-child").forEach((el, index) => {
    el.checked = !allIsSelected.value;
    if (allIsSelected.value) removeSingleItem(data.value[index]);
    else addSingleItem(data.value[index]);
  });
  allIsSelected.value = !allIsSelected.value;
  console.log(selectedItems.value);
};

let addSingleItem = (item) => {
  if (!selectedItems.value.includes(item)) selectedItems.value.push(item);
  updateSelectedRow(selectedItems)
};
let removeSingleItem = (item) => {
  let index = selectedItems.value.indexOf(item);
  if (index !== -1) {
    selectedItems.value.splice(index, 1);
    updateSelectedRow(selectedItems)
  }
};
let toggleSingleCheckbox = (item) => {
  console.log(item)
  if (selectedItems.value.includes(item)) removeSingleItem(item);
  else addSingleItem(item);
  console.log(item.id);
};

onMounted(() => {
    console.log("MOUNTED")
    console.log(data)
  document.querySelectorAll(".page-item").forEach((element) => {
    element.addEventListener("click", () => {
      document.querySelector(".page-item.active").classList.remove("active");
      element.classList.add("active");
    });
  });
  dataMirror.value = Array.from(data.value);
  updatePage(1);
});

const axios = getCurrentInstance().appContext.config.globalProperties.axios;

let actionDelete = (itemId)=> {
  let path = props.deleteActionEndpoint + itemId;
  axios.post(path).then(response => {
    if(response.status == 200) {
      alert("Item is deleted successfully")
      data.value = data.value.filter(item =>item.id != itemId);
      dataMirror.value = data.value;
      console.log(data)
    }
    else {
      alert("Something went wrong");
    }
  })
}
</script>

<style scoped>
body {
  background-color: #673ab7;
  font-family: "Calibri", sans-serif !important;
}

.container {
  margin-top: 100px;
}
.card {
  position: relative;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -ms-flex-direction: column;
  flex-direction: column;
  min-width: 0;
  word-wrap: break-word;
  background-color: #fff;
  background-clip: border-box;
  border: 0px solid transparent;
  border-radius: 0px;
}

.card-body {
  -webkit-box-flex: 1;
  -ms-flex: 1 1 auto;
  flex: 1 1 auto;
  padding: 1.25rem;
}

.card .card-title {
  position: relative;
  font-weight: 600;
  margin-bottom: 10px;
}

.table {
  width: 100%;
  max-width: 100%;
  margin-bottom: 1rem;
  background-color: transparent;
  text-align: center;
}

* {
  outline: none;
}

.table th .arrow {
  position: relative;
  float: right;
}
.table thead th {
  font-weight: 500;
  padding: 20px;
  border: 1px solid #dedede;
  color: #000;
  text-transform: capitalize;
  min-width: 8rem;
}
table .thead-dark th {
  background-color: #444;
  color: white;
}

.table thead th {
  vertical-align: middle;
  border-bottom: 2px solid #dee2e6;
}
tr {
  vertical-align: middle;
}

.table th {
  padding: 1rem;
  vertical-align: top;
  border-top: 1px solid #dee2e6;
  cursor: pointer;
}

.table th,
.table thead th {
  font-weight: 500;
}

th {
  text-align: inherit;
}

.custom-checkbox input {
  position: relative;
  cursor: pointer;
}
</style>
