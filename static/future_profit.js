// future_profit.js
// chart of future profit until date of expiration

const el=document.getElementById("myCanvas");
const ctx = el.getContext('2d');

const deepRed = '#FF0000';
const medRed = '#FF6B6B';
const ltRed = '#FFA1A1';
const deepGreen = '#00FF00';
const medGreen = '#80FF80';
const ltGreen = '#BDFFBD';
const ltGray = '#D3D3D3';

// values used for all charts
ctx.font = "20px Arial"; // Set font size and family
ctx.fillStyle = "black"; // Set fill color for the text
ctx.textAlign = "left" 
ctx.textBaseline = "hanging";


// positions
const month_pos = [85,10];
const ticker_pos = [5,40];
const days_start = [80,40];
const x_offset = 60;
const y_offset = 30;
let x_end = 200;

let x = days_start[0];
let y = days_start[1];

// make boxes
const box = (rectColor, x, y, text, fontSize, ctx) => {
    const textMetrics = ctx.measureText('99.999');
    const textWidth = textMetrics.width;
    const textHeight = fontSize; // Approximate height for simpler calculations
    const padding = 0; 
    const rectWidth = textWidth + (2 * padding) + 6;
    const rectHeight = textHeight + (2 * padding) + 6;
    ctx.fillStyle = rectColor;
    ctx.fillRect(x-2, y, rectWidth, rectHeight);
};

const getColor = (maxProfit, value) => {
    // negative values always RED, positive GREEN
    // the darker the color, the further from 0
    let total = 0.0;
    if (value < 0) {
        total = Math.abs(value) / Math.abs(maxProfit);
        if (total > 0.6) {
            return deepRed;
        } else if (total > .3) {
            return medRed;
        } else {
            return ltRed;
        }
    }
    total = value / maxProfit;
    if (total < .3) {
        return ltGreen; 
    } else if (total < .6) {
        return medGreen;
    } else {
        return deepGreen;
    }
}

const make_days_array = (data) => {
    // first month is this month
    const months = [
    'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
    'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'
    ];
    // not including leap year, sorry
    const max_days = [31,28,31,30,31,30,31,31,30,31,30,31]
    const today = new Date();
    let cur_month = today.getMonth();
    let cur_day = today.getDate();
    let day_array = [];
    // get number of days from data
    const total_days = data['days'][0];
    for (let i = 0; i < total_days; i++ ) {
        let e = [months[cur_month], cur_day];
        day_array.push(e)
        cur_day += 1;
        if (cur_day > max_days[cur_month]) {
            cur_day = 1;
            cur_month += 1;
            if (cur_month > 11) {
                cur_month = 0;
            }
        }
    }
    // console.log(day_array)
    return day_array;
};

// draw header of chart
const drawHeader = (day_array, ticker_name) => {
        // month on first row, day on 2nd row
        // only show month when it changes
        // day array = [[month,day],[month,day]..]
        const ticker_text = ticker_name
        ctx.fillText(ticker_text, ticker_pos[0], ticker_pos[1]);

        let cur_month = ''; // force month to print on first day
        for (let i = 0; i < day_array.length; i ++) {
            let new_month = day_array[i][0];
            if (new_month != cur_month) {
                ctx.fillText(new_month, x, month_pos[1]);
                cur_month = new_month;
            }
            // put in the day number
            ctx.fillText(day_array[i][1], x, y);
            x += x_offset;
        }

/*
    let month_text = first_month;
    ctx.fillText(month_text, month[0], month[1]);
    const ticker_text = ticker_name
    ctx.fillText(ticker_text, ticker_pos[0], ticker_pos[1]);
    for (let i = first_day; i >= last_day; i--) {
        ctx.fillText(i, x, y);
        x += x_offset;
    }
*/
    x += x_offset;
    y += 20;
    x_end = x;
    // line under days
    ctx.strokeStyle = ltGray;
    ctx.lineWidth = 2; // Set the line thickness
    ctx.beginPath(); 
    ctx.moveTo(0, y); 
    ctx.lineTo(el.width, y); 
    ctx.stroke();  
}

const drawData = (data, maxProfit) => {
    x = ticker_pos[0];
    y += y_offset;
    
    const p = data['data'];
    const nbrCols = p[0]['data'].length;
    const nbrRows = p.length;
    //for (let s_index = 0; s_index < sp.length; s_index++) {
    for (let r = 0; r < nbrRows; r++) {
        // stock price for line
        const stock_price = p[r]['price'];
        ctx.fillText(stock_price, x, y);
        x = days_start[0];
        // now do all the days prices - sample data
        // for (let i=1; i<=4; i++) {
        for (let i=1; i<nbrCols; i++) {
            let value = p[r]['data'][i]
            let color = getColor(maxProfit, value)
            box(color, x,y-5,value,20,ctx);
            ctx.fillStyle = 'black';
            ctx.fillText(value, x, y);
            x += x_offset;
        }
        y += y_offset;
        x = ticker_pos[0];
    }
}

const setCanvasSize = (data) => {
    // this distorts canvas, so don't do it
    const p = data['data'];
    const nbrCols = p[0]['data'].length;
    const newWidth = days_start[0] + x_offset * nbrCols + 20;
    const divEl=document.getElementById("myCanvasDiv");
    let s = "";
    s = String(newWidth) + "px";
    divEl.style.maxWidth = s;
}


// external function to call to make the chart
export const makeProfitChart = (data, ticker_name, max_profit, expiration_date) => {
    // clear canvas
    ctx.clearRect(0, 0, el.width, el.height);
    // set new size
    setCanvasSize(data);
    x = days_start[0];
    y = days_start[1];
    let day_array = make_days_array(data);
    drawHeader(day_array, ticker_name);
    drawData(data, max_profit);
}
