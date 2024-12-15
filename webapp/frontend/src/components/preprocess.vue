<template>

    <div>

        <div class="start_bn">
            <b-button variant="outline-primary" type="button" @click="bgAnalyze" >开始分析</b-button>
        </div>

        <div class="info_table">
            <b-table striped hover sticky-header="700px" :items="items" :fields="fields"></b-table>
        </div>


    </div>

</template>




<script>
export default {
    data() {
        return {
            fields: ['id', 'filepath', 'licenseOriginType', 'matchedLicenses', 'text'],
            items: [
            // {'id': '291', 
            // 'filepath': 'D:\\Python\\LiDetector-webapp\\backend\\data\\repos\\apachecn___ailearning\\apachecn___ailearning\\ailearning-master\\src\\tutorials\\tool\\python2libsvm.py:__future__', 
            // 'licenseOriginType': 'REFERENCED LICENSE', 
            // 'matchedLicenses': "['MIT License', 'MIT-license']", 
            // 'text': ''},

            ],
        }
    },
    methods: {

        bgAnalyze(){

            var param = {
                'repoName': this.$repoMsg.repoName
            }
            console.log(param)

            this.axios.post("/result/preprocess", param).then(
                res => {
                    this.items = res.data
                    console.log(res.data)
                }
            ).catch(res => {
                console.log(res.data.res)
            })

        },

    },
    // computed: {

    //     'items':function(newVal,oldVal){

	// 		var param = {
    //             'repoName': this.$repoMsg.repoName
    //         }
    //         console.log(param)

    //         this.axios.post("/result/preprocess", param).then(
    //             res => {
    //                 //this.items = res.data
    //                 console.log(res.data)
    //                 return res.data
    //             }
    //         ).catch(res => {
    //             console.log(res.data.res)
    //         })

	// 	},

    //     loadTreeImg() {

    //         var param = {
    //             'repoName': this.$repoMsg.repoName
    //         }
    //         console.log(param)

    //         this.axios.post("/result/preprocess", param).then(
    //             res => {
    //                 this.items = res.data
    //                 console.log(res.data)
    //             }
    //         ).catch(res => {
    //             console.log(res.data.res)
    //         })

    //     },

    // },


    components: {

    }
}
</script>

<style>

.start_bn{
    /* float: left; */
    /* margin-top: 10%; */
    /* float: top; */
    /* position:fixed;
    margin-top: 1%;
    margin-left: 15%; */
    margin-top: 0.5%;
    margin-left: 22%;
    text-align: left;
    display: block;

}

.info_table{
    /* padding-top: 2%; */

    /* margin-top: 15%;
    margin-left: 20%;
    margin-right: 5%;
    height: 100%; */

    margin-top: 10px;
    text-align: center;
    display: block;
    width: 70%;
    margin-left: 22%;
}

</style>


