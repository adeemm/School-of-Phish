// Copyright (c) 2021 by redesigned (https://codepen.io/redesigned/pen/xWMrEJ)
//
// Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

var isLoading = true;
updateLoadingText();
isLoading = false;

var intervalID = window.setInterval(updateLoadingText, 3500);

function toggleLoad(shouldShow) {
    document.getElementsByClassName('loading-screen-wrapper')[0].style.display = shouldShow ? '' : 'none';
    document.getElementsByClassName('container-scroller')[0].style.display = !shouldShow ? '' : 'none';
    isLoading = shouldShow;
}

async function updateLoadingText() {
    if (isLoading) {
        var response = await fetch('/api/loading');
        if (response.ok) {
            document.getElementById('loading-text').innerText = await response.text();
        }
    }
}

jQuery(document).ready(function ($) {
    var bArray = [];
    var sArray = [5, 10, 18, 25];

    for (var i = 0; i < $('.bubbles').width(); i++) {
        bArray.push(i);
    }

    function randomValue(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    // setInterval function used to create new bubble every 350 milliseconds
    setInterval(function () {
        var size = randomValue(sArray);
        $('.bubbles').append('<div class="individual-bubble" style="left: ' + randomValue(bArray) + 'px; width: ' + size + 'px; height:' + size + 'px;"></div>');


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