<template>
  <div id="app">
    <h1>Test - czy to działa?</h1>
    <p>Jeśli widzisz ten tekst, Vue działa!</p>
    <router-view />
  </div>
</template>

<script setup>
console.log('App.vue loaded!')
</script>

<style>
body {
  margin: 0;
  padding: 20px;
  font-family: Arial, sans-serif;
}

#app {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
