
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
        },

        datefunc: function(start, end, table) {
            var xrange
            if(table === undefined) {
                throw "input undefined"
            }
            if(start === undefined) {
                xrange = {'autoscale': true}
            } else {
                xrange = {
                    'range': [start, end]
                }
            }

            data = JSON.parse(table)
            console.log(start)
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
                    'yaxis': {'autoscale': true},
                    'type': 'scattergl',
                    "hovermode": "closest"
                }
            }

            console.log(start)
            console.log(end)
        },

        specfunc: function(res, range, log, table) {
            if(table == []) {
                throw "input undefined"
            }
            data = JSON.parse(table)

            let linlog = "linear"
            if(log) {
                linlog = "log"
            }
            let index = 0, x_order = [], y_order = [], data_structure = []

            if( data.hasOwnProperty("ORDER")) {
                for(let order = range[0]; order < range[1]; order++) {
                    while(data['ORDER'][index] <= order) {
                        if(data['ORDER'][index] === order) {
                            x_order.push(data['# WAVE'][index])
                            y_order.push(data['FLUX'][index])
                        }
                        index++
                    }

                    data_structure.push({
                        "line": { "color": ["#EE3124", "#F8971D", "#FFDD00", "#3DAE2B", "#00AEEF", "#002F87", "#A25EB5"][order%7], "dash": "solid" },
                        "mode": "lines",
                        "name": "<b>" + order + "</b>",
                        "showlegend": true,
                        "type": "scattergl",
                        "x": x_order,
                        "xaxis": "x",
                        "y": y_order,
                        "yaxis": "y"
                    })
                    x_order = []
                    y_order = []
                }
            } else {

                less = {
                    'wave':[],
                    'flux':[]
                }
                for (i = 0; i < data['wave'].length; i=i+res) {
                    less['wave'].push(data['wave'][i]);
                    less['flux'].push(data['flux'][i]);
                }

                data_structure = [{
                    'x': Object.values(less['wave']),
                    'y': Object.values(less['flux']),
                    'xaxis': 'x',
                    'yaxis': 'y',
                    'type': 'linegl',
                }]
            }
            
            
            return {
                'data': data_structure,
                'layout':{
                    'yaxis': {
                        'type': linlog,
                        'autoscale': true},
                    'xaxis': {'autoscale': true},
                    'type': 'linegl',
                    "hovermode": "closest",
                    
                }
            }
        },
    }
});
