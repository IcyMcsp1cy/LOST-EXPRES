
window.onload = function () {

    let transitioning = false;

    function transition(nextPage) {
        if (nextPage.hasClass("landing")) {
            $(".logo").animate({ opacity: "0" }, 500)
        }
        else {
            $(".logo").animate({ opacity: "1" }, 500)
        }
        active = $(".active");
        if (!transitioning && !nextPage.hasClass("active")) {

            active.fadeOut(500, function () {
                nextPage.fadeIn(500, function () {
                    nextPage.removeClass("inactive").addClass("active")
                    active.addClass("inactive");

                })
            }).removeClass("active");
        }
        $("nav ul.open").removeClass("open");
    }

    $("#tab-intro").click(function () {
        transition($("#content-intro"));
    })

    $("#tab-team").click(function () {
        transition($("#content-team"));
    })

    $("#tab-description").click(function () {
        transition($("#content-description"));
    })

    $("#tab-requirements").click(function () {
        transition($("#content-requirements"));
    })

    $("#tab-technologies").click(function () {
        transition($("#content-technologies"));
    })

    $("#tab-solutions").click(function () {
        transition($("#content-solutions"));
    })

    $("#tab-deliverables").click(function () {
        transition($("#content-deliverables"));
    })



    // Responsive navbar to dropdown menu
    let dropdown = $("nav ul");

    $("#menu").click(function () {
        if (dropdown.hasClass("open")) {
            dropdown.removeClass("open");
        }
        else {
            dropdown.addClass("open");
        }
    })

    // dropdown resize handling
    window.addEventListener("resize", function () {
        viewportWidth = window.innerWidth || document.documentElement.clientWidth;
        if (dropdown.hasClass("open") && viewportWidth >= 900) {
            dropdown.removeClass("open");
        }
    });



    // Config for Particle System
    particlesJS("particles-js", {
        particles: {
            number: { value: 160, density: { enable: true, value_area: 800 } },
            color: { value: ["#FAEAA7", "#EDD382", "#FC9E4F", "#F4442E"] },
            shape: {
                type: "circle",
                stroke: { width: 0, color: "#000000" },
                polygon: { nb_sides: 5 },
                image: { src: "img/github.svg", width: 100, height: 100 }
            },
            opacity: {
                value: 0.8,
                random: false,
                anim: { enable: false, speed: 1, opacity_min: 0, sync: false }
            },
            size: {
                value: 3,
                random: true,
                anim: { enable: false, speed: 4, size_min: 2, sync: false }
            },
            line_linked: {
                enable: true,
                distance: 65,
                color: "#FAEAA7",
                opacity: 0.8,
                width: 1
            },
            move: {
                enable: true,
                speed: 0.4,
                direction: "top",
                random: true,
                straight: false,
                out_mode: "out",
                bounce: false,
                attract: { enable: true, rotateX: 600, rotateY: 600 }
            }
        },
        interactivity: {
            detect_on: "canvas",
            events: {
                onhover: { enable: false },
                onclick: { enable: false },
                resize: true
            }
        },
        retina_detect: true
    });



}
