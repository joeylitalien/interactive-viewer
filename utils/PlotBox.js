/*!
    PlotBox.js
    Copyright (c) 2019 Joey Litalien <joey.litalien@mail.mcgill.ca>
    Released under the MIT license

    Permission is hereby granted, free of charge, to any person obtaining a copy of this
    software and associated documentation files (the "Software"), to deal in the Software
    without restriction, including without limitation the rights to use, copy, modify,
    merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
    permit persons to whom the Software is furnished to do so, subject to the following
    conditions:

    The above copyright notice and this permission notice shall be included in all copies
    or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
    OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

var plotBoxSettings = {
    width: 1152
};

var PlotBox = function(parent, title, stats) {
    
    // Selection tabs
    var selectorGroup = document.createElement("div");
    selectorGroup.className = "selector-group";
    this.selectors = [];
    for (var i = 0; i < stats[0]['series'].length; i++) {
        var selector = document.createElement("div");
        selector.className = "selector selector-primary";
        if (i == 0)
            selector.className += " active";
        selector.appendChild(document.createTextNode(stats[0]['series'][i]['label']));

        selector.addEventListener("click", function(idx, event) {
            this.selectPlot(idx);
        }.bind(this, i));

        this.selectors.push(selector);
        selectorGroup.appendChild(selector);
    }

    // Header
    var h1 = document.createElement("h1");
    h1.className = "title";
    h1.appendChild(document.createTextNode(title));

    // Plot canvas
    var box = document.createElement("div");
    box.className = "plot-box";
    box.style.width = plotBoxSettings.width+"px";

    // Plot
    var plot = document.createElement("div");
    plot.setAttribute("id", "metric-plot");

    // Add to canvas
    box.appendChild(h1);
    box.appendChild(selectorGroup);
    box.appendChild(plot);

    // Read data
    this.plots = [];
    for (var i = 0; i < stats[0]["series"].length; i++) {
        var traces = []
        for (var j = 0; j < stats[0]["series"][i]["track"].length; ++j) {
            var trace = {
                x: [10, 20, 30, 40, 50],
                y: stats[0]["series"][i]["track"][j],
                type: "scatter",
                name: stats[0]["labels"][j]
            };
            traces.push(trace);
        }
        this.plots.push(traces);
    }

    // Styling
    var options = {
        xaxis: { title: "Times (s)", titlefont: {size: 14, color: "#aaa"}, type: "log", autorange: true },
        yaxis: { title: "Metric",  titlefont: {size: 14, color: "#aaa"}, type: "log", autorange: true },
        margin: { l: 64, r: 64, b: 64, t: 64, pad: 12 },
        font: { family: 'Roboto', size: 14, color: '#555' },
        width: plotBoxSettings["width"] - 2
    };

    parent.append(box);

    // Plot selection toggle
    PlotBox.prototype.selectPlot = function(idx) {
        for (var i = 0; i < this.plots.length; i++) {
            if (i == idx) {
                this.selectors[i].className += " active";
                Plotly.react("metric-plot", this.plots[i], options, {displayModeBar: false});
            } else {
                this.selectors[i].className = this.selectors[i].className.replace( /(?:^|\s)active(?!\S)/g , '');
            }
        }
    };

    Plotly.newPlot("metric-plot", this.plots[0], options, {displayModeBar: false});
}