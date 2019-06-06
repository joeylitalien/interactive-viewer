/*!
    ChartBox.js
    Copyright (c) 2016 Jan Novak <jan.novak@disneyresearch.com>
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

var TableBox = function(parent, title, stats) {

    var h1 = document.createElement("h1");
    h1.className = "title";
    h1.appendChild(document.createTextNode(title));

    var box = document.createElement("div");
    box.className = "table-box";

    box.appendChild(h1);

    for (var i = 0; i < stats.length; ++i) {
        var table = document.createElement("table");
        table.className = "stats";

        var thead = document.createElement("thead");
        thead.className = "stats";
        var tbody = document.createElement("tbody");
        tbody.className = "stats";

        table.appendChild(thead);
        table.appendChild(tbody);

        var tr = document.createElement("tr");
        tr.className = "stats";
        var td = document.createElement("th");
        td.className = "stats";
        td.appendChild(document.createTextNode('Metric'))
        tr.appendChild(td);
        for (var j = 0; j < stats[i]['labels'].length; ++j) {
            var td = document.createElement("th");
            td.className = "stats";
            td.appendChild(document.createTextNode(stats[i]['labels'][j]))
            tr.appendChild(td);
        }
        thead.appendChild(tr);

        for (var j = 0; j < stats[i]['series'].length; ++j) {
            var tr = document.createElement("tr");
            tr.className = "stats";
            var td = document.createElement("td");
            td.className = "stats";
            if (j == 0) {
                td.width = 100;
            }
            td.appendChild(document.createTextNode(stats[i]['series'][j]['label']))
            tr.appendChild(td);

            var err = stats[i]['series'][j]['data'].map(parseFloat);
            var bestIdx = err.indexOf(Math.min.apply(null, err.map(Number)));

            for (var k = 0; k < stats[i]['series'][j]['data'].length; ++k) {
                var td = document.createElement("td");
                td.className = "stats";
                var valueStr = err[k].toExponential().toString();
                if (k == bestIdx) {
                    td.className += " best-stat"
                }
                td.appendChild(document.createTextNode(valueStr.replace("-", "−")))
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
        // parent.appendChild(table);
    }

    box.appendChild(table);
    parent.append(box);
}
