/* ==========================================
   VOICESHIELD AI LOGIN
========================================== */

const loginForm =
    document.getElementById("loginForm");

const nameInput =
    document.getElementById("name");

const emailInput =
    document.getElementById("email");

const passwordInput =
    document.getElementById("password");

const showPassword =
    document.getElementById("showPassword");

const loginButton =
    document.getElementById("loginButton");

const buttonText =
    document.getElementById("buttonText");

const loader =
    document.getElementById("loader");

const arrow =
    document.querySelector(".arrow");


/* ==========================================
   SHOW / HIDE PASSWORD
========================================== */

showPassword.addEventListener("click", function () {

    if (passwordInput.type === "password") {

        passwordInput.type = "text";

        showPassword.textContent = "🙈";

    } else {

        passwordInput.type = "password";

        showPassword.textContent = "👁";
    }

});


/* ==========================================
   LOGIN
========================================== */

loginForm.addEventListener("submit", function (event) {

    event.preventDefault();

    clearErrors();


    const name =
        nameInput.value.trim();

    const email =
        emailInput.value.trim();

    const password =
        passwordInput.value;


    let valid = true;


    /* NAME */

    if (name.length < 2) {

        document.getElementById("nameError")
            .textContent =
            "Please enter your name.";

        valid = false;
    }


    /* EMAIL */

    const emailPattern =
        /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    if (!emailPattern.test(email)) {

        document.getElementById("emailError")
            .textContent =
            "Enter a valid email address.";

        valid = false;
    }


    /* PASSWORD */

    if (password.length < 6) {

        document.getElementById("passwordError")
            .textContent =
            "Password must be at least 6 characters.";

        valid = false;
    }


    if (!valid) {

        return;
    }


    /* ======================================
       LOGIN LOADING
    ====================================== */

    loginButton.disabled = true;

    buttonText.style.display = "none";

    arrow.style.display = "none";

    loader.style.display = "block";


    /* ======================================
       SAVE USER
    ====================================== */

    const user = {

        name: name,

        email: email

    };


    sessionStorage.setItem(
        "voiceShieldUser",
        JSON.stringify(user)
    );


    /* ======================================
       OPEN INDEX1.HTML
    ====================================== */

    setTimeout(function () {

        window.location.href =
            "index1.html";

    }, 1000);

});


/* ==========================================
   CLEAR ERRORS
========================================== */

function clearErrors() {

    document.getElementById("nameError")
        .textContent = "";

    document.getElementById("emailError")
        .textContent = "";

    document.getElementById("passwordError")
        .textContent = "";
}


/* ==========================================
   FORGOT PASSWORD
========================================== */

function forgotPassword(event) {

    event.preventDefault();

    alert(
        "🔐 Frontend Demo\n\n" +
        "Password recovery is not connected " +
        "to a backend yet."
    );
}