<template>
  <div class="div_result">

    <!-- <div class="ul-result">
  
        <div class="left-menu">
  
          <router-link class="lm_a" to="/result/preprocess">
            <p class="li_title">预处理</p>
          </router-link>
  
          <router-link class="lm_a" to="/result/termExtraction">
            <p class="li_title">条款提取</p>
          </router-link>
  
          <router-link class="lm_a" to="/result/attiInference">
            <p class="li_title">极性判别</p>
          </router-link>

          <router-link class="lm_a" to="/result/incomReport">
            <p class="li_title">兼容性</p>
          </router-link>
  
        </div>
  
      </div> -->

    <!-- w-50 h-20 -->

    <div class="left-block">

      <b-navbar-nav tabs vertical fill class="left-menu">

        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>

        <b-nav-item class="b_nav_bn" style="margin-top: 30%; ">
          <router-link to="/result/preprocess" active-class="active">
            <div class="li_title2" @click="forShow1" :style="{'color':title_color_dict[isShow1]}">Data Preprocess</div>
          </router-link>
        </b-nav-item>

        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>

        <b-nav-item class="b_nav_bn" style="margin-top: 30%; ">
          <router-link to="/result/termExtraction" active-class="active">
            <div class="li_title2" @click="forShow2" :style="{'color':title_color_dict[isShow2]}">Term Identification</div>
          </router-link>
        </b-nav-item>

        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>

        <b-nav-item class="b_nav_bn" style="margin-top: 30%; ">
          <router-link to="/result/attiInference" active-class="active">
            <div class="li_title2" @click="forShow3" :style="{'color':title_color_dict[isShow3]}">Attitude Inference</div>
          </router-link>
        </b-nav-item>

        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>

        <b-nav-item class="b_nav_bn" style="margin-top: 30%; ">
          <router-link to="/result/incomReport" active-class="active">
            <div class="li_title2" @click="forShow4" :style="{'color':title_color_dict[isShow4]}"  >Incomp Detection</div>  
          </router-link>
        </b-nav-item>

        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>
        <div class="li_title2"></div>

        <b-nav-item class="b_nav_bn" style="margin-top: 40%; ">
          <!-- <router-link to="/result/incomReport" active-class="active">
            <div class="li_title2" @click="forShow4">Incomp Detection</div>
          </router-link> -->
        </b-nav-item>

      </b-navbar-nav>


    </div>


    <!-- <b-card no-body>
      <b-tabs pills card vertical>

        <b-tab title="Tab 1" active><b-card-text>Tab contents 1</b-card-text></b-tab>
        <b-tab title="Tab 2"><b-card-text>Tab contents 2</b-card-text></b-tab>
        <b-tab title="Tab 3"><b-card-text>Tab contents 3</b-card-text></b-tab>

      </b-tabs>
    </b-card> -->

    <div class="alert_block">
      <b-alert variant="warning" v-model="isRepoNotUploaded" dismissible >请上传测试项目再查看结果！</b-alert>
    </div>

    


    <Preprocess v-show="isShow1"></Preprocess>
    <TermExtraction v-show="isShow2"></TermExtraction>
    <AttiInference v-show="isShow3"></AttiInference>
    <IncomReport v-show="isShow4"></IncomReport>



  </div>
</template>




<script>
import Preprocess from '@/components/preprocess'
import TermExtraction from '@/components/termExtraction'
import AttiInference from '@/components/attiInference'
import IncomReport from '@/components/incomReport'

export default {

  data() {
    return {
      isRepoNotUploaded: false,
      isShow1: false,
      isShow2: false,
      isShow3: false,
      isShow4: false,
      title_color_dict:{
        true: '#000000',
        false:'#FFFFFF',
      },
    }
  },

  methods: {

    forShow1() {
      if (this.$repoMsg){
        this.isShow1 = true
      this.isShow2 = false
      this.isShow3 = false
      this.isShow4 = false
      }
      else{
        this.isRepoNotUploaded = true
      }
    },

    forShow2() {
      if (this.$repoMsg){
        this.isShow1 = false
      this.isShow2 = true
      this.isShow3 = false
      this.isShow4 = false
      }
      else{
        this.isRepoNotUploaded = true
      }
      
    },
    forShow3() {
      if (this.$repoMsg){
        this.isShow1 = false
      this.isShow2 = false
      this.isShow3 = true
      this.isShow4 = false
      }
      else{
        this.isRepoNotUploaded = true
      }
      
    },
    forShow4() {
      if (this.$repoMsg){
        this.isShow1 = false
      this.isShow2 = false
      this.isShow3 = false
      this.isShow4 = true
      }
      else{
        this.isRepoNotUploaded = true
      }
      
    }

  },

  components: {
    Preprocess, TermExtraction, AttiInference, IncomReport
  }
}
</script>





<style>
.div_result {
  top: 0;
  left: 0;
}

.left-block{
  /* position:fixed; */
  margin-left: 0%;
  margin-top: 0%;
  width: 20%;
  height: 100%;
  /* height: 100%; */
  /* height:1000px; */
  background-color: #17a2b8;
}

.left-menu {
  float: left;
  margin-left: 0%;
  margin-top: 0%;
  width: 100%;
  /* height: 100%; */
  border: 1px solid transparent;
  background-color: #17a2b8;
}

.li_title2 {
  font-size: 25px;
  border: 1px solid transparent;
  /* font-weight:bold; */
  color: #FFFFFF;
  font-family: "Rajdhani";
}

.alert_block{
  display: block;
  width: 50%;
}

</style>