<template>
  <div>
    <form action="">
      <div class="dropdown" :id="title">
        <button
          class="btn btn-primary dropdown-toggle we-hover we-active we-border"
          type="button"
          id="dropdownMenuButton"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          {{ title }}
        </button>
        <ul class="dropdown-menu" aria-labelledby="dropdownMenuButton">
          <form class="m-2 sticky-top">
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
          <li v-for="item in dataMirror">
            <a class="dropdown-item">
              <div class="form-check">
                <input
                  @change="changeSelection"
                  v-model="checked"
                  class="form-check-input we-checked"
                  type="checkbox"
                  :value="item"
                />
                <label class="form-check-label">{{ item }}</label>
              </div>
            </a>
          </li>
          <!-- <li>
                            <hr class="dropdown-divider" />
                        </li> -->
        </ul>
      </div>
    </form>
  </div>
</template>

<script setup>
import { computed, mergeProps, onMounted, reactive, ref, watch } from "vue";

let props = defineProps({
  items: Array,
  title: String,
});

onMounted(() => {
  console.log(props.items.value);
  document.querySelector("#"+props.title).addEventListener("hidden.bs.dropdown", ()=>{
    document.querySelector("#search").value = "";
    searchKeywords.value = "";
  })
});
const emits = defineEmits(["selectionChange"]);
const checked = ref([]);
let searchKeywords = ref("");

let dataMirror = computed({
  get() {
    let keywords = searchKeywords.value.toLocaleLowerCase();
    if (keywords.trim() == "") {
      return props.items;
    } 
    else {
      let searchResult = props.items.filter((item) => {
        let itemValues = Object.values(item).join("").toLocaleLowerCase();
        if (itemValues.includes(keywords)) {
          return item;
        }
      });

      return searchResult;
    }
  },
});
// let dataMirror = ref(originalData);

const changeSelection = () => {
  emits("selectionChange", checked.value);
};

// let search = () => {
//   console.log(searchKeywords.value);
//   let keywords = searchKeywords.value.toLocaleLowerCase();
//   if (keywords.trim() == "") {
//     return props.items.value;
//   } else {
//     console.log(dataMirror);
//     let searchResult = props.items.value.filter((item) => {
//       let itemValues = Object.values(item).join(" ").toLocaleLowerCase();
//       if (itemValues.includes(keywords)) {
//         console.log("FOund " + item);
//         return item;
//       }
//     });
//     console.log(searchResult);
//     // dataMirror = ref(searchResult);
//     console.log(dataMirror);
//     // console.log(props.items);
//     return searchResult;
//   }
// };
</script>

<style scoped>
.card {
  border: none;
  border-top: 5px solid rgb(176, 106, 252);
}

p {
  font-weight: 600;
  font-size: 15px;
}

.btn-primary.show {
  background-color: #3e1271;
  color: white;
}
.dropdown-menu {
  overflow: scroll;
  max-height: 40vh;
}
.division {
  float: none;
  position: relative;
  margin: 30px auto 20px;
  text-align: center;
  width: 100%;
  box-sizing: border-box;
}

.division .line {
  border-top: 1.5px solid #57557a;
  position: absolute;
  top: 13px;
  width: 85%;
}

.division span {
  font-weight: 600;
  font-size: 14px;
}

.myform {
  padding: 0 25px 0 33px;
}

.form-control {
  border: 1px solid #3e1271;
  border-radius: 3px;
  margin-bottom: 20px;
  letter-spacing: 1px;
}

.form-control:focus {
  border-radius: 3px;
  box-shadow: none;
  letter-spacing: 1px;
}

.form-control:focus::placeholder {
  /* Chrome, Firefox, Opera, Safari 10.1+ */
  color: white;
  opacity: 1;
  /* Firefox */
}

.bn {
  text-decoration: underline;
}

.bn:hover {
  cursor: pointer;
}

.form-check-input {
  margin-top: 8px !important;
}

.btn-primary {
  /* background: linear-gradient(135deg, rgba(176, 106, 252, 1) 39%, rgba(116, 17, 255, 1) 101%); */
  border: none;
  border-radius: 50px;
  background: white;
  color: black;
  border: 1px solid black;
  border-radius: 12px;
}

.btn-primary:focus {
  box-shadow: none;
  border: none;
}

small {
  color: #f2ceff;
}

.far.fa-user {
  font-size: 13px;
}

@media (min-width: 767px) {
  .bn {
    text-align: right;
  }
}

@media (max-width: 767px) {
  .form-check {
    text-align: center;
  }

  .bn {
    text-align: center;
    align-items: center;
  }
}

@media (max-width: 450px) {
  .fab {
    width: 100%;
    height: 100%;
  }

  .division .line {
    width: 50%;
  }
}
</style>
