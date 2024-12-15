<template>

  <div>

    <uploader :options="options" class="uploader-example" ref="uploader" @file-added="fileAdded"
      @file-error="errorUpload" @file-success="successUpload" @file-complete="fileComplete">
      <uploader-unsupport></uploader-unsupport>
      <uploader-drop>
        <p>Drop files, or</p>
        <uploader-btn>choose files (uploaded automatically)</uploader-btn>
        <p class="text-hint"> (compressed .zip file please) </p>
      </uploader-drop>
      <uploader-list></uploader-list>
    </uploader>

    <div style="max-width: 2000px; display: flex; margin-top: 3%; justify-content: center; ">

      <b-form >

        <b-form-group id="input-group-2" label="repo name:" label-for="input-2">
          <b-form-input id="input-2" v-model="form_reponame" placeholder="Enter repo name" required></b-form-input>
        </b-form-group>


        <b-button variant="outline-primary" type="button" @click="beginAnalyze" style="margin-top: 3%; ">Start analyze</b-button>

      </b-form>

    </div>


    <!-- <b-button variant="outline-primary" type="button" @click="testAlertShow">(手动赋值试一下show)</b-button> -->

    <!-- <b-alert variant="success" v-show="isStartAnalyze">上传成功，开始分析：{repoName}</b-alert> -->
    <!-- <b-alert variant="success" show>（fixed）上传成功，开始分析：{{repoName}}</b-alert> -->

    

    <div class="alert_block">
      <b-alert variant="success" v-model="isStartAnalyze" dismissible >上传成功，开始分析：{{repoName}}</b-alert>
    </div>

    <div class="alert_block">
      <b-alert variant="warning" v-model="isStartFail" dismissible >请填写项目名称再提交！</b-alert>
    </div>
    
    <div class="alert_block">
      <b-alert variant="warning" v-model="isAnalyzeFail" dismissible >请填写正确的项目名称！</b-alert>
    </div>

    

  </div>


</template>
   
<script>
import Vue from 'vue'

export default {
  data() {
    return {
      options: {
        // https://github.com/simple-uploader/Uploader/tree/develop/samples/Node.js
        target: '/upload',
        testChunks: false
      },
      isStartAnalyze: false,
      repoName: "",
      repoNamesent: "",
      isStartFail: false,
      isAnalyzeFail: false,
      form_reponame: '',
    }
  },
  methods: {

    beginAnalyze() {
      //###

      if (this.form_reponame==''){
        this.isStartFail = true
      }
      else{

        var param = {
        "form_reponame": this.form_reponame
      }
      this.axios.post('/analyze', param) //对analyze的get请求
        .then(
          res => {
            //console.log('开始分析： ', res.data["message"])
            console.log('开始分析： ', res.data)
            ///
            if(res.data["status"]=="reponame error"){
              this.isAnalyzeFail = true
            }
            else{

              //
            this.repoName = res.data["repoName"]
            this.isStartAnalyze = true
            ////
            const repoMsg = {
              repoName: this.repoName,
              aaa: '111',
              bbb: '222'
            }
            Vue.prototype.$repoMsg = repoMsg;//将全局变量模块挂载到Vue.prototype中

            //this.$forceUpdate();

            }
            

          }).catch(
            res => {
              console.log(res.data.res)
              //this.isStartFail = true
            }
          )

      }


      
    },
    testAlertShow() {
      this.isStartAnalyze = true
      // 这个测试成功，说明v-model="isStartAnalyze"本身没问题。
    },
    fileComplete() {
      //#

    },

  }
}
</script>
   
<style>
.uploader-example {
  width: 880px;
  padding: 15px;
  margin: 40px auto 0;
  font-size: 12px;
  box-shadow: 0 0 10px rgba(0, 0, 0, .4);
}

.uploader-example .uploader-btn {
  margin-right: 4px;
}

.uploader-example .uploader-list {
  max-height: 440px;
  overflow: auto;
  overflow-x: hidden;
  overflow-y: auto;
}

.text-hint {
  font-size: 10px;
  font-style: oblique;
  color: dimgray;
}

.alert_block{
  /* display: flex;
  justify-content: center; */
  /* width: 800px; */
  margin-top: 80px;
  text-align: center;
  display:inline-block;
}


</style>