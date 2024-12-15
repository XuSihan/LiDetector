<template>

  <div>

    <!-- <b-row >
    
      <div class="start_bn">
        <b-button variant="outline-primary" type="button" @click="getSents">点击获取条款实体识别的结果</b-button>
      </div>
    
    </b-row> -->

    



    <div class="TE_row">
    <b-row no-gutters  >
      <!-- no-gutters style="{width: 100%;}"-->

      <b-col md="8">

        <div style="{margin-left: 2%;}">
          <!-- class="start_bn" -->
          <b-button variant="outline-primary" type="button" @click="getSents">点击获取条款实体识别的结果</b-button>
        </div>

        <div class="info_table_1 multiSent">

          <div v-for="sent in sentList" :key="sent">

            <div class="oneSent">

              <b-button-group v-for="item in sent" :key="item">

                <b-button variant="light" class="item_bn" :style="{'backgroundColor':color_dict[item.type]}">
                  {{item.word}}
                </b-button>

              </b-button-group>

            </div>

            <br>


          </div>

        </div>


      </b-col>


      <b-col md="1"></b-col>


      <b-col md="2">

        <div class="info_table_2 multiSent_2">

          <div v-for="sent2 in sentList2" :key="sent2">

            <div class="oneSent_2">

              <b-button-group v-for="item2 in sent2" :key="item2">

                <b-button variant="info" class="item_bn" :style="{'backgroundColor':color_dict[item2.type]}">
                  {{item2.word}}
                </b-button>

              </b-button-group>

            </div>

            <br>


          </div>

        </div>

      </b-col>

      <b-col md="1"></b-col>

    </b-row>
    </div>











  </div>


</template>



<script>


export default {

  data() {
    return {
      sentList: [],
      color_dict: {
        "-1": '#F0F0F0',
        "0": '#000099',
        "1": '#336633',
        "2": '#660066',
        "3": '#003333',
        "4": '#663300',
        "5": '#003300',
        "6": '#993333',
        "7": '#666600',
        "8": '#CCCC00',
        "9": '#99CC33',
        "10": '#FFCC00',
        "11": '#CC0066',
        "12": '#330000',
        "13": '#CC6600',
        "14": '#996633',
        "15": '#FFFF00',
        "16": '#666666',
        "17": '#336666',
        "18": '#990000',
        "19": '#660066',
        "20": '#FF6666',
        "21": '#663366',
        "22": '#330000',
      },
    
      sentList2: [
        [{"word": "Distribute", "type": '0'},],
        [{"word": "Modify", "type": '1'},],
        [{"word": "Commercial Use", "type": '2'},],
        [{"word": "Hold Liable", "type": '3'},],
        [{"word": "Include Copyright", "type": '4'},],

        [{"word": "Include License", "type": '5'},],
        [{"word": "Sublicense", "type": '6'},],
        [{"word": "Use Trademark", "type": '7'},],
        [{"word": "Private Use", "type": '8'},],
        [{"word": "Disclose Source", "type": '9'},],

        [{"word": "State Changes", "type": '10'},],
        [{"word": "Place Warranty", "type": '11'},],
        [{"word": "Include Notice", "type": '12'},],
        [{"word": "Include Original", "type": '13'},],
        [{"word": "Give Credit", "type": '14'},],

        [{"word": "Use Patent Claims", "type": '15'},],
        [{"word": "Rename", "type": '16'},],
        [{"word": "Relicense", "type": '17'},],
        [{"word": "Contact Author", "type": '18'},],
        [{"word": "Include Install Instructions", "type": '19'},],

        [{"word": "Compensate for Damages", "type": '20'},],
        [{"word": "Statically Link", "type": '21'},],
        [{"word": "Pay Above Use Threshold", "type": '22'},],
      ],

    }
  },

  // created() {
  //   this.getSents()
  // },

  methods: {

    getSents() {
      // 请求返回sentList = list[ list[dict] ]      dict:{word, type, }
      // this.sentList = [
      //   [
      //     { "word": "We", "type": "-1" },
      //     { "word": "grant", "type": "-1" },
      //     { "word": "you", "type": "-1" },
      //     { "word": "copy", "type": "0" },
      //     { "word": "this", "type": "0" },
      //     { "word": "work", "type": "0" },
      //   ],
      //   [
      //     { "word": "We", "type": "-1" },
      //     { "word": "grant", "type": "-1" },
      //     { "word": "you", "type": "-1" },
      //     { "word": "modify", "type": "1" },
      //     { "word": "the", "type": "1" },
      //     { "word": "license", "type": "1" },
      //   ],

      // ]
      //
      var param = {
        'repoName': this.$repoMsg.repoName
      }
      console.log(param)

      this.axios.post("/result/termExtraction", param).then(
        res => {
          this.sentList = res.data
          console.log(res.data)
        }
      ).catch(res => {
        console.log(res.data.res)
      })



    },

  },

}

</script>




<style>


.TE_row{
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

/* .start_bn{
    position:fixed;
    margin-top: 1%;
    margin-left: 15%;

} */

/* .info_table{
    margin-left: 20%;
    margin-right: 5%;
    height: 100%;
    background-color: rgb(229, 221, 221);
} */
.info_table_1{
    margin-top: 10px;
    text-align: center;
    display: block;
    /* width: 100%; */
    margin-left: 2%;
}

.multiSent {
  overflow: scroll;
  height: 700px;
  /* max-width:1400px; */
  width: 100%;
}

.oneSent {
  display: block;
  text-align: left;
}

.item_bn {
  border: 1px solid transparent;
}





.info_table_2{
    margin-top: 10px;
    text-align: center;
    display: block;
    /* width: 25%; */
    margin-left: 10%;
}

.multiSent_2 {
  overflow: scroll;
  height: 750px;
  /* max-width:1400px; */
  /* width: 25%; */
}

.oneSent_2 {
  display: block;
  text-align: left;
}
</style>







