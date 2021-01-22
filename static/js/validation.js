function isIP(ip) {
    return (/^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/.test(ip));
}

function isDomain(domain) {
    return (/(https?:\/\/)?([a-zA-Z0-9-][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+)(:?\d{0,5})(\/.*)?/).test(domain);
}

// Base64 encode and make it URL safe (according to RFC 4648)
function encodeBase64(str) {
    return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/\=+$/, '');
}

// Fetches the redirected URL
async function getRedirect(url) {
    var options = {
        method: 'POST',
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: 'query=' + url
    };

    var response = await fetch('/api/redirect', options);
    if (response.ok) {
        return await response.text();
    }
}

async function validateSearch() {
    toggleLoad(true);

    var lookup = document.getElementById('lookup');
    var url = lookup.value;

    var redirected = await getRedirect(url);
    if (redirected)
        redirected = redirected.replace(/[\n]+/g, '');

    url = redirected !== "null" ? redirected : url;

    if (isDomain(url)) {
        window.location.href = '/domain/' + encodeBase64(url) + '/risk';
    }
    else {
        document.getElementById('fish-span').style.borderColor = 'red';
        lookup.style.borderColor = 'red';
        toggleLoad(false);
    }
}


// Handle enter button keypress in search bar
$("#lookup").on('keypress',function(e) {
    if(e.which === 13) {
        e.preventDefault();
        $("#searchButton").click();
    }
});
