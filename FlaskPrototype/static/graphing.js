
if(!window.dash_clientside) {
    window.dash_clientside = {}
}

window.dash_clientside.graphing = {
    clickData: function(clickData, table) {
        if(clickData === undefined) return;

        let pointData = clickData.points[0];
        let data = JSON.stringify(table[pointData.pointIndex].FILENAME)

        return data;
    },
    zoomData: function(value, data) {
        if(value === undefined){
            console.log('undef')
            return;}

        console.log(value)

        return {
            'data': data,
            'layout': {
                'xaxis': {'range': [value[0], value[1]]}
            }
        }
    }
}
