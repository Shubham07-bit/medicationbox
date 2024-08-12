$(document).ready(function() {
    // Initialize Owl Carousel
    $('.owl-carousel').owlCarousel({
        loop: true,
        margin: 0,
        nav: true,
        autoplay: true,
        dots: true,
        autoplayTimeout: 5000,
        navText: ['<i class="fa fa-angle-left"></i>', '<i class="fa fa-angle-right"></i>'],
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            1000: {
                items: 1
            }
        }
    });

    // Toggle side panel
    $('#toggleBtn').on('click', function() {
        $('#sidePanel').toggleClass('show');
        $(this).toggleClass('active'); // Optional: to change button style when panel is open
    });
});
