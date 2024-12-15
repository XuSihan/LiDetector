<template>
    <div class="div_main">



        <h1 class="title_h2">
            LiDetector

        </h1>

        <div style="font-size=20px; text-align: left; margin-left: 10%;">
            (our paper has been accepted by TOSEM 2022, click <a href="https://dl.acm.org/doi/10.1145/3518994">
                here
            </a> to learn more ...)
        </div>



        <div>

            <!-- <b-carousel id="carousel-1" v-model="slide" :interval="4000" controls indicators background="#ababab"
                img-width="1024" img-height="480" style="text-shadow: 1px 1px 2px #000000; margin-top: 2%;" >

                <b-carousel-slide :img-src="imgUrl1" >
                    <h1 class="img_text">overview</h1>
                </b-carousel-slide>

                <b-carousel-slide :img-src="imgUrl2">
                    <h1 class="img_text">author</h1>
                </b-carousel-slide>

            </b-carousel> -->

            <!-- <div class="bgMask">
                <img v-bind:src="imgUrl">
            </div> -->


            <b-card no-body class="overflow-hidden"
                style="max-width: 2000px;background-color: rgba(23, 162, 184,0.0); margin-top: 1%; border: 1px solid transparent;">

                <b-row no-gutters>

                    <b-col md="8">

                        <b-card-img :src="imgUrl1" alt="Image" class="wrap">
                            <!-- <div class="bgMask2"></div> -->
                        </b-card-img>


                    </b-col>

                    <b-col md="4">
                        <b-card-body title="">
                            <b-card-text>
                                <h2 class="img_text">
                                    <b>LiDetector</b> <br>
                                    an effective tool to extract and interpret OSS licenses, and to detect license
                                    incompatibility.
                                </h2>

                            </b-card-text>
                        </b-card-body>
                    </b-col>

                </b-row>
                
            </b-card>




        </div>




        <div class="mt-3" style="display: flex; margin-top: 5%; justify-content: center; ">

            <b-card-group deck style="max-width: 1600px;">

                <b-card bg-variant="info" text-variant="white" class="text-center" header-tag="header1"
                    header="Information Collection">

                    <!-- <template #header1>
                        <h6 class="mb-0">Information Collection</h6>
                    </template> -->

                    <b-card-text>
                        <div class="small_card_text">
                            Help you collect license-related information in you OSS projects, mainly in three forms
                            (Declared, Inline, Referenced).
                        </div>

                    </b-card-text>

                </b-card>

                <b-card bg-variant="info" text-variant="white" header="License Comprehension" class="text-center">
                    <b-card-text class="small_card_text">
                        Model and Interpret OSS licenses (both official licenses and custom licenses), by term entity
                        extraction and term attitude inference.
                    </b-card-text>
                </b-card>

                <b-card bg-variant="info" text-variant="white" header="Compliance report" class="text-center">
                    <b-card-text class="small_card_text">
                        Detect license incompatibility among these licenses based on much knowledge on open source
                        software license related work.
                    </b-card-text>
                </b-card>

            </b-card-group>

        </div>


        <!-- <div>

            <b-card no-body class="overflow-hidden" style="max-width: 2000px;background-color: rgba(23, 162, 184,0.05); margin-top: 5%; ">
                <b-row no-gutters>

                    <b-col md="4">
                        <b-card-body title="">
                            <b-card-text>
                                <h2 class="img_text">
                                    <b>LiDetector</b> <br>
                                    an effective tool that extracts and interprets OSS licenses, and detects license incompatibility.
                                </h2>

                            </b-card-text>
                        </b-card-body>
                    </b-col>

                    <b-col md="8">

                        <b-card-img :src="imgUrl1" alt="Image" class="wrap">
                        </b-card-img>


                    </b-col>

                    

                </b-row>
            </b-card>

        </div> -->





        <footer class="footer">
            <div class="container">
                <div class="row pt-5 pl-5 pr-5 responsive-footer" style="display: flex; justify-content: center; ">
                    
                    <div class="col-md-2">
                        <h5 class="footer-title">About us</h5>
                        <ul class="nav flex-column list-unstyled">
                            <li class="nav-item"><a href="#">Blog</a></li>
                            <li class="nav-item"><a href="#">About Us</a></li>
                            <li class="nav-item"><a href="#" target="_blank">Contact us</a>
                            </li>

                        </ul>
                    </div>

                    <div class="col-md-2">
                        <h5 class="footer-title">More Info</h5>
                        <ul class="nav flex-column list-unstyled">
                            <li class="nav-item"><a
                                    href="#"
                                    target="_blank">Submit product</a></li>
                        </ul>
                    </div>

                    <div class="col-md-2">
                        <h5 class="footer-title">Special Thanks</h5>
                        <ul class="nav flex-column list-unstyled">
                            <li class="nav-item"><a href="https://bootstrap-vue.org/" target="_blank">sites framework</a></li>
                            <li class="nav-item"><a href="https://stanfordnlp.github.io/CoreNLP/" target="_blank">Stanford CoreNLP</a></li>
                        </ul>
                    </div>

                    <div class="col-md-3">
                        <h5 class="footer-title">Useful Links</h5>
                        <ul class="nav flex-column list-unstyled">
                            <li class="nav-item"><a target="_blank" href="https://opensource.org/licenses">OSI-approved</a></li>
                            <li class="nav-item"><a target="_blank" href="https://spdx.org/licenses/">SPDX List</a></li>
                            <li class="nav-item"><a target="_blank" href="https://tldrlegal.com/licenses/browse">tldrlegal</a></li>
                        </ul>
                    </div>

                </div>

                <hr>
                <div class="social-area ml-auto mr-auto">
                    <ul class="footer-social ml-auto mr-auto justify-content-center">
                        <li class="nav-item">
                            <a href="https://github.com/expojs/vuejsexpo" target="_blank" class="nav-link"><i
                                    class="fab fa-github"></i></a>
                        </li>
                        <li class="nav-item">
                            <a href="https://vuejsexpo.com/rss/" target="_blank" class="nav-link"><i
                                    class="fa fa-rss"></i></a>
                        </li>
                    </ul>
                    <p class="text-center">Copyright © 2020 VueJSExpo. All Rights Reserved.</p>
                </div>

            </div>
        </footer>






    </div>


</template>




<script>
import overview from '../assets/overview.jpg'
import author from '../assets/author.jpg'


export default {
    data() {
        return {
            imgSrc_overview: overview,
            imgSrc_author: author,
            imgUrl1: "/static/overview2.jpg",
            imgUrl2: "/static/author.jpg",
        }
    },
    methods: {
    }
}
</script>


<style scoped>
.div_main {
    float: top;
    /* overflow: scroll; */
}

.title_h2 {
    float: top;
    margin-top: 2%;
    margin-left: 10%;
    color: rgb(18, 6, 45);
    font-family: "Rajdhani";
    size: 30px;
    text-align: left;
}

.img_text {
    color: rgb(18, 6, 45);
    size: 20px;
    line-height: 52px;
    margin-top: 10%;
    text-align: left;
    font-family: "Rajdhani";
}

.small_card_text {
    color: rgb(13, 22, 43);
    font-size: 20px;
    line-height: 30px;
    margin-top: 2%;
    text-align: left;
    font-family: "Rajdhani";
}

.bgMask2 {
    background-color: rgba(23, 162, 184, 0.2);
    width: 100%;
    height: 100%;
}


.footer {
    display: block;
    background-color: #17a2b8;
    padding-top: 1px;
    margin-top: 3%;
}

.footer .made-with-react,
.footer .vuejs-expo {
    /* To correctly align image, regardless of content height: */
    vertical-align: top;
    display: inline-block;
    /* To horizontally center images and caption */
    text-align: center;
    /* The width of the container also implies margin around the images. */
    width: 140px;
}

.footer .made-with-react .float-buttons,
.footer .vuejs-expo .float-buttons {
    display: block;
    background-color: #FFFFFF;
    border-radius: 50%;
    box-shadow: 0 15px 30px 0 rgba(48, 54, 77, 0.1);
    height: 80px;
    width: 80px;
}

.footer .made-with-react .float-buttons img,
.footer .vuejs-expo .float-buttons img {
    width: 65px;
    margin-top: 7px;
}

.footer .made-with-react .text-float-buttons,
.footer .vuejs-expo .text-float-buttons {
    font-weight: bold;
    font-size: 18px;
}

.footer .footer-title {
    font-size: 18px;
    font-weight: bold;
    color: #223464;
}

.footer .footer-text {
    color: #223464;
}

.footer .footer-img {
    width: 20px;
    height: 20px;
    margin: 0;
}

.footer .social-area {
    max-width: 400px;
    display: block;
    padding-bottom: 16px;
}

.footer .social-area .footer-social {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
}

.footer .social-area p {
    color: #223464;
    font-weight: lighter;
    margin: 0;
}

.footer .nav .nav-item {
    padding: 3px 0;
}

.footer .nav .nav-item a {
    text-transform: uppercase;
    color: #223464;
}

.footer .special-thanks {
    color: #223464;
    margin: 30px 0;
}
</style>








