
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    graphing: {
        clickData: function(clickData, table) {
            if(clickData === undefined) return;
            data = JSON.parse(table)
            return data['FILENAME'][clickData.points[0].pointIndex]
        },
        
        datefunc: function(start, end, table) {
            var xrange
            if(table === undefined) {
                throw "input undefined"
            }
            if(start === undefined) {
                xrange = {
                    
                    'autoscale': true}
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
                    'xaxis': {
                        'title': {
                            'text': 'Recorded Date',
                            'font': {
                                'size': 18,
                                'color': '#7f7f7f'
                            }
                        },
                        xrange,
                    },
                    'yaxis': {
                        'title': {
                            'text': 'Radial Velocity',
                            'font': {
                                'size': 18,
                                'color': '#7f7f7f'
                            }
                        },
                        'autoscale': true
                    },
                    'type': 'scattergl',
                    "hovermode": "closest"
                }
            }

        },

        specfunc: function(res, range, log, table) {
            if(table === undefined) {
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
                len =Object.keys(data['# WAVE']).length
                for (i = 0; i < len; i=i+res) {
                    f=0
                    for (r=0; r < res; r+=1) {
                        f += data['# WAVE'][i+r]
                    }

                    less['wave'].push(f/res);
                    less['flux'].push(data['FLUX'][i]);
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
                        'title': {
                            'text': 'Flux',
                            'font': {
                                'size': 18,
                                'color': '#7f7f7f'
                            }
                        },
                        'type': linlog,
                        'autoscale': true},
                    'xaxis': {
                        'title': {
                            'text': 'Wavelength(Angstroms)',
                            'font': {
                                'size': 18,
                                'color': '#7f7f7f'
                            }
                        },
                        'autoscale': true
                    },
                    'type': 'linegl',
                    "hovermode": "closest",
                    
                }
            }
        },
    }
});
