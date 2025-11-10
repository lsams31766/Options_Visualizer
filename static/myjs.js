
// myjs.js


var cur_stock_ticker = 'TSLA';
var cur_exp_date = '2025-11-21';

$(document).ready( () => {
    $('#getPrice').click(function(){
        getPrice();
    });

    $("#strategyList").change(function () {
        // strategy changed
        console.log("strategy changed");
        setStrategy();
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

    var table = $('#callsOptionsChain').DataTable({
        info: false,
        ordering: false,
        paging: false,
        serverSide: true,
        searching: false,
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
                return JSON.stringify($.extend({}, d, {
                    ticker_symbol: cur_stock_ticker,
                    exp_date: cur_exp_date
                }));
            },
            "dataSrc": "data" // Specify the property in the JSON response containing the data array
        },

        columns: [
            { "data": "STRIKE" },
            { "data": "PREMIUM1" },
            { "data": "DELTA1" },
            { "data": "PREMIUM2" },
            { "data": "DELTA2" }
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
            })
            .catch(console.error);
        updateOptionsChain()
    }
    
    const updateOptionsChain = () => {
        console.log('UpdateOptionsChain');
        $('#callsOptionsChain').DataTable().ajax.reload();
    } 

    loadListBoxes();
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

