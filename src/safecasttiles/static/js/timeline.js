

function getTimeline(year, month){
    var selectedDate = new Date(year, month-1);

    // create and adjust relative dates
    var dateMinus2 = new Date(selectedDate);
    dateMinus2.setMonth(dateMinus2.getMonth() - 2);

    var dateMinus1 = new Date(selectedDate);
    dateMinus1.setMonth(dateMinus1.getMonth() - 1);

    var datePlus1 = new Date(selectedDate);
    datePlus1.setMonth(datePlus1.getMonth() + 1);

    var datePlus2 = new Date(selectedDate);
    datePlus2.setMonth(datePlus2.getMonth() + 2);

    // create timeline html
    var barDiv = document.createElement("div");
    barDiv.className = "bar";

    var timelineDiv = document.createElement("div");
    timelineDiv.className = "timeline";

    var dateEntries = [ dateMinus2, dateMinus1, selectedDate, datePlus1, datePlus2];
    var arrayLength = dateEntries.length;
    var selectedDateIndex = 2;
    for (var idx = 0; idx < arrayLength; idx++) {
        var thisDate = dateEntries[idx];
        var entryDiv = document.createElement("div");
        entryDiv.innerHTML = '<h1>' + (thisDate.getMonth() + 1) + '</h1>';
        entryDiv.className = "entry";
        if (idx == selectedDateIndex){
            entryDiv.className = "entry-selected";
            entryDiv.innerHTML += '<h2>' + thisDate.getFullYear() + '</h2>';
        };
        timelineDiv.appendChild(entryDiv);
    };
    barDiv.appendChild(timelineDiv);

    return barDiv.outerHTML;
}