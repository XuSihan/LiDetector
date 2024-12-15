<template>

  <div>


    <div class="start_bn">
      <b-button variant="outline-primary" type="button" @click="getIncomInfo">获得兼容性检测结果</b-button>
    </div>

    <div class="info_table">


      <!-- <div class="info_row">
        <b-row>
          Project Name:  <b>{{repoName}}</b>
        </b-row>
      </div>

      <div class="info_row">
        <b-row>
          Number of Licenses:  <b>{{licenseNum}}</b>
        </b-row>
      </div>

      <div class="info_row">
        <b-row>
          Whether Exists PL:  <b>{{ispl}}</b>
        </b-row>
      </div>

      <div class="info_row">
        <b-row>
          Whether Exists License Incompatibility:  <b>{{isincom}}</b>
        </b-row>
      </div>

      <div class="info_row">
        <b-row>
          Involved License Term(s):  
          <b><div v-for="term in incomterms" :key="term">{{term}}, </div></b>
        </b-row>
      </div> -->


      <div class="info_row">
        <b-row>
          Project Name:  <b>{{repoName}}</b>
        </b-row>
      </div>

      <div class="info_row">
        <b-row>
          Number of Licenses:  <b>{{licenseNum}}</b>
        </b-row>
      </div>

      <div class="info_row">
        <b-row>
          Whether Exists PL:  <b>{{ispl}}</b>
        </b-row>
      </div>

      <div class="info_row">
        <b-row>
          Whether Exists License Incompatibility:  <b>{{isincom}}</b>
        </b-row>
      </div>


      <b-table striped hover sticky-header="500px" :items="items" :fields="fields"></b-table>



    </div>




  </div>


</template>
<script>

export default {

  data() {

    return {

      repoName: "",
      licenseNum: "",
      ispl: "",
      isincom: "",
      reportList: [],

      fields: [
        {key:'A', label:'license A'}, 
        {key:'B', label:'license B'}, 
        {key:'incomterms', label:'terms that exist incompatibility'}, 
      ],
      items: [],

    }

  },
  methods: {

    getIncomInfo() {
      var param = {
        'repoName': this.$repoMsg.repoName
      }
      console.log(param)

      this.axios.post("/result/incomReport", param).then(
        res => {
          this.repoName = res.data['repoName']
          this.licenseNum = res.data['numm']
          this.ispl = res.data['ispl']
          this.isincom = res.data['isincom']
          this.reportList = res.data['reportList']
          this.items = res.data['reportList'] ///
          console.log(res.data)
        }
      ).catch(res => {
        console.log(res.data.res)
      })

    },
  }

}

</script>


<style>
.info_row {
  margin-top: 1%;
  margin-left: 2%;
  text-align: left;
  font-size: 18px;
}
</style>


