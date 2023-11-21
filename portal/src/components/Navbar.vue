<template>
<div class="container-fluid px-0">
    <nav class="navbar navbar-expand-lg navbar-dark we-background-color py-0 px-0">
        <RouterLink to="/" class="navbar-brand"><img src="@/assets/logo.svg" width="64"><strong id="logo-title"><i>IntelliScraper</i></strong></RouterLink>
        <button class="navbar-toggler mr-3 collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
                <li class="nav-item we-hover active">
                    <RouterLink to="/" class="nav-link">Explore</RouterLink>
                    <!-- <a class="nav-link" href="/about">Home</a> -->
                </li>
                <li class="nav-item we-hover">
                    <RouterLink to="/jobs" class="nav-link">Jobs</RouterLink>
                    <!-- <a class="nav-link" href="/about">Home</a> -->
                </li>
                <li class="nav-item we-hover right">
                    <RouterLink to="/login" class="nav-link">Login</RouterLink>
                </li>
                <li class="nav-item we-hover nav-right-margin">
                    <RouterLink to="/register" class="nav-link">Register</RouterLink>
                </li>
            </ul>
        </div>
    </nav>
</div>
</template>

<script setup>
import { onMounted } from 'vue';

onMounted(() => {
    document.querySelectorAll(".nav-item").forEach(element => {
        element.addEventListener("click", () => {
            document.querySelector(".nav-item.active").classList.remove("active");
            element.classList.add('active');
        })
    })
})
</script>

<style scoped>
.navbar {
    box-shadow: #3e1271 -1px -1px 20px 0px;
}
body {
    background-color: #BBDEFB;
}

#logo-title {
    vertical-align: middle;
}
.bg-black { 
    background-color: #000;
}

.navbar-brand {
    padding: 0px 20px;
}


.nav-right-margin {
    margin-right: 20px;
}
.navbar-nav {
    width: 100%;
}

.nav-link {
    color: #fff !important;
    font-size: 1.1em;
}

.nav-item, we-hover {
    padding: 6px 12px;
    text-align: center;
    border-radius: 12px;
    font-weight: 700;
    transition: 0.1s;
}



.right {
    margin-left: auto;
}

.navbar-collapse.collapse.in {
    display: block !important;
}

@media (max-width: 992px) {
    .right {
        margin-left: 0;
    }

    .nav-item we-hover {
        width: 100%;
        text-align: left;
    }
}
</style>