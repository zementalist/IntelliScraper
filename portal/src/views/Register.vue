<template>
    <div class="container">
        <div class="row d-flex justify-content-center mt-5">
            <div class="col-12 col-md-8 col-lg-6 col-xl-5">
                <div class="card py-3 px-2 we-background-color">
                    <div class="division">
                        <div class="row text-center">
                            <div class="col-12">
                                <div class="display-3">Register</div>
                            </div>
                        </div>
                    </div>
                    <form class="myform">
                        <div class="form-group">
                            <input type="text" class="form-control we-focus" placeholder="Username">
                        </div>
                        <div class="form-group">
                            <input type="email" class="form-control we-focus" placeholder="Email">
                        </div>
                        <div class="form-group">
                            <input type="password" class="form-control we-focus" placeholder="Password">
                        </div>
                        <div class="form-group">
                            <input type="email" class="form-control we-focus" placeholder="Password Confirmation">
                        </div>
                        <div class="form-group mt-3 justify-content-center text-center">
                            <button type="button" class="btn btn-block btn-primary btn-lg"><small><i
                                        class="far fa-user pr-2"></i>Create Account</small></button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</template>
    
<script>
export default {
    setup() {


        return {}
    }
}
</script>
    
<style scoped>
.card {
    border: none;
    border-top: 5px solid rgb(176, 106, 252);
}

p {
    font-weight: 600;
    font-size: 15px;
}

.division {
    float: none;
    position: relative;
    margin: 30px auto 20px;
    text-align: center;
    width: 100%;
    box-sizing: border-box;
}

.division .line {
    border-top: 1.5px solid #57557A;
    ;
    position: absolute;
    top: 13px;
    width: 85%;
}

.division span {
    font-weight: 600;
    font-size: 14px;
}

.myform {
    padding: 0 25px 0 33px;
}

.form-control {
    border: 1px solid #57557A;
    border-radius: 3px;
    margin-bottom: 20px;
    letter-spacing: 1px;

}

.form-control:focus {
    border: 1px solid #57557A;
    border-radius: 3px;
    box-shadow: none;
    letter-spacing: 1px;
}

.form-control:focus::placeholder {
    /* Chrome, Firefox, Opera, Safari 10.1+ */
    color: white;
    opacity: 1;
    /* Firefox */
}

.bn {
    text-decoration: underline;
}

.bn:hover {
    cursor: pointer;
}

.form-check-input {
    margin-top: 8px !important;
}

.btn-primary {
    background: linear-gradient(125deg, #3E1261 39%, rgba(116, 17, 255, 1) 101%);
    border: none;
    border-radius: 50px;
}

.btn-primary:focus {
    box-shadow: none;
    border: none;
}

small {
    color: #F2CEFF;
}

.far.fa-user {
    font-size: 13px;
}

@media(min-width: 767px) {
    .bn {
        text-align: right;
    }
}

@media(max-width: 767px) {
    .form-check {
        text-align: center;
    }

    .bn {
        text-align: center;
        align-items: center;
    }
}

@media(max-width: 450px) {
    .fab {
        width: 100%;
        height: 100%;
    }

    .division .line {
        width: 50%;
    }
}</style>