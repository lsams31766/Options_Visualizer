// legs.js
// make leg divisions



const AppendRow = (targetDiv, rowClass) => {
    var $tDiv = $(targetDiv);
    var rowDivStr = '<div class="' + rowClass + '">';
    var $rowDiv = $(rowDivStr);
    $tDiv.append($rowDiv);
    return [$tDiv, $rowDiv];
};

const AppendCol = (targetDiv, colClass) => {
    var $tDiv = targetDiv;
    var colDivStr = '<div class="' + colClass +'">';
    var $colDiv = $(colDivStr);
    $tDiv.append($colDiv);
    return [$tDiv, $colDiv];
};

const AppendH4 = (targetDiv, h4Text, aId='X', aClass = 'X') => {
    var $tDiv = targetDiv;
    var h4Str = '<h4 id="' + aId + '" class="' + aClass + '">' + h4Text + '</h4>';
    var $h4Element = $(h4Str);
    $tDiv.append($h4Element);
    return [$tDiv, $h4Element];
};

const AppendButton = (targetDiv, aId, aClass, aDisabled, aText) => {
    var $tDiv = targetDiv;
    var btnStr = '<button id="' + aId + '" class="btn ' + aClass + 
        '" ' + aDisabled + '>' + aText + '</button>';
    var $btnElement = $(btnStr);
    $tDiv.append($btnElement);
    return [$tDiv, $btnElement];
};

const AppendSelect = (targetDiv, aId, aClass) => {
    var $tDiv = targetDiv;
    var selStr = '<select class="' + aClass + '" id="' + aId+ '">';
    var $selElelment = $(selStr);
    $tDiv.append($selElelment);
    return [$tDiv, $selElelment];
};

const AppendOption = (targetDiv, aValue, aText) => {
    var $tDiv = targetDiv;
    var optStr = '<option value="' + aValue + '">' + aText + '</option>';
    var $optElelment = $(optStr);
    $tDiv.append($optElelment);
    return [$tDiv, $optElelment];
};

var parent_div = '#X';
// var parent_div = '#X'; // the div all these legs go under
export const MakeLegs = (aParent_div, number_legs) => {
    // remove contents of legs div and then reload it
    parent_div = aParent_div; // set the gloval parent div name
    //var $tDiv = parent_div;
    //$tDiv.empty(); // so refreshes do not accumulate legs
    $(parent_div).empty();

    for (let i = 1; i <= number_legs; i++) {
        // ROW 1 name of leg
        var [$targetDiv, $row1] = AppendRow(parent_div,'row pt-3');
        var [$targetDiv, $col] = AppendCol($row1,'col-auto');
        var [$targetDiv, $h4Elem] = AppendH4($col,'Leg ' + String(i));

        // ROW 2 Get Options Button, Buy Write Select, Nbr Contracts Select
        var [$targetDiv, $row2] = AppendRow(parent_div,'row py-2');
        var [$targetDiv, $col] = AppendCol($row2,'col-3');
        var [$targetDiv, $btn] = AppendButton($col, 'getOption' + String(i), 'btn-primary', 'disabled', 'Select Option for Leg ' + String(i));

        var [$targetDiv, $col] = AppendCol($row2,'col-auto');
        var [$targetDiv, $h4Elem] = AppendH4($col,'Buy/Write:');

        var [$targetDiv, $col] = AppendCol($row2,'col-2');
        var [$targetDiv, $selElem] = AppendSelect($col, 'buyWrite' + String(i), 'form-control');
        var [$targetDiv, $optElem1] = AppendOption($selElem, 'buy2', 'Buy');
        var [$targetDiv, $optElem2] = AppendOption($selElem, 'write2', 'Write');

        var [$targetDiv, $col] = AppendCol($row2,'col-2');
        var [$targetDiv, $h4Elem] = AppendH4($col,'Contracts:');

        var [$targetDiv, $col] = AppendCol($row2,'col-2');
        var [$targetDiv, $selElem2] = AppendSelect($col, 'contracts' + String(i), 'form-control');
        var [$targetDiv, $optElem2] = AppendOption($selElem2, '1', '1');
        var [$targetDiv, $optElem2] = AppendOption($selElem2, '2', '2');

        // Row 3 Details on Expiration, Call/Put, Strike, Premium
        var [$targetDiv, $row3] = AppendRow(parent_div,'row py-2 pb-5');
        var [$targetDiv, $col] = AppendCol($row3,'col-auto');
        var [$targetDiv, $h4Elem] = AppendH4($col, 'Expiration: ?', 'selected_expiration' + String(i), 'not-bold');

        var [$targetDiv, $col] = AppendCol($row3,'col-auto');
        var [$targetDiv, $h4Elem] = AppendH4($col, 'CALL/PUT ?', 'selected_option_type' + String(i), 'not-bold');

        var [$targetDiv, $col] = AppendCol($row3,'col-auto');
        var [$targetDiv, $h4Elem] = AppendH4($col, 'Strike: ?', 'selected_strike' + String(i),  'not-bold');

        var [$targetDiv, $col] = AppendCol($row3,'col-auto');
        var [$targetDiv, $h4Elem] = AppendH4($col, 'Premium: ?', 'selected_premium' + String(i), 'not-bold');
    }
}

// some setup data
// buy_write index 0 is Buy, index 1 is Write
export const leg_settings = {
    'Call': {'nbr_legs':1, 'call_put':['call'], 'buy_write':['buy']},    
    'Put': {'nbr_legs':1, 'call_put':['put'], 'buy_write':['buy']},
    'Sell Call': {'nbr_legs':1, 'call_put':['call'], 'buy_write':['write']},
    'Sell Put': {'nbr_legs':1, 'call_put':['put'], 'buy_write':['write']},
    'Credit Spread': {'nbr_legs':2, 'call_put':['put','put'], 'buy_write':['write','buy']},
    'Iron Condor': {'nbr_legs':4, 'call_put':['put','put','call','call'], 'buy_write':['write','buy','write','buy']},
    'Calendar Spread': {'nbr_legs':2, 'call_put':['call','call'], 'buy_write':['write','buy']},
    'Collar': {'nbr_legs':2, 'call_put':['call','put'], 'buy_write':['write','buy']}}




