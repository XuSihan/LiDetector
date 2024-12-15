<template>
  <div class="div_header">

    <b-navbar toggleable="lg" type="dark" variant="info" sticky class="top-menu">

      <b-navbar-brand href="/home" class="li_title">
        <!-- LiDetector -->
        <img v-bind:src="imgUrl_logo" style="max-width: 200px;">
      </b-navbar-brand>

      <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

      <b-collapse id="nav-collapse" is-nav>

        <!-- left aligned nav items -->
        <b-navbar-nav>

          <b-nav-item class="b_nav_bn">
            <router-link to="/home" active-class="active">
              <div class="li_title"  @click="hideLeftMenu">Home</div>
            </router-link>
          </b-nav-item>

          <b-nav-item class="b_nav_bn">
            <router-link to="/upload" active-class="active">
              <div class="li_title"  @click="hideLeftMenu">Upload</div>
            </router-link>
          </b-nav-item>

          <b-nav-item class="b_nav_bn">
            <router-link to="/result" active-class="active">
              <div class="li_title"  @click="showLeftMenu">Result</div>
            </router-link>
          </b-nav-item>

        </b-navbar-nav>

        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto">

          <b-nav-form>
            <b-form-input size="sm" class="mr-sm-2" placeholder="Search"></b-form-input>
            <b-button size="sm" class="my-2 my-sm-0" type="submit">Search</b-button>
          </b-nav-form>

          <b-nav-item-dropdown text="Lang" right>
            <b-dropdown-item href="#">EN</b-dropdown-item>
            <b-dropdown-item href="#">ES</b-dropdown-item>
            <b-dropdown-item href="#">RU</b-dropdown-item>
            <b-dropdown-item href="#">FA</b-dropdown-item>
          </b-nav-item-dropdown>

          <b-nav-item-dropdown right>
            <!-- Using 'button-content' slot -->
            <template #button-content>
              User
            </template>
            <b-dropdown-item href="#">Profile</b-dropdown-item>
            <b-dropdown-item href="#">Sign Out</b-dropdown-item>
          </b-nav-item-dropdown>

        </b-navbar-nav>

      </b-collapse>

    </b-navbar>



    <v-leftHeader v-show="isShowLeftMenu"></v-leftHeader>

  </div>

</template>





<script>
import leftHeader from '@/components/leftHeader.vue'

export default {
  data() {
    return {
      isShowLeftMenu: false,
      imgUrl_logo: "/static/logo2.png",
    }
  },
  methods: {
    showLeftMenu() {

      this.isShowLeftMenu = true

    },
    hideLeftMenu() {
      this.isShowLeftMenu = false
    }
  },
  components: {
    'v-leftHeader': leftHeader,
  }
}
</script>




<style>
.div_header {
  top: 0;
  left: 0;
  right: 0;
}

.li_title {
  font-size: 30px;
  border: 1px solid transparent;
  /* font-weight:bold; */
  color: #FFFFFF;
  font-family:"Rajdhani";
}

/* .top-menu {
  top: 0;
  margin-left: 20%;
  margin-right: 40%;
  height: 60px;
}


.li_title {
  font-size: 20px;
  color: black;
  border: 1px solid transparent;
} */

/* .tm_a {
  float: left;
  width: 100%;
  
  cursor: pointer;
  font-family: "Segoe UI", Segoe, Tahoma, Arial, Verdana, sans-serif;
}
.li_title{
  font-size: 20px;
  color:black;
}

.ul-header {
  top: 0;
  left: 0;
  right: 0;
  height: 40px;
  line-height: 40px;
  z-index: 111;
  margin: 0;
  font-size: 0;
  padding: 0 20px;
} */

.top-menu {
  margin-top: 0%;
  margin-left: 0;
  margin-right: 0;
  /* background-color: rgba(30, 9, 164, 0.5); */
}


/* .tm_a {
  display: inline-block;
  float: left;
  width: 20%;
  font-size: 20px;
  padding: 0 14px;
  margin: 0;
  color: rgba(127, 255, 212, 0.5);
  cursor: pointer;
  font-family: "Segoe UI", Segoe, Tahoma, Arial, Verdana, sans-serif;
}
.li_title{
  color:black;
  border-bottom:1px solid grey;
} */ 
</style>