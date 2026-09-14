document.addEventListener("DOMContentLoaded", function () {

    // Navbar shadow when scrolling

    const nav = document.querySelector(".zenvora-nav");

    window.addEventListener("scroll", function () {

        if (!nav) return;

        if (window.scrollY > 30) {

            nav.style.boxShadow =
                "0 8px 30px rgba(0,0,0,.08)";

        } else {

            nav.style.boxShadow = "none";

        }

    });


    // Automatically close alerts

    setTimeout(function () {

        document.querySelectorAll(
            ".alert"
        ).forEach(function (alert) {

            const closeButton =
                alert.querySelector(".btn-close");

            if (closeButton) {
                closeButton.click();
            }

        });

    }, 4500);


    // Image fallback

    document.querySelectorAll("img").forEach(
        function (image) {

            image.addEventListener(
                "error",
                function () {

                    this.src =
                        "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c";

                }
            );

        }
    );


    // Price number animation

    document.querySelectorAll(
        ".stats-section strong"
    ).forEach(function (element) {

        element.style.opacity = "0";

        setTimeout(function () {

            element.style.transition =
                "opacity .8s ease";

            element.style.opacity = "1";

        }, 150);

    });

});