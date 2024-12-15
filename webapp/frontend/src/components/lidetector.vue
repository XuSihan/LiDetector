<template>
    <div>
        <h2>XXX</h2>
        <div id="word-text-area">
            <el-input 
                type="textarea" :rows="10" placeholder="请输入文本内容" v-model="textarea">
            </el-input>
            <div id="word-img">
                <el-image :src="'data:image/png;base64,'+pic" :fit="fit">
                    <div slot="error" class="image-slot">
                        <i class="el-icon-picture-outline"></i>
                    </div>
                </el-image>
            </div>
            <div id="word-operation">
                <el-row>
                    <el-button type="primary" @click="onSubmit" round>提交</el-button>
                    <el-button type="success" @click="onDownload" round>保存到本地</el-button>
                </el-row>
            </div>
        </div>
    </div>

    <div style="margin-top: 20px">
        <el-upload
        style="float: right"
        class="upload-demo"
        action=""
        multiple=False
        :http-request="uploadFile"
        >
            <el-button size="small" type="primary">点击上传</el-button>
        </el-upload>
    </div>

</template>




<script>
    export default {
        name: 'wordcloud',
        data() {
            return {
                textarea: '',
                pic: "",
                pageTitle: 'Flask Vue Word Cloud',
            }
        },
        methods: {
            onSubmit() {
                var param = {
                    "word": this.textarea
                }
                this.axios.post("/word/cloud/generate", param).then(
                    res => {
                        this.pic = res.data
                        console.log(res.data)
                    }
                ).catch(res => {
                    console.log(res.data.res)
                })
            },
            onDownload() {
                const imgUrl = 'data:image/png;base64,' + this.pic
                const a = document.createElement('a')
                a.href = imgUrl
                a.setAttribute('download', 'word-cloud')
                a.click()
            }
        }
    }
</script>


<style scoped>
    #word-text-area {
        margin-left: 20%;
        margin-right: 20%;
    }
    #word-operation {
        margin-top: 20px;
    }
    #word-img {
        width: 800px;
        height: 300px;
        margin: 20px;
    }
</style>