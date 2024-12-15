<template>

  <uploader :options="options" class="uploader-example" ref="uploader" 
        @file-added="fileAdded" @file-error="errorUpload" @file-success="successUpload"
        @file-complete="fileComplete">
    <uploader-unsupport></uploader-unsupport>
    <uploader-drop>
      <p>拖拽文件上传 或</p> <uploader-btn>选择文件</uploader-btn>
      <p class="text-hint"> （请上传.zip格式的压缩文件） </p>
    </uploader-drop>
    <uploader-list></uploader-list>
  </uploader>

  <div id="word-operation">
    <el-row>
      <el-button type="primary" @click="onSubmit" round>提交</el-button>
      <el-button type="success" @click="onDownload" round>保存到本地</el-button>
    </el-row>
  </div>

</template>
 
<script>
export default {
  data() {
    return {
      options: {
        // https://github.com/simple-uploader/Uploader/tree/develop/samples/Node.js
        target: '/upload',
        testChunks: false
      },
    }
  },
  methods: {
    onSubmit() {
      this.axios.post("/analyze", { params: arguments[0] }).then(
        res => {
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

</style>