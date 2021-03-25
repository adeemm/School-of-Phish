var isLoading = false;
var loadingMessages;
var getRandom;


window.setInterval(updateLoadingText, 5000);

$.getJSON("/static/json/loading.json", function (json) {
    loadingMessages = json;
    getRandom = nonRepeatingRandom(loadingMessages);
    //$("#loading-text").text(getRandom());
});

function randomValue(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
}

function randomValueRange(min, max) {
    return Math.random() * (max - min) + min;
}

function nonRepeatingRandom(array) {
    var copy = array.slice(0);

    return function () {
        if (copy.length < 1) {
            copy = array.slice(0);
        }
        var index = Math.floor(Math.random() * copy.length);
        var item = copy[index];
        copy.splice(index, 1);
        return item;
    };
}

function toggleLoad(shouldShow) {
    $(".loading-screen-wrapper").css("display", shouldShow ? '' : "none");
    $(".container-scroller").css("display", !shouldShow ? '' : "none");
    isLoading = shouldShow;
}

function updateLoadingText() {
    if (isLoading) {
        $("#loading-text").text(getRandom());
    }
}

jQuery(document).ready(function ($) {
    var sArray = [5, 10, 18, 25];

    // setInterval function used to create new bubble every 350 milliseconds
    setInterval(function () {
        var size = randomValue(sArray);
        var loc = randomValueRange(5, 95);

        $('.bubbles').append('<div class="individual-bubble" style="left: ' + loc + '%; width: ' + size + 'px; height:' + size + 'px;"></div>');


        $('.individual-bubble').animate({
                'bottom': '100%',
                'opacity': '-=0.6'
            }, 8000, function () {
                $(this).remove()
            }
        );


    }, 300);

    $('.nav-link').each(function(){
        var linkToFollow = $(this).attr('href');

        if (linkToFollow.indexOf("#") === -1) {
            $(this).click(function(e) {
                toggleLoad(true);
                window.open(linkToFollow, "_self");
                return false;
            });
        }
    });
});