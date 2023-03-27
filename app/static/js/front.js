"use strict";

document.addEventListener("DOMContentLoaded", function () {
    // Main Template Color
    var brandPrimary = "#33b35a";

    // ------------------------------------------------------- //
    // Side Navbar Functionality
    // ------------------------------------------------------ //
    const sidebarToggleBtn = document.getElementById("toggle-btn");
    const sidebar = document.querySelector(".side-navbar");
    const pageHolder = document.querySelector(".page");
    const sidebarHeading = document.querySelectorAll(".side-navbar .heading");
    const navbar = document.querySelector('.navbar.fixed-top')

    if (sidebarToggleBtn) {
        sidebarToggleBtn.addEventListener("click", (e) => {
            e.preventDefault();
            if (window.outerWidth > 1194) {
                sidebar.classList.toggle("shrink");
                pageHolder.classList.toggle("active");
                navbar.classList.toggle('active')
                sidebarHeading.forEach((el) => {
                    el.classList.toggle("mx-lg-2");
                });
            } else {
                sidebar.classList.toggle("show-sm");
                navbar.classList.toggle("active-sm");
            }
        });
    }

    window.addEventListener('resize', function () {
        if (this.outerWidth > 1194) {
            sidebar.classList.remove("show-sm");
            pageHolder.classList.remove("active");
            navbar.classList.remove("active-sm")
        } else {
            sidebar.classList.remove("shrink");
            pageHolder.classList.remove("active");
            navbar.classList.remove('active')
        }
    })


    // ------------------------------------------------------- //
    // Tooltips init
    // ------------------------------------------------------ //
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // ------------------------------------------------------- //
    // Material Inputs
    // ------------------------------------------------------ //

    let materialInputs = document.querySelectorAll("input.input-material");
    let materialLabel = document.querySelectorAll("label.label-material");

    // activate labels for prefilled values
    let filledMaterialInputs = Array.from(materialInputs).filter(function (input) {
        return input.value !== "";
    });
    filledMaterialInputs.forEach((input) =>
        input.parentElement.lastElementChild.setAttribute("class", "label-material active")
    );

    // move label on focus
    materialInputs.forEach((input) => {
        input.addEventListener("focus", function () {
            input.parentElement.lastElementChild.setAttribute("class", "label-material active");
        });
    });

    // remove/keep label on blur
    materialInputs.forEach((input) => {
        input.addEventListener("blur", function () {
            if (input.value !== "") {
                input.parentElement.lastElementChild.setAttribute("class", "label-material active");
            } else {
                input.parentElement.lastElementChild.setAttribute("class", "label-material");
            }
        });
    });

    function bsValidationBehavior(errorInputs, form) {
        function watchError() {
            errorInputs.forEach((input) => {
                if (input.classList.contains("js-validate-error-field")) {
                    input.classList.add("is-invalid");
                    input.classList.remove("is-valid");
                } else {
                    input.classList.remove("is-invalid");
                    input.classList.add("is-valid");
                }
            });
        }
        watchError();
    }

    // ------------------------------------------------------- //
    // Login Form Validation
    // ------------------------------------------------------ //
    let loginForm = document.querySelector(".login-form");
    if (loginForm) {
        new window.JustValidate(".login-form", {
            rules: {
                loginUsername: {
                    required: true,
                    email: true,
                },
                loginPassword: {
                    required: true,
                },
            },
            messages: {
                loginUsername: "Please enter a valid email",
                loginPassword: "Please enter your password",
            },
            invalidFormCallback: function () {
                let errorInputs = document.querySelectorAll(".login-form input[required]");
                bsValidationBehavior(errorInputs, loginForm);
                loginForm.addEventListener("keyup", () => bsValidationBehavior(errorInputs, loginForm));
            },
        });
    }

    // ------------------------------------------------------- //
    // Register Form Validation
    // ------------------------------------------------------ //
    let registerForm = document.querySelector(".register-form");
    if (registerForm) {
        new window.JustValidate(".register-form", {
            rules: {
                registerUsername: {
                    required: true,
                },
                registerEmail: {
                    required: true,
                    email: true,
                },
                registerPassword: {
                    required: true,
                },
                registerAgree: {
                    required: true,
                },
            },
            messages: {
                registerUsername: "Please enter your username",
                registerEmail: "Please enter a valid email address",
                registerPassword: "Please enter your password",
                registerAgree: "Your agreement is required",
            },
            invalidFormCallback: function () {
                let errorInputs = document.querySelectorAll(".register-form input[required]");
                bsValidationBehavior(errorInputs, registerForm);
                registerForm.addEventListener("keyup", () => bsValidationBehavior(errorInputs, registerForm));
                registerForm.addEventListener("change", () => bsValidationBehavior(errorInputs, registerForm));
            },
        });
    }

    // ------------------------------------------------------- //
    // Profile page choices
    // ------------------------------------------------------ //
    function injectClassess(x) {
        let pickerCustomClass = x.dataset.customclass;
        let pickerSevClasses = pickerCustomClass.split(" ");
        x.parentElement.classList.add.apply(x.parentElement.classList, pickerSevClasses);
    }

    const profileCountryChoices = document.querySelector(".profile-country-choices");
    if (profileCountryChoices) {
        const countryChoices = new Choices(profileCountryChoices, {
            searchEnabled: false,
            placeholder: false,
            callbackOnInit: () => injectClassess(profileCountryChoices),
        });
    }

    // ------------------------------------------------------- //
    // External links to new window
    // ------------------------------------------------------ //
    document.querySelectorAll(".external").forEach((el) => {
        el.addEventListener("click", function (e) {
            e.preventDefault();
            window.open(el.getAttribute("href"));
        });
    });

    // ------------------------------------------------------- //
    // Masonry with ImagesLoaded
    // ------------------------------------------------------ //
    const masonryGrid = document.querySelector(".msnry-grid");
    if (masonryGrid) {
        var msnry = new Masonry(masonryGrid, {
            percentPosition: true,
        });
        imagesLoaded(masonryGrid).on("progress", function () {
            msnry.layout();
        });
    }

    OverlayScrollbars(document.querySelector(".side-navbar"), {
        overflowBehavior: {
            x: "hidden",
        },
    });
});
