
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    graphing: {
        clickData: function(clickData, table) {
            if(clickData === undefined) return;
            data = JSON.parse(table)
            return data['FILENAME'][clickData.points[0].pointIndex]
        },
        zoomfunc: function (x1, x2, y1, y2, table) {
            console.log(x1)
            var xrange, yrange, xlo, xhi, ylo, yhi
            if(table === undefined){
                throw 'input undefined'
            }
            
            data = JSON.parse(table)
            console.log(Object.values(data['MJD'])[0])

            xlo = (x1 === undefined) ? Math.min(data['MJD']) : x1 ;
            xhi= (x1 === undefined) ? Math.max(data['MJD']) : x1 ;
            ylo = (x1 === undefined) ? Math.min(data['V']) : x1 ;
            yhi = (x1 === undefined) ? Math.max(data['V']) : x1 ;
            
            if(x1 === undefined && x2 === undefined) {
                xrange = {
                    'autoscale': true
                }
            }
            else {
                xrange = {
                    'range': [xlo, xhi]
                }
            }

            if(y1 === undefined && y2 === undefined) {
                yrange = {
                    'autoscale': true
                }
            }
            else {
                yrange = {
                    'range': [ylo, yhi]
                }
            }


            return {
                'data':[{
                    'x': Object.values(data['MJD']),
                    'y': Object.values(data['V']),
                    'xaxis': 'x',
                    'yaxis': 'y',
                    'type': 'scattergl',
                    'mode': 'markers'
                }],
                'layout':{
                    'xaxis': xrange,
                    'yaxis': yrange,
                    'type': 'scattergl',
                    "hovermode": "closest"
                }
            }



            
        }
    }
});
