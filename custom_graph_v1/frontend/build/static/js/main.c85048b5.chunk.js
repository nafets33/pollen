/*! For license information please see main.c85048b5.chunk.js.LICENSE.txt */
(this.webpackJsonpstreamlit_custom_graph=this.webpackJsonpstreamlit_custom_graph||[]).push([[0],{30:function(t,e,r){t.exports=r(45)},45:function(t,e,r){"use strict";r.r(e);var n=r(11),o=r.n(n),a=r(28),i=r.n(a),c=r(5),u=r(9),s=r(6),l=r(0),h=r(1),f=r(13),p=r(2),d=r(3),v=r(24),y=r(25),g=r(23),m=r.n(g),x=(r(40),r(47));function b(){b=function(){return t};var t={},e=Object.prototype,r=e.hasOwnProperty,n=Object.defineProperty||function(t,e,r){t[e]=r.value},o="function"==typeof Symbol?Symbol:{},a=o.iterator||"@@iterator",i=o.asyncIterator||"@@asyncIterator",c=o.toStringTag||"@@toStringTag";function u(t,e,r){return Object.defineProperty(t,e,{value:r,enumerable:!0,configurable:!0,writable:!0}),t[e]}try{u({},"")}catch(C){u=function(t,e,r){return t[e]=r}}function s(t,e,r,o){var a=e&&e.prototype instanceof f?e:f,i=Object.create(a.prototype),c=new O(o||[]);return n(i,"_invoke",{value:_(t,r,c)}),i}function l(t,e,r){try{return{type:"normal",arg:t.call(e,r)}}catch(C){return{type:"throw",arg:C}}}t.wrap=s;var h={};function f(){}function p(){}function d(){}var v={};u(v,a,(function(){return this}));var y=Object.getPrototypeOf,g=y&&y(y(S([])));g&&g!==e&&r.call(g,a)&&(v=g);var m=d.prototype=f.prototype=Object.create(v);function x(t){["next","throw","return"].forEach((function(e){u(t,e,(function(t){return this._invoke(e,t)}))}))}function w(t,e){var o;n(this,"_invoke",{value:function(n,a){function i(){return new e((function(o,i){!function n(o,a,i,c){var u=l(t[o],t,a);if("throw"!==u.type){var s=u.arg,h=s.value;return h&&"object"==typeof h&&r.call(h,"__await")?e.resolve(h.__await).then((function(t){n("next",t,i,c)}),(function(t){n("throw",t,i,c)})):e.resolve(h).then((function(t){s.value=t,i(s)}),(function(t){return n("throw",t,i,c)}))}c(u.arg)}(n,a,o,i)}))}return o=o?o.then(i,i):i()}})}function _(t,e,r){var n="suspendedStart";return function(o,a){if("executing"===n)throw new Error("Generator is already running");if("completed"===n){if("throw"===o)throw a;return j()}for(r.method=o,r.arg=a;;){var i=r.delegate;if(i){var c=E(i,r);if(c){if(c===h)continue;return c}}if("next"===r.method)r.sent=r._sent=r.arg;else if("throw"===r.method){if("suspendedStart"===n)throw n="completed",r.arg;r.dispatchException(r.arg)}else"return"===r.method&&r.abrupt("return",r.arg);n="executing";var u=l(t,e,r);if("normal"===u.type){if(n=r.done?"completed":"suspendedYield",u.arg===h)continue;return{value:u.arg,done:r.done}}"throw"===u.type&&(n="completed",r.method="throw",r.arg=u.arg)}}}function E(t,e){var r=e.method,n=t.iterator[r];if(void 0===n)return e.delegate=null,"throw"===r&&t.iterator.return&&(e.method="return",e.arg=void 0,E(t,e),"throw"===e.method)||"return"!==r&&(e.method="throw",e.arg=new TypeError("The iterator does not provide a '"+r+"' method")),h;var o=l(n,t.iterator,e.arg);if("throw"===o.type)return e.method="throw",e.arg=o.arg,e.delegate=null,h;var a=o.arg;return a?a.done?(e[t.resultName]=a.value,e.next=t.nextLoc,"return"!==e.method&&(e.method="next",e.arg=void 0),e.delegate=null,h):a:(e.method="throw",e.arg=new TypeError("iterator result is not an object"),e.delegate=null,h)}function L(t){var e={tryLoc:t[0]};1 in t&&(e.catchLoc=t[1]),2 in t&&(e.finallyLoc=t[2],e.afterLoc=t[3]),this.tryEntries.push(e)}function k(t){var e=t.completion||{};e.type="normal",delete e.arg,t.completion=e}function O(t){this.tryEntries=[{tryLoc:"root"}],t.forEach(L,this),this.reset(!0)}function S(t){if(t){var e=t[a];if(e)return e.call(t);if("function"==typeof t.next)return t;if(!isNaN(t.length)){var n=-1,o=function e(){for(;++n<t.length;)if(r.call(t,n))return e.value=t[n],e.done=!1,e;return e.value=void 0,e.done=!0,e};return o.next=o}}return{next:j}}function j(){return{value:void 0,done:!0}}return p.prototype=d,n(m,"constructor",{value:d,configurable:!0}),n(d,"constructor",{value:p,configurable:!0}),p.displayName=u(d,c,"GeneratorFunction"),t.isGeneratorFunction=function(t){var e="function"==typeof t&&t.constructor;return!!e&&(e===p||"GeneratorFunction"===(e.displayName||e.name))},t.mark=function(t){return Object.setPrototypeOf?Object.setPrototypeOf(t,d):(t.__proto__=d,u(t,c,"GeneratorFunction")),t.prototype=Object.create(m),t},t.awrap=function(t){return{__await:t}},x(w.prototype),u(w.prototype,i,(function(){return this})),t.AsyncIterator=w,t.async=function(e,r,n,o,a){void 0===a&&(a=Promise);var i=new w(s(e,r,n,o),a);return t.isGeneratorFunction(r)?i:i.next().then((function(t){return t.done?t.value:i.next()}))},x(m),u(m,c,"Generator"),u(m,a,(function(){return this})),u(m,"toString",(function(){return"[object Generator]"})),t.keys=function(t){var e=Object(t),r=[];for(var n in e)r.push(n);return r.reverse(),function t(){for(;r.length;){var n=r.pop();if(n in e)return t.value=n,t.done=!1,t}return t.done=!0,t}},t.values=S,O.prototype={constructor:O,reset:function(t){if(this.prev=0,this.next=0,this.sent=this._sent=void 0,this.done=!1,this.delegate=null,this.method="next",this.arg=void 0,this.tryEntries.forEach(k),!t)for(var e in this)"t"===e.charAt(0)&&r.call(this,e)&&!isNaN(+e.slice(1))&&(this[e]=void 0)},stop:function(){this.done=!0;var t=this.tryEntries[0].completion;if("throw"===t.type)throw t.arg;return this.rval},dispatchException:function(t){if(this.done)throw t;var e=this;function n(r,n){return i.type="throw",i.arg=t,e.next=r,n&&(e.method="next",e.arg=void 0),!!n}for(var o=this.tryEntries.length-1;o>=0;--o){var a=this.tryEntries[o],i=a.completion;if("root"===a.tryLoc)return n("end");if(a.tryLoc<=this.prev){var c=r.call(a,"catchLoc"),u=r.call(a,"finallyLoc");if(c&&u){if(this.prev<a.catchLoc)return n(a.catchLoc,!0);if(this.prev<a.finallyLoc)return n(a.finallyLoc)}else if(c){if(this.prev<a.catchLoc)return n(a.catchLoc,!0)}else{if(!u)throw new Error("try statement without catch or finally");if(this.prev<a.finallyLoc)return n(a.finallyLoc)}}}},abrupt:function(t,e){for(var n=this.tryEntries.length-1;n>=0;--n){var o=this.tryEntries[n];if(o.tryLoc<=this.prev&&r.call(o,"finallyLoc")&&this.prev<o.finallyLoc){var a=o;break}}a&&("break"===t||"continue"===t)&&a.tryLoc<=e&&e<=a.finallyLoc&&(a=null);var i=a?a.completion:{};return i.type=t,i.arg=e,a?(this.method="next",this.next=a.finallyLoc,h):this.complete(i)},complete:function(t,e){if("throw"===t.type)throw t.arg;return"break"===t.type||"continue"===t.type?this.next=t.arg:"return"===t.type?(this.rval=this.arg=t.arg,this.method="return",this.next="end"):"normal"===t.type&&e&&(this.next=e),h},finish:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e];if(r.finallyLoc===t)return this.complete(r.completion,r.afterLoc),k(r),h}},catch:function(t){for(var e=this.tryEntries.length-1;e>=0;--e){var r=this.tryEntries[e];if(r.tryLoc===t){var n=r.completion;if("throw"===n.type){var o=n.arg;k(r)}return o}}throw new Error("illegal catch attempt")},delegateYield:function(t,e,r){return this.delegate={iterator:S(t),resultName:e,nextLoc:r},"next"===this.method&&(this.arg=void 0),h}},t}var w=v.a.CanvasJSChart,_=v.a.CanvasJS,E=[[],[],[],[],[],[],[],[],[],[]];m.a.options={positionClass:"toast-top-full-width",hideDuration:300,timeOut:3e3};var L=function(t){Object(p.a)(r,t);var e=Object(d.a)(r);function r(t){var n;return Object(l.a)(this,r),(n=e.call(this,t)).updateChart=n.updateChart.bind(Object(f.a)(n)),n.toggleDataSeries=n.toggleDataSeries.bind(Object(f.a)(n)),n}return Object(h.a)(r,[{key:"componentDidMount",value:function(){var t=this.props.args.kwargs,e=(t.y_axis,t.api,t.y_max,t.refresh_sec);t.graph_height;y.a.setFrameHeight(),this.updateChart(),e&&setInterval(this.updateChart,1e3*e)}},{key:"toggleDataSeries",value:function(t){"undefined"===typeof t.dataSeries.visible||t.dataSeries.visible?t.dataSeries.visible=!1:t.dataSeries.visible=!0,this.chart.render()}},{key:"fetchGraphData",value:function(){var t=Object(s.a)(b().mark((function t(){var e,r,n;return b().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return e=this.props.args.kwargs,e.y_axis,r=e.api,e.y_max,e.refresh_sec,t.next=4,x.a.post(r,Object(u.a)({},e));case 4:return n=t.sent,t.abrupt("return",JSON.parse(n.data));case 6:case"end":return t.stop()}}),t,this)})));return function(){return t.apply(this,arguments)}}()},{key:"updateChart",value:function(){var t=Object(s.a)(b().mark((function t(){var e,r,n,o,a,i,u,s=this;return b().wrap((function(t){for(;;)switch(t.prev=t.next){case 0:return e=this.props.args.kwargs,r=e.x_axis,n=e.y_axis,e.api,e.y_max,o=e.refresh_sec,a=e.refresh_button,t.prev=2,t.next=5,this.fetchGraphData();case 5:for(i=t.sent,u=[],n.map((function(t,e){return u[e]=i.map((function(e,n){return{x:e[r.field],y:e[t.field]}}))}));E[0].length;)n.map((function(t,e){E[e].pop()}));console.log("fetchGraphData",E),n.map((function(t,e){var r;(r=E[e]).push.apply(r,Object(c.a)(u[e])),s.chart.options.data[e].legendText=t.name+u[e].pop().y})),this.chart.render(),a&&!o&&m.a.success("Success!"),t.next=18;break;case 15:t.prev=15,t.t0=t.catch(2),a&&!o&&m.a.error("Fetch Error: ".concat(t.t0.message));case 18:case"end":return t.stop()}}),t,this,[[2,15]])})));return function(){return t.apply(this,arguments)}}()},{key:"render",value:function(){var t=this,e=[],r=this.props.args.kwargs,n=r.y_axis,a=(r.api,r.y_max),i=r.refresh_sec,c=r.theme_options,u=r.refresh_button,s=n.map((function(t,r){return e.push(t.color),{type:"spline",xValueFormatString:"#.##0 ",yValueFormatString:"#.##0",showInLegend:!0,name:t.name,dataPoints:E[r]}}));_.addColorSet("greenShades",e);var l={colorSet:"greenShades",backgroundColor:c.backgroundColor?c.backgroundColor:"white",zoomEnabled:!0,title:{text:c.main_title?c.main_title:""},axisX:{title:c.x_axis_title?c.x_axis_title:"",labelFormatter:function(t){return t.value}},axisY:{suffix:"",maximum:a||null,gridColor:c.grid_color?c.grid_color:""},toolTip:{shared:!0},legend:{cursor:"pointer",verticalAlign:"top",fontSize:18,fontColor:"dimGrey",itemclick:this.toggleDataSeries},data:s,height:r.graph_height?r.graph_height:400};return o.a.createElement("div",null,u&&!i&&o.a.createElement("div",{style:{display:"flex"}},o.a.createElement("div",{style:{margin:"10px 10px 10px 2px"}},o.a.createElement("button",{className:"btn btn-warning",onClick:this.updateChart},"Refresh"))),o.a.createElement(w,{options:l,onRef:function(e){return t.chart=e}}))}}]),r}(n.Component),k=Object(y.b)(L);i.a.render(o.a.createElement(o.a.StrictMode,null,o.a.createElement(k,null)),document.getElementById("root"))}},[[30,1,2]]]);
//# sourceMappingURL=main.c85048b5.chunk.js.map