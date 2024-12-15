<template>

  <div id='bgImg'>
    <div class="bgMask">
      <div id="app">
        <v-topHeader></v-topHeader>
        <router-view />
      </div>
    </div>

  </div>

</template>




<script>
import topHeader from '@/components/topHeader.vue'


export default {
  name: "App",
  components: {
    'v-topHeader': topHeader,
  }

}
</script>



<style>
#app {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  /*color: rgba(255, 255, 255, 1);*/
  /* margin-top: 5%; */
  margin-top: 0px;
  margin-bottom: 0%;
  margin-left: 0%;
  margin-right: 0%;
  /* background: url('@/assets/oss.jpg'); */
}

body,
html {
  box-sizing: border-box;
  /* background:rgba(255, 255, 255, 1); */
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  margin: 0;
  padding: 0;
  border: 0;
}

/* #bgImg {
  background: url("assets/oss.jpg");
  width: 100%;
  height: 100%;
  position: fixed;
  background-size: 100% 100%;
}
 */
 .bgMask {
  background-color: rgba(23, 162, 184,0.25);
  width: 100%;
  height: 100%;
  position: fixed;
  background-size: 100% 100%;
}

</style>
