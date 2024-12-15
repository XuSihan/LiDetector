<template>

  <div>

    <div class="start_bn">
      <b-button variant="outline-primary" type="button" @click="getAttis">获得极性分析结果</b-button>
    </div>

    <div class="info_table">
      <b-table striped hover sticky-header="700px" :items="items" :fields="fields" >


        <template #cell(id)="data">
          <i>{{ data.value }}</i>
        </template>

        <template #cell()="data">
          <b-icon :icon=icon_style[data.value] :variant=icon_color[data.value] ></b-icon>
        </template>


      </b-table>
    </div>


  </div>

</template>




<script>
export default {
  data() {
    return {
      fields: ['id',
        //  {
        //   key:'Distribute', //0
        //   formatter: 'label_to_icon',
        //  },
        'Distribute', //0
        'Modify', //1
        'Commercial Use', //2
        'Hold Liable', //3
        'Include Copyright',//4
        'Include License', //5
        'Sublicense', //6
        'Use Trademark', //7
        'Private Use', //8
        'Disclose Source', //9
        'State Changes', //10
        'Place Warranty', //11
        'Include Notice', //12
        'Include Original', //13
        'Give Credit',//14
        'Use Patent Claims', //15
        'Rename', //16
        'Relicense', //17
        'Contact Author', //18
        'Include Install Instructions', //19
        'Compensate for Damages', //20
        'Statically Link', //21
        'Pay Above Use Threshold', //22
      ],
      items: [],

      icon_style:{
        1:"check-square",
        2:"x-circle",
        3:"exclamation-triangle",
      },
      icon_color:{
        1:"success",
        2:"danger",
        3:"warning",
      },

    }
  },
  methods: {

    getAttis() {

      var param = {
        'repoName': this.$repoMsg.repoName
      }
      console.log(param)

      this.axios.post("/result/attiInference", param).then(
        res => {
          this.items = res.data
          console.log(res.data)
        }
      ).catch(res => {
        console.log(res.data.res)
      })

    },

    label_to_icon(value) {
      //return `${value.first} ${value.last}`
      if (value == 1) {
        return <b-icon icon="check-square" variant="success"></b-icon>
      }
      if (value == 2) {
        return <b-icon icon="x-circle" variant="danger"></b-icon>
      }
      if (value == 3) {
        return <b-icon icon="exclamation-triangle" variant="warning"></b-icon>
      }
    },

  },


  components: {

  }
}
</script>



<style>

/* .start_bn{
    position:fixed;
    margin-top: 1%;
    margin-left: 15%;

} */

/* .info_table {
  margin-left: 20%;
  margin-right: 5%;
  height: 100%;
} */


</style>


