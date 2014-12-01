var page = require('webpage').create(),
    system = require('system'),
    output_path = "",
    address = "";

var content = '',
    f = null,
    lines = null;


if (system.args.length < 3){
    console.log("usage : phantomjs makepng.js url output_path");
    phantom.exit(1);
}


// Read target URL to capture & output image path
try {
    address = system.args[1];
    output_path = system.args[2];

} catch(e) {
    console.log(e);
    phantom.exit(1);
}

function snap(){
    console.log("address ", address);
    console.log("output " + output_path);
    page.viewportSize = { width: 850, height: 850 };
    page.open(address, function(status){
        if (status !== 'success'){
            console.log('Unable to load the address!');
            phantom.exit(1);
        } else {
            setTimeout(function() {
                page.render(output_path);
                phantom.exit();
            }, 3000); // 3000 == 3 seconds
        }
    });
}

try{
    snap();
} catch(e) {
    console.log(e);
    phantom.exit(1);
}
