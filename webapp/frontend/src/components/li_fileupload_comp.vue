<template>

    <uploader :options="options" class="uploader-example" :fileStatusText="fileStatusText" :autoStart="autoStart"
        ref="uploader" 
        @file-added="fileAdded" @file-error="errorUpload" @file-success="successUpload"
        @file-complete="fileComplete">

        <uploader-unsupport></uploader-unsupport>
        <uploader-drop>
            <div style="height: 10rem" class="flex a-c j-c">
                <div style="text-align: center">
                    <i class="fas fa-upload" style="font-size: 2rem; color: #00bbff"></i>
                    <div>拖动上传</div>
                </div>
            </div>

            <!-- <uploader-btn>选择文件</uploader-btn> -->
            <div class="flex j-c">
                <uploader-btn >上传文件</uploader-btn>
                <uploader-btn :directory="true">上传文件夹</uploader-btn>
            </div>

        </uploader-drop>
        <uploader-list></uploader-list>

    </uploader>

</template>



<script>
export default {

    data() {
        return {
            options: {
                //上传地址
                target: "http://localhost:50000/upload", //对upload的post请求
                //uploadMethod: "POST",

                testChunks: false,

                // 请求接口的参数名
                fileParameterName: "file",

                //请求头
                // headers: {
                //   "Content-Type": "multipart/form-data;charset=UTF-8",
                // },

                // // 单文件上传
                // singleFile: true,

                // 上传文件会自动分块
                chunkSize: 1024 * 1024 * 1, //每块大小
                simultaneousUploads: 5, //并发上传块数

                //处理接口的响应
                processResponse: function (response, cb, file, chunk) {
                    //调用cb()回调函数,续传文件未上传的片段
                    //当为最后一个片段时,不再调用该回调函数
                    if (chunk.endByte < file.size || chunk.endByte < file.size) {
                        cb();
                    } else {

                        this.currentId = JSON.parse(response).id;
                        console.log(this.currentId);
                    }
                },
                maxChunkRetries: 0,
                processParams: function (params) {
                    params.aa = 11;
                    // console.log(params);
                    return params;
                },

                parseTimeRemaining: function (timeRemaining, parsedTimeRemaining) {
                    return parsedTimeRemaining
                        .replace(/\syears?/, "年")
                        .replace(/\days?/, "天")
                        .replace(/\shours?/, "小时")
                        .replace(/\sminutes?/, "分钟")
                        .replace(/\sseconds?/, "秒");
                },
            },
            fileStatusText: {
                success: "上传成功",
                error: "上传失败",
                uploading: "上传中...",
                paused: "暂停",
                waiting: "等待中...",
                cmd5: "cmd5",
            },
        }
    },


    methods: {
        fileAdded(file) {
            // window.uploader.removeFile(file);
        },

        successUpload() {
            console.log("success");
        },

        errorUpload() {
            this.$message({
                type: "warning",
                message: "上传失败",
                duration: 1000,
            });
        },

        //整个根文件上传结束
        fileComplete(rootFile) {
            console.log('file complete', arguments)

            let url = '//localhost:50000/upload';
            this.$axios.get(url, { params: arguments[0] }) //对upload的get请求
                .then((res) => {
                    console.log(url)
                    if (res.data["statusCode"] == 200) {
                        this.$message.success('上传成功');
                    } else {
                        this.$message.error('上传失败. ' + res.data["message"]);
                        return false
                    }
                }).catch((err) => {
                    this.$message.error('网络异常');
                    console.log(err);
                })
        },

    },


}
</script>



<style>
.uploader-example {
    width: 44rem;
    padding: 0.75rem;
    margin: 2rem auto;
    font-size: 0.6rem;
    box-shadow: 0 0 0.5rem rgba(0, 0, 0, 0.4);
}

.uploader-example .uploader-btn {
    margin-right: 0.2rem;
    border: 0;
    color: #009fcc;
    height: 1.715rem;
    border-radius: 0.15rem;
    padding: auto;
}

.uploader-example .uploader-list {
    max-height: 22rem;
    overflow: auto;
    overflow-x: hidden;
    overflow-y: auto;
}
</style>