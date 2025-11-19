
// myjs.js


var cur_stock_ticker = 'TSLA';
var cur_exp_date = '2025-12-19';
var callOrPutSelection = 'CALLS'; // for options chain table 
var pnlChartVisible = false;
var dialog;


// forward declare showPnlChart()
let showPnlChart = function() {

}
function setLegDetails(strike, premium) {
    console.log('setLegDetails',strike, premium)
    // TODO
    // set selected_expiration, selected_option_type, 
    // selected_strike, selected_premium
    var h4Element = document.querySelector('#selected_expiration')
    h4Element.innerHTML = 'Expiration:&nbsp' + cur_exp_date;

    h4Element = document.querySelector('#selected_option_type')
    var s = 'CALL';
    if (callOrPutSelection == 'PUTS') {
        s = 'PUT'
    }
    h4Element.innerHTML = s

    h4Element = document.querySelector('#selected_strike')
    h4Element.innerHTML = 'Strike:&nbsp' + String(strike);

    h4Element = document.querySelector('#selected_premium')
    h4Element.innerHTML = 'Premium:&nbsp' + premium;

    // enable pnl chart
    $('#showPNL').removeAttr('disabled');
    // not sure if this will work
    if (pnlChartVisible == true) {
        showPnlChart();
    }
    dialog.close();
}


$(document).ready( () => {
    dialog = document.querySelector("dialog");

    $('#getPrice').click(function(){
        getPrice();
        getOptionsChain();
        updateOptionsChain();
        $('#getOption').removeAttr('disabled');
    });

    $("#strategyList").change(function () {
        // strategy changed
        console.log("strategy changed");
        setStrategy();
        // set correct toggle in options chain
        var strategy = $('#strategyList').find(":selected").text()
        const callsElement = $('.strip-button-0')[0]
        const putsElement = $('.strip-button-1')[0]
        if (strategy == 'Put' || strategy =='Sell Put') {
            // remove active-strip-button from class of strip-button-0
            callsElement.classList.remove("active-strip-button");
            // add active-strip-button to class of strip-button-1
            putsElement.classList.add("active-strip-button");
            callOrPutSelection = 'PUTS';
        }
        else {
            // remove active-strip-button from class of strip-button-1
            putsElement.classList.remove("active-strip-button");
            // add active-strip-button to class of strip-button-0
            callsElement.classList.add("active-strip-button");
            callOrPutSelection = 'CALLS';
        }
        updateOptionsChain();
        
     });

    
    $('#getOptionsChain').click(function(){
        getOptionsChain();
        updateOptionsChain();
    });

    $("#expirationDates").change(function () {
        // expiration date changed
        console.log("expiration date changed");
        cur_exp_date = $('#expirationDates').find(":selected").text(); 
        $('#callsOptionsChain').DataTable().ajax.reload();
     });

     $("#showPNL").click(function () {
        // show Profit and Loss Chart
        console.log("Show PNL chart");
        showPnlChart();
     });

     

    var table = $('#callsOptionsChain').DataTable({
        info: false,
        ordering: false,
        paging: false,
        serverSide: true,
        searching: false,
        autoWidth: false,
        scrollY: '300px', 
        deferLoading: 0,  // Prevents the initial AJAX call
        // TODO fetch correct symbol and expiration date
        ajax: {
            "url": "getOptionsChain", // Replace with your server-side script URL
            "type": "POST", // Specify the request type as POST
            "contentType": "application/json",
            "dataType": "json",
            "data": function (d) {
                // Add any extra data you want to send in the POST request
                // For example, to send a search term from an input field:
                // TODO provide number of strikes to show
                return JSON.stringify($.extend({}, d, {
                    ticker_symbol: cur_stock_ticker,
                    exp_date: cur_exp_date,
                    calls_or_puts: callOrPutSelection
                }));
            },
            "dataSrc": "data" // Specify the property in the JSON response containing the data array
        },

        columns: [
            { "data": "STRIKE" },
//            { "data": "PREMIUM" },
            { "data": "PREMIUM",
                        "orderable": true,
                        "searchable": false,
                        "render": function(data,type,row,meta) { 
                            
                            var params = "(" + row.STRIKE + "," + row.PREMIUM + ")" 
                            var a = '<a onclick="setLegDetails' + params +   '" href="javascript:void(0)">' + row.PREMIUM + '</a>'

                            return a;
                        }
                },
            { "data": "DELTA" }
        ]
    });

    const getOptionsChain = () => {
        console.log("getOptionsChain")
        const tickerElement = document.querySelector("#tickerSymbol");
        const tickerValue = tickerElement.value;
    
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        const myRequest = new Request("getExpirationDates", {
            method: "post",
            body: JSON.stringify({ ticker_symbol: tickerValue }),
            headers: myHeaders,
            });
    
        fetch(myRequest)
            // Convert response to text
            .then((response) => response.json())
            .then((data) => {
                for (const i of data.items) {
                    // add list items to expirationDates
                    var option = document.createElement("option");
                    option.text = i;
                    option.value = i;
                    $("#expirationDates").append(option)
                }
                // set selcted expiration date to 1st entry
                cur_exp_date = data.items[0]
            })
            .catch(console.error);
   
        updateOptionsChain()
    }
    
    const updateOptionsChain = () => {
        console.log('UpdateOptionsChain');
        $('#callsOptionsChain').DataTable().ajax.reload();
    } 

    const makeCallOrPutToggle = () => {
        // from https://www.cssscript.com/inline-toggle-button-buttonstrip/
        var instance = new ButtonStrip({
            id: 'buttonStrip-viewToggle'
        });
        instance.addButton('Calls', true, 'click', function(){
            if (callOrPutSelection == 'CALLS' ) {
                return;
            }    
            callOrPutSelection = 'CALLS';
            const putsElement = $('.strip-button-1')[0]
            putsElement.classList.remove("active-strip-button");    
            // $('#je_rules').empty();
            // $("#outputText").html("Text View");
            updateOptionsChain();
        });
        instance.addButton('PUTS', false, 'click', function(){
            console.log('Tree View toggle');
            if (callOrPutSelection == 'Puts' ) {
                return;
            }    
            callOrPutSelection = 'PUTS';
            const callsElement = $('.strip-button-0')[0]
            callsElement.classList.remove("active-strip-button");    
            // $("#je_rules").show();
            // $("#outputText").html("Tree View");
            updateOptionsChain();
        });
        // TODO - call GetOptionsTable with Call or Put value
        instance.append('#callOrPutToggle');
    }

    $('#getOption').click(function(){
        dialog.showModal();
    });

    // "Close" button closes the dialog
    $( "#closeButton").on( "click", () => {
        dialog.close();
    });

    showPnlChart = () => {
        // TODO 2 and more leg trades
        console.log("showPnlChart")
        const myDiv = document.getElementById('myChartContainer');
        myDiv.style.display = 'block';
        pnlChartVisible = true;
        // MUST SEND:
        //  exp_date1, calls_or_puts1, strike_price1, premium1, 
        //  strategy, cur_stock_price, buy_or_sell
        const strikePriceElement = document.querySelector('#selected_strike');
        const strikePrice1 = strikePriceElement.innerText;

        const PremiumElement = document.querySelector('#selected_premium');
        const premium1 = PremiumElement.innerText;

        const strategyElement = document.querySelector('#strategySelected');
        const strategy = strategyElement.innerText;

        const curStockPriceElement = document.querySelector('#priceVal');
        const cur_stock_price = curStockPriceElement.innerText;
        
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        const myRequest = new Request("getPnlTable", {
            method: "post",
            body: JSON.stringify({ 
                exp_date1: cur_exp_date,
                calls_or_puts1: strategy,
                strike_price1: strikePrice1,
                premium1: premium1,
                strategy: strategy,
                cur_stock_price: cur_stock_price,
                buy_or_sell: strategy
            }),
            headers: myHeaders,
            });
    
        fetch(myRequest)
            // Convert response to text
            .then((response) => response.json())
            .then((data) => {
                console.log(data.data);
                // TODO put in the red and green fills!
                prices = data.data[0];
                values = data.data[1];
                myChart.data.labels = [];
                myChart.data.datasets.forEach((dataset) => {
                    dataset.data = [];
                });
                myChart.data.labels = prices;
                myChart.data.datasets[0].data = values;
                myChart.update();
            })
            .catch(console.error);
    }

    var prices = [100,105,110,115,120,125,130,135,140,145];
    var values = [-2.5,-2.5,-2,-1,0,1,1.5,2.5,2.5,2.5];

    // THE CHART
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, {
        type: 'line', // or 'line', 'pie', 'doughnut', etc.
        data: {
            labels: prices,
            datasets: [{
                label: 'Profit',
                data: values,
                backgroundColor: 'black',
                borderColor: [
                ],
                borderWidth: 1,
                fill: {
                    target: 'origin',
                    below: 'rgb(255, 0, 0)', // Red for areas below 0
                    above: 'rgb(0, 255, 0)'  // Green for areas above 0
                  }
            }
        ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false, // Allows chart to resize freely
            scales: {
                y: {
                    stacked: true,
                    beginAtZero: false,
                    ticks: {
                        callback: function(value, index, ticks) {
                            return value.toFixed(2); // Formats the tick value to two decimal places
                        }
                    },
                    grid: {
                        color: (context) => {
                            if(context.tick.value === 0) {
                                return 'green'
                            } else {
                                return 'rgba(211, 211, 211)'
                            }
                        }
                    }
                }
            }
        }
    });

    loadListBoxes();
    makeCallOrPutToggle();
})

const loadListBoxes = () => {
    console.log('Load List Boxes');
    loadListBox("strategyList","getStrategies");
}

const loadListBox = (aSelect, aUrl) => {
    // aUrl = '/jerules/getConnectors'
    fetch(aUrl)
        // Convert response to text
        .then((response) => response.json())
        .then((data) => {
			for (const i of data.items) {
                // add list items to conList
                var option = document.createElement("option");
                option.text = i;
                option.value = i;
                $("#" + aSelect).append(option)
            }})
        .catch(console.error);
}

function AddOption(aSelect, aValue) {
    var option = document.createElement("option");
    option.text = aValue;
    option.value = aValue;
    $("#" + aSelect).append(option)
}

const setStrategy = () => {
    console.log("setStrategy")
    var strategy = $('#strategyList').find(":selected").text(); 
     // Get a reference to the h4 element by its class
     // const h4Element = $("#strategySelected");
     const h4Element = document.querySelector('#strategySelected')
     // Set the new HTML content
     h4Element.innerHTML = strategy;
     // update legs 1 value
     const h4Element2 = document.querySelector('#leg1TypeValue')
     h4Element2.innerHTML = strategy;
}

const getPrice = () => {
    console.log("getPrice")
    const tickerElement = document.querySelector("#tickerSymbol");
    const tickerValue = tickerElement.value;
    console.log("ticker symbol is",tickerValue)
    cur_stock_ticker = tickerValue // for options chain

    const myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    const myRequest = new Request("getPrice", {
        method: "post",
        body: JSON.stringify({ ticker_symbol: tickerValue }),
        headers: myHeaders,
        });

    fetch(myRequest)
        // Convert response to text
        .then((response) => response.json())
        .then((data) => {
            newData = data.item;
            console.log('price is ', newData)
            $("#priceVal").html(newData);                
        })
        .catch(console.error);
}


