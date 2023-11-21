<script>
const data = fetch("")

export default {
  props: ["msg"],
  data() {
    return {
      counter:3,
      userInput:"",
      data:{"name":""}
    }
  },
  methods: {
    increment() {
      this.counter += 1;
    }
  },
  mounted() {
    // fetch("@assets/data.json").then(res =>{
    //   return res.json();
    // }).then(jsonRes => {
    //   this.data = jsonRes;
    // })
    fetch("src/assets/data.json").then(res => {
      return res.json()
    }).then(jsonRes => {
      this.data = jsonRes;
    })
  }
}


</script>

<template>
  <div class="greetings">
    <h1 class="green">{{ msg }}</h1>
    <h2>{{ counter }}</h2>
    <button @click="increment">Increment</button>
    <input v-model="userInput" type="text" placeholder="text" class="form-control">
    <p>{{ userInput }}</p>
    <h3>{{ data['name'] }}</h3>
    <h3>
      You’ve successfully created a project with
      <a href="https://vitejs.dev/" target="_blank" rel="noopener">Vite</a> +
      <a href="https://vuejs.org/" target="_blank" rel="noopener">Vue 3</a>.
    </h3>
  </div>
</template>

<style scoped>
h1 {
  font-weight: 500;
  font-size: 2.6rem;
  top: -10px;
}

h3 {
  font-size: 1.2rem;
}

.greetings h1,
.greetings h3 {
  text-align: center;
}

@media (min-width: 1024px) {
  .greetings h1,
  .greetings h3 {
    text-align: left;
  }
}
</style>
