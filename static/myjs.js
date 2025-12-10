
// myjs.js


var cur_stock_ticker = 'TSLA';
var cur_exp_date = '2025-12-19';
var callOrPutSelection = 'CALLS'; // for options chain table 
var pnlChartVisible = false;
var dialog;
var optionsLegSelected = 1; // which options button was pressed
var cur_strategy = 'Call'

import {
    MakeLegs, leg_settings
 } from './legs.js';

 import {
    makeProfitChart
 } from './future_profit.js'

// key value pairs for strategy desriptions
const strategy_desc = {
    'Call': 'BULLISH: Buy Call option. Profit if Stock Price is > Strike Price at Expiration',
    'Put': 'BEARISH: Buy Put Option. Profit if Stock Price is < Strike Price at Expiration',
    'Sell Call': 'BEARISH: SELL Call option.  Profit if Stock Price is <= Strike Price at Expiration',
    'Sell Put': 'BULLISH: SELL Put option.  Profit if Stock Price is >= Strike Price at Expiration',
    'Credit Spread': 'BULLISH: Sell a PUT lower than current stock price, and Buy a PUT at a lower strike price, profit if stock ends up between Strke Prices',
    'Iron Condor': 'BEARISH: Sell PUT below market price, buy PUT below Sell Put, Sell CALL above market price, Buy call above Sell Call, ',
    'Calendar Spread': 'Sell Call Expires soon, Buy Call Expires later at same Strike Price',
    'Collar': 'BEARISH: Sell a Call higher than current stock price, and Buy a PUT at a lower than market price, profit if stock ends up between Strke Prices'
}

const singleLeg = ['Call','Put','Sell Call','Sell Put']
const twoLegs = ['Credit Spread', 'Calendar Spread', 'Collar']
const fourLegs = ['Iron Condor']

// forward declare showPnlChart()
let showPnlChart = function() {}

// forward declare showFutureProfitChart()
let showFutureProfitChart = function() {}

function setLegDetails(strike, premium) {
    console.log('setLegDetails',strike, premium)
    // use optionsLegSelected to create id of elemnet to update
    const i = optionsLegSelected;
    const expirationElement = document.querySelector('#selected_expiration' + String(i));
    const optionTypeElement = document.querySelector('#selected_option_type' + String(i));
    const strikeElement = document.querySelector('#selected_strike' + String(i));
    const premiumElement = document.querySelector('#selected_premium' + String(i));
    expirationElement.innerHTML = 'Expiration:&nbsp' + cur_exp_date;

    var s = 'CALL';
    if (callOrPutSelection == 'PUTS') {
        s = 'PUT'
    }
    optionTypeElement.innerHTML = s
    strikeElement.innerHTML = 'Strike:&nbsp' + String(strike);
    premiumElement.innerHTML = 'Premium:&nbsp' + premium;

    // enable pnl chart
    $('#showPNL').removeAttr('disabled');
    $('#showProfit').removeAttr('disabled');
    
    if (pnlChartVisible == true) {
        showPnlChart();
    }
    dialog.close();
}

window.setLegDetails = setLegDetails; // make this global


// TODO !!! - options chain - wrong options sent as per toggle given strategy change
//   fix which chain (put or call ) is specified for when sent to backend 


$(document).ready( () => {
    dialog = document.querySelector("dialog");
    MakeLegs('#legsDiv',1);

    const MakeOptionsEventListeners = () => {
        const nbr_legs = leg_settings[cur_strategy]['nbr_legs'];
        // Loop through the range of IDs
        for (let i = 1; i <= nbr_legs; i++) {
            const elementId = `getOption${i}`; // Construct the ID
            const element = document.getElementById(elementId);
        
            if (element) { // Check if the element actually exists
                element.addEventListener('click', function() {
                    optionsLegSelected = i;
                    // set callOrPutToggle to correct value
                    const call_or_put = leg_settings[cur_strategy]['call_put'][optionsLegSelected - 1]
                    SetCallPutToggle(call_or_put);
                    updateOptionsChain();
                    dialog.showModal();
                });
            }
        }
    };

    $('#getPrice').click(function(){
        getPrice();
        getOptionsChain();
        updateOptionsChain();
        // determine which getOptions buttons to enable
        const nbr_legs = leg_settings[cur_strategy]['nbr_legs']
        for (let i=1; i<=nbr_legs; i++) {
            let className = '#getOption' + String(i);
            $(className).removeAttr('disabled');
        }
    });

    const SetCallPutToggle = (newValue) => {

        const callsElement = $('.strip-button-0')[0]
        const putsElement = $('.strip-button-1')[0]

        if (newValue == 'put') {
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

    };

    $("#strategyList").change(function () {
        // strategy changed
        console.log("strategy changed");
        cur_strategy = $('#strategyList').find(":selected").text(); 
        updateOptionsChain();
        const ls = leg_settings[cur_strategy];
        const number_legs = ls['nbr_legs'];
        MakeLegs('#legsDiv',number_legs);
        // set the buy/write and put/call boxes
        //   and enabling of get options button
        //  using leg_settings config
        for (let i = 1; i <= number_legs; i++) {
            // Assuming you have a <select> element with the ID 'mySelect'
            // const selectElement = document.getElementById('buyWrite1');
            // Set the value to 'orange', which will select the option with value="orange"
            // selectElement.selectedIndex = 0;
            let bwClass = 'buyWrite' + String(i)
            let bwElem = document.getElementById(bwClass);
            // get value, convert to index
            let aIndex = 0;
            if (ls['buy_write'][i-1] == 'write') {
                aIndex = 1;
            }
            bwElem.selectedIndex = aIndex;
        }
        // clear the chart, need to select options and pull in the chart
        const myDiv2 = document.getElementById('myChartContainer');
        myDiv2.style.display = 'none';

        setStrategyTextArea();
        MakeOptionsEventListeners();
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

     $("#showProfit").click(function () {
        // show Future Profit Chart
        console.log("Show Future Profit chart");
        showFutureProfitChart();
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
            "dataSrc": "data", // Specify the property in the JSON response containing the data array
        },
        "rowCallback": function(nRow, aData, index) {
            //  console.log('rowCallback',nRow,aData);
            // For Calls options chain, make light green ITM
            const cur_stock_price = Number($('#priceVal').text());
            if (callOrPutSelection == 'CALLS') {
                if (aData['STRIKE'] < cur_stock_price) {
                    $('td', nRow).css('background-color', 'rgb(189,255,189)'); 
                }   
            // For Puts options chain, make light green ITM
            } else {
                if (aData['STRIKE'] > cur_stock_price) {
                    $('td', nRow).css('background-color', 'rgb(189,255,189)');                
                }
            }
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
    // "Close" button closes the dialog
    $( "#closeButton").on( "click", () => {
        dialog.close();
    });

    const makePnlCallPayload = () => {
        // make the payload for call to getPnlTable()
        // MUST SEND:
        //  exp_date1, calls_or_puts1, strike_price1, premium1, 
        //  strategy, cur_stock_price, buy_or_sell
        const cur_stock_price = $('#priceVal').text();
        const tickerElement = document.querySelector("#tickerSymbol");
        const tickerValue = tickerElement.value;
        let payload = {}
        payload = {
            strategy: cur_strategy,
            cur_stock_price: cur_stock_price,
            ticker_name: tickerValue
        }
        // for each leg, add options details
        const nbr_legs = leg_settings[cur_strategy]['nbr_legs']
        for (let i = 1; i<= nbr_legs; i++) {
            let expiration = $('#selected_expiration' + String(i)).text();
            let calls_or_puts = $('#selected_option_type' + String(i)).text();
            let strikePrice = $('#selected_strike' + String(i)).text();
            let premium = $('#selected_premium' + String(i)).text();
            let buy_or_sell = $('#buyWrite' + String(i)).find(":selected").text();
            payload['exp_date' + String(i)] = expiration;
            payload['calls_or_puts' + String(i)] =  calls_or_puts;
            payload['strike_price' + String(i)] = strikePrice;
            payload['premium' + String(i)] = premium;
            payload['buy_or_sell' + String(i)] = buy_or_sell;
        }
        return payload;
    }

    showPnlChart = () => {
        // TODO 3 and more leg trades
        // show pnl chart
        console.log("showPnlChart");
        const myDiv = document.getElementById('myChartContainer');
        myDiv.style.display = 'block';
        pnlChartVisible = true;
        // make the payload
        let payload = makePnlCallPayload();
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        const myRequest = new Request("getPnlTable", {
            method: "post",
            body: JSON.stringify(payload),
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
    
    const calcMaxProfit = (payload) => {
        // calcluate max profit
        // this is the highest premium of all the legs
        const nbr_legs = leg_settings[cur_strategy]['nbr_legs'];
        let max_profit = 0;
        for (let i = 1; i<= nbr_legs; i++) {
            let cur_premium = payload['premium' + String(i)]
            let p = cur_premium.match(/\d+(\.\d+)?/g); // Matches integers and decimals
            p = Number(p)
            if (p > max_profit) {
                max_profit = p;
            }
        }
        return max_profit;
    }
    
    showFutureProfitChart = () => {
        console.log("showFutureProfitChart");
        // make the payload
        const tickerElement = document.querySelector("#tickerSymbol");
        const tickerValue = tickerElement.value;
        
        let payload = makePnlCallPayload();
        const expiration_date = payload['exp_date1']
        const myHeaders = new Headers();
        myHeaders.append("Content-Type", "application/json");
        const myRequest = new Request("get_future_profit", {
            method: "post",
            body: JSON.stringify(payload),
            headers: myHeaders,
            });
    
        fetch(myRequest)
            // Convert response to text
            .then((response) => response.json())
            .then((data) => {
                const max_profit = calcMaxProfit(payload)
                makeProfitChart(data['data'], tickerValue, max_profit, expiration_date);
            })
            .catch(console.error);
    }


    const setStrategyTextArea = () => {
        //strategyTextArea
        $("#strategyTextArea").val(strategy_desc[cur_strategy]);
    }
    
    MakeOptionsEventListeners();
    loadListBoxes();
    makeCallOrPutToggle();
    setStrategyTextArea();
})

const loadListBoxes = () => {
    console.log('Load List Boxes');
    loadListBox("strategyList","getStrategies");
    // contracts1, contracts2 listboxes
    const values = ['1','2','3','4','5']
    for (const i of values) {
        // add list items
        var option = document.createElement("option");
        var option2 = document.createElement("option");
        option.text = i;
        option.value = i;
        option2.text = i;
        option2.value = i;
        $("#contracts1").append(option)
        $("#contracts2").append(option2)
    }
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
     // Get a reference to the h4 element by its class
     // const h4Element = $("#strategySelected");
     // const h4Element = document.querySelector('#strategySelected')
     // Set the new HTML content
     // h4Element.innerHTML = strategy;
     // update legs 1 value
     // const h4Element2 = document.querySelector('#leg1TypeValue')
     // h4Element2.innerHTML = strategy;
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
            const newData = data.item;
            console.log('price is ', newData)
            $("#priceVal").html(newData);                
        })
        .catch(console.error);
}


