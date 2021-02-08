(

function(relayoutData) {
    console.log(relayoutData);
    let data = JSON.stringify(relayoutData);

    if ('xaxis.range[0]' in data) {

    }

    if ('yaxis.range[0]' in data) {

    }

    return data;
}
,

function(clickData, table) {
    console.log(table);
    if(clickData === undefined) {
        return;
    }

    let pointData = clickData.points[0];
    let data = JSON.stringify(table[pointData.pointIndex])

    

    return data;
}

)