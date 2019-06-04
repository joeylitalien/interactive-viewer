/*!
    ImageBox.js
    Copyright (c) 2016 Jan Novak <novakj4@gmail.com> and Benedikt Bitterli <benedikt.bitterli@gmail.com>
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

    The wheelzoom class is based on code written by Jack Moore.
    The original source code is released under the MIT license
    and can be found at http://www.jacklmoore.com/wheelzoom.
*/

var imageBoxSettings = {
    zoom: 0.1,
    width: 1152,
    height: 720
};

window.wheelzoom = (function(){

    var canvas = document.createElement('canvas');

    var main = function(img, settings){
        if (!img || !img.nodeName || img.nodeName !== 'IMG') { return; }

        var width;
        var height;
        var previousEvent;
        var cachedDataUrl;

        function setSrcToBackground(img) {
            img.style.backgroundImage = 'url("'+img.src+'")';
            img.style.backgroundRepeat = 'no-repeat';
            canvas.width = settings.width;
            canvas.height = Math.min(720, canvas.width * (img.imHeight / img.imWidth));
            img.bgOffsetX = (canvas.width - img.naturalWidth)/2;
            img.bgOffsetY = (canvas.height - img.naturalHeight)/2;
            cachedDataUrl = canvas.toDataURL();
            img.src = cachedDataUrl;

            reset();
        }

        function updateBgStyle() {

            var minX = -img.bgOffsetX;
            var maxX = img.imWidth - img.bgWidth + img.bgOffsetX;
            if (img.bgWidth - img.bgOffsetX * 2 >= img.imWidth) {
                img.bgPosX = Math.max(Math.min(img.bgPosX, minX), maxX);
            } else {
                img.bgPosX = Math.min(Math.max(img.bgPosX, minX), maxX);
            }

            var minY = -img.bgOffsetY;
            var maxY = img.imHeight - img.bgHeight + img.bgOffsetY;
            if (img.bgHeight - img.bgOffsetY * 2 >= img.imHeight) {
                img.bgPosY = Math.max(Math.min(img.bgPosY, minY), maxY);
            } else {
                img.bgPosY = Math.min(Math.max(img.bgPosY, minY), maxY);
            }

            img.style.backgroundSize = img.bgWidth+'px '+img.bgHeight+'px';
            img.style.backgroundPosition = (img.bgOffsetX + img.bgPosX)+'px '+ (img.bgOffsetY + img.bgPosY)+'px';

            // // Apply anti-aliasing when not zoomed in too much, and when not viewing at a power of 2.
            // var globalZoomFactor = img.bgWidth / img.imWidth;
            // if (globalZoomFactor > 4 || (globalZoomFactor >= 1 && Math.log2(globalZoomFactor) % 1 < 0.001)) {
            //     img.className = "image-display pixelated";
            // } else {
            //     img.className = "image-display";
            // }
        }

        function reset() {

            if (canvas) {
                var zoomFactor = Math.min(canvas.width / img.imWidth, canvas.height / img.imHeight);
            } else {
                var zoomFactor = 1;
            }

            img.bgWidth = img.imWidth * zoomFactor;
            img.bgHeight = img.imHeight * zoomFactor;
            img.bgPosX = (img.imWidth - img.bgWidth) / 2;
            img.bgPosY = (img.imHeight - img.bgHeight) / 2;
            updateBgStyle();
        }

        function onwheel(e) {
            var deltaY = 0;

            e.preventDefault();

            if (e.deltaY) { // FireFox 17+ (IE9+, Chrome 31+?)
                deltaY = -e.deltaY;
            } else if (e.wheelDelta) {
                deltaY = e.wheelDelta;
            }

            // As far as I know, there is no good cross-browser way to get the cursor position relative to the event target.
            // We have to calculate the target element's position relative to the document, and subtrack that from the
            // cursor's position relative to the document.
            var rect = img.getBoundingClientRect();
            var offsetX = e.pageX - rect.left - window.pageXOffset - img.bgOffsetX;
            var offsetY = e.pageY - rect.top - window.pageYOffset - img.bgOffsetY;

            // Record the offset between the bg edge and cursor:
            var bgCursorX = offsetX - img.bgPosX;
            var bgCursorY = offsetY - img.bgPosY;

            // Use the previous offset to get the percent offset between the bg edge and cursor:
            var bgRatioX = bgCursorX/img.bgWidth;
            var bgRatioY = bgCursorY/img.bgHeight;

            var zoomFactor = 1 + settings.zoom;
            if (deltaY >= 0) {
                zoomFactor = 1 / zoomFactor;
            }

            img.bgWidth *= zoomFactor;
            img.bgHeight *= zoomFactor;

            // Take the percent offset and apply it to the new size:
            img.bgPosX = offsetX - (img.bgWidth * bgRatioX);
            img.bgPosY = offsetY - (img.bgHeight * bgRatioY);

            updateBgStyle();
        }

        function drag(e) {
            e.preventDefault();
            img.bgPosX += (e.pageX - previousEvent.pageX);
            img.bgPosY += (e.pageY - previousEvent.pageY);
            previousEvent = e;
            updateBgStyle();
        }

        function removeDrag() {
            document.removeEventListener('mouseup', removeDrag);
            document.removeEventListener('mousemove', drag);
        }

        // Make the background draggable
        function draggable(e) {
            e.preventDefault();
            previousEvent = e;
            document.addEventListener('mousemove', drag);
            document.addEventListener('mouseup', removeDrag);
        }

        function load() {
            if (img.src === cachedDataUrl) return;

            img.imWidth = img.naturalWidth;
            img.imHeight = img.naturalHeight;

            img.bgWidth = img.imWidth;
            img.bgHeight = img.imHeight;
            img.bgPosX = 0;
            img.bgPosY = 0;

            img.style.backgroundSize     = img.bgWidth+'px '+img.bgHeight+'px';
            img.style.backgroundPosition = img.bgPosX+' '+img.bgPosY;

            setSrcToBackground(img);

            img.addEventListener('wheelzoom.reset', reset);
            img.addEventListener('wheel', onwheel);
            img.addEventListener('mousedown', draggable);
        }

        var destroy = function (originalProperties) {
            img.removeEventListener('wheelzoom.destroy', destroy);
            img.removeEventListener('wheelzoom.reset', reset);
            img.removeEventListener('load', load);
            img.removeEventListener('mouseup', removeDrag);
            img.removeEventListener('mousemove', drag);
            img.removeEventListener('mousedown', draggable);
            img.removeEventListener('wheel', onwheel);

            img.style.backgroundImage = originalProperties.backgroundImage;
            img.style.backgroundRepeat = originalProperties.backgroundRepeat;
            img.src = originalProperties.src;
        }.bind(null, {
            backgroundImage: img.style.backgroundImage,
            backgroundRepeat: img.style.backgroundRepeat,
            src: img.src
        });

        img.addEventListener('wheelzoom.destroy', destroy);

        if (img.complete) {
            load();
        }

        img.addEventListener('load', load);
    };

    // Do nothing in IE8
    if (typeof window.getComputedStyle !== 'function') {
        return function(elements) {
            return elements;
        };
    } else {
        return function(elements, settings) {
            if (elements && elements.length) {
                Array.prototype.forEach.call(elements, main, settings);
            } else if (elements && elements.nodeName) {
                main(elements, settings);
            }
            return elements;
        };
    }
}());


var ImageBox = function(parent, config) {
    var self = this;

    var box = document.createElement('div');
    box.className = "image-box";

    // var h1 = document.createElement('h1');
    // h1.className = "title";
    // h1.appendChild(document.createTextNode("Images"));
    // box.appendChild(h1);

    // var help = document.createElement('div');
    // help.appendChild(document.createTextNode("Use mouse wheel to zoom in/out, click and drag to pan. Press keys [1], [2], ... to switch between individual images."));
    // help.className = "help";
    // box.appendChild(help);

    this.tree = [];
    this.selection = [];
    this.buildTreeNode(config, 0, this.tree, box);

    for (var i = 0; i < this.selection.length; ++i) {
        this.selection[i] = 0;
    }
    this.showContent(0, 0);
    parent.appendChild(box);

    document.addEventListener("keypress", function(event) { self.keyPressHandler(event); });
}

ImageBox.prototype.buildTreeNode = function(config, level, nodeList, parent) {

    var self = this;

    var selectorGroup = document.createElement('div');
    selectorGroup.className = "selector-group";

    parent.appendChild(selectorGroup);

    var insets = [];

    for (var i = 0; i < config.length; i++) {
        // Create tab
        var selector = document.createElement('div');
        selector.className = "selector selector-primary";
        // selector.className += (i == 0) ? " active" : "";

        selector.addEventListener("click", function(l, idx, event) {
            this.showContent(l, idx);
        }.bind(this, level, i));

        // Add to tabs
        selectorGroup.appendChild(selector);

        // Create content
        var contentNode = {};
        contentNode.children = [];
        contentNode.selector = selector;

        var content;
        if (typeof(config[i].elements) !== 'undefined') {
            // Recurse
            content = document.createElement('div');
            this.buildTreeNode(config[i].elements, level+1, contentNode.children, content);
            selector.appendChild(document.createTextNode(config[i].title));
        } else {
            // Create image
            content = document.createElement('img');
            content.className = "image-display pixelated";
            content.src = config[i].image;
            wheelzoom(content, imageBoxSettings);
            var key = '';
            if (i < 9)
                key = i+1 + ": ";
            else if (i == 9)
                key = "0: ";
            else if (i == 10)
                key = "R: ";


            selector.appendChild(document.createTextNode(key+config[i].title));
            // selector.appendChild(document.createElement('br'));
            // selector.appendChild(document.createTextNode(config[i].version));
            this.selection.length = Math.max(this.selection.length, level+1);

            // Create inset
            var inset = document.createElement('img');
            inset.className = "inset pixelated";
            inset.style.backgroundImage = "url('" + config[i].image + "')";
            inset.style.backgroundRepeat = "no-repeat";
            inset.style.border = "0px solid black";
            inset.style.width  = Math.min(256, imageBoxSettings.width / config.length-4) + "px";
            inset.style.height = Math.min(256, imageBoxSettings.width / config.length-4) + "px";
            if (config[i].version != '-') {
                inset.name = config[i].title + '_' + config[i].version;
            } else {
                inset.name = config[i].title;
            }
            var canvas = document.createElement("canvas");
            cachedDataUrl = canvas.toDataURL();
            inset.src = cachedDataUrl;
            insets.push(inset);

            content.addEventListener("mousemove", function(content, insets, event) {
                this.mouseMoveHandler(event, content, insets);
            }.bind(this, content, insets));
            content.addEventListener("wheel", function(content, insets, event) {
                this.mouseMoveHandler(event, content, insets);
            }.bind(this, content, insets));

        }
        content.style.display = 'none';
        parent.appendChild(content);
        contentNode.content = content;
        nodeList.push(contentNode);
    }

    if (insets.length > 0) {
        var insetGroup = document.createElement('table');
        insetGroup.className = "insets";
        insetGroup.width = imageBoxSettings.width;
        var tr = document.createElement('tr');
        tr.className = "insets";
        insetGroup.appendChild(tr);

        for (var i = 0; i < insets.length; ++i) {
            var auxDiv = document.createElement('td');
            auxDiv.className = "insets";
            auxDiv.style.width = (imageBoxSettings.width / insets.length) + "px";
            insetTitle = document.createElement('div');
            insetTitle.append(document.createTextNode(insets[i].name));
            auxDiv.appendChild(insetTitle);
            // auxDiv.appendChild(document.createTextNode(insets[i].name));
            auxDiv.appendChild(insets[i]);
            tr.appendChild(auxDiv);
        }
        parent.appendChild(insetGroup);
    }
}

ImageBox.prototype.showContent = function(level, idx) {
    // Hide
    var bgWidth = 0;
    var bgHeight = 0;
    var bgPosX = 0;
    var bgPosY = 0;
    var bgOffsetX = 0;
    var bgOffsetY = 0;
    var l = 0;
    var node = {};
    node.children = this.tree;
    while (node.children.length > 0 && node.children.length > this.selection[l]) {
        node = node.children[this.selection[l]];
        node.selector.className = 'selector selector-primary';
        node.content.style.display = 'none';
        if (l == this.selection.length-1) {
            bgWidth =   node.content.bgWidth;
            bgHeight =  node.content.bgHeight;
            bgPosX =    node.content.bgPosX;
            bgPosY =    node.content.bgPosY;
            bgOffsetX =  node.content.bgOffsetX;
            bgOffsetY =  node.content.bgOffsetY;
        }
        l += 1;
    }

    this.selection[level] = Math.max(0, idx);

    // Show
    l = 0;
    node = {};
    node.children = this.tree;
    while (node.children.length > 0) {
        if (this.selection[l] >= node.children.length)
            this.selection[l] = node.children.length - 1;
        node = node.children[this.selection[l]];
        node.selector.className = 'selector selector-primary active';
        node.content.style.display = 'block';
        if (l == this.selection.length-1) {
            node.content.bgWidth = bgWidth;
            node.content.bgHeight = bgHeight;
            node.content.bgPosX = bgPosX;
            node.content.bgPosY = bgPosY;
            node.content.bgOffsetX = bgOffsetX;
            node.content.bgOffsetY = bgOffsetY;
            node.content.style.backgroundSize = bgWidth+'px '+bgHeight+'px';
            node.content.style.backgroundPosition = (bgOffsetX + bgPosX)+'px '+ (bgOffsetY + bgPosY)+'px';
        }
        l += 1;
    }
}

ImageBox.prototype.keyPressHandler = function(event) {
    if (parseInt(event.charCode) == "0".charCodeAt(0)) {
        var idx = 9;
        this.showContent(this.selection.length-1, idx);
    } else {
        var idx = parseInt(event.charCode) - "1".charCodeAt(0);
        this.showContent(this.selection.length-1, idx);
    }
}

ImageBox.prototype.mouseMoveHandler = function(event, image, insets) {
    var rect = image.getBoundingClientRect();
    var xCoord = ((event.clientX - rect.left) - image.bgOffsetX - image.bgPosX) / (image.bgWidth  / image.imWidth);
    var yCoord = ((event.clientY - rect.top)  - image.bgOffsetY - image.bgPosY) / (image.bgHeight / image.imHeight);

    var scale = 2;
    for (var i = 0; i < insets.length; ++i) {
        insets[i].style.backgroundSize = (image.imWidth * scale) + "px " + (image.imHeight*scale) + "px";
        insets[i].style.backgroundPosition = (insets[i].width/2  - xCoord*scale) + "px "
                                           + (insets[i].height/2 - yCoord*scale) + "px";
    }
}
