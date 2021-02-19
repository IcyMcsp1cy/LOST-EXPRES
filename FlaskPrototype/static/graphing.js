
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    graphing: {
        clickData: function(clickData, table) {
            if(clickData === undefined) return;
    
            let pointData = clickData.points[0];
            let data = JSON.stringify(table[pointData.pointIndex].FILENAME)
    
            return data;
        },
        zoomfunc: function (value, table) {
            data = JSON.parse(table)
            if(table === undefined || value === undefined){
                throw 'input undefined'
            }
            return {
                'data':[{
                    'x': Object.values(data['MJD']),
                    'y': Object.values(data['V']),
                    'xaxis': 'x',
                    'yaxis': 'y',
                    'type': 'scatter',
                    'mode': 'markers'
                }],
                'layout':{
                    'xaxis': {
                        'range': [value[0],value[1]]
                    },
                    'type': 'scatter'
                }
            }
            
        }
    }
});
