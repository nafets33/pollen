(this.webpackJsonpstreamlit_custom_graph=this.webpackJsonpstreamlit_custom_graph||[]).push([[0],{14:function(t,e,a){t.exports=a(30)},30:function(t,e,a){"use strict";a.r(e);var r=a(2),s=a.n(r),o=a(12),i=a.n(o),n=a(8),l=a(6),c=a.n(l),h=a(7),p=a.n(h),m=(a(23),a(32)),d=a(9),g=n.a.CanvasJSChart,u=n.a.CanvasJS;const _=[[],[],[],[],[],[],[],[],[],[]];p.a.options={positionClass:"toast-top-full-width",hideDuration:300,timeOut:3e3};class x extends r.Component{constructor(t){super(t),this.updateChart=this.updateChart.bind(this),this.toggleDataSeries=this.toggleDataSeries.bind(this)}componentDidMount(){const{kwargs:t}=this.props.args,{y_axis:e,api:a,y_max:r,refresh_sec:s,graph_height:o}=t;d.a.setFrameHeight(),this.updateChart(),s&&setInterval(this.updateChart,1e3*s)}toggleDataSeries(t){"undefined"===typeof t.dataSeries.visible||t.dataSeries.visible?t.dataSeries.visible=!1:t.dataSeries.visible=!0,this.chart.render()}async fetchGraphData(){const{kwargs:t}=this.props.args,{y_axis:e,api:a,y_max:r,refresh_sec:s}=t,o=await m.a.post(a,{...t});return JSON.parse(o.data)}async updateChart(){const{kwargs:t}=this.props.args,{x_axis:e,y_axis:a,api:r,y_max:s,refresh_sec:o,refresh_button:i,theme_options:n}=t;try{const t=await this.fetchGraphData(),r=[];for(a.map((a,s)=>r[s]=t.map((t,r)=>({x:r,y:t[a.field],timeStamp:t[e.field]})));_[0].length;)a.map((t,e)=>{_[e].pop()});a.map((t,e)=>{_[e].push(...r[e]),this.chart.options.data[e].legendText=t.name+r[e].pop().y}),this.chart.options.axisX.labelFormatter=function(t){const e=_[0][t.value];return c()(e.timeStamp).format("MM/DD/YY hh")},this.chart.render(),i&&!o&&p.a.success("Success!")}catch(l){i&&!o&&p.a.error("Fetch Error: ".concat(l.message))}}render(){const t=[],{kwargs:e}=this.props.args,{y_axis:a,api:r,y_max:o,refresh_sec:i,theme_options:n,refresh_button:l}=e,h=a.map((e,a)=>(t.push(e.color),{type:"spline",xValueFormatString:"#.##0 ",yValueFormatString:"#.##0",showInLegend:n.showInLegend,name:e.name,dataPoints:_[a]}));u.addColorSet("greenShades",t);const p={colorSet:"greenShades",backgroundColor:n.backgroundColor?n.backgroundColor:"white",zoomEnabled:!0,title:{text:n.main_title?n.main_title:""},axisX:{title:n.x_axis_title?n.x_axis_title:"",labelFormatter:t=>c()(t.value).format("MM/DD/YY hh"),labelFontSize:12},axisY:{suffix:"",maximum:o||null,gridColor:n.grid_color?n.grid_color:""},toolTip:{shared:!0,contentFormatter:function(t){let e="";const a=c()(t.entries[0].dataPoint.timeStamp).format("MM/DD/YY HH:mm");e+="<strong>Date</strong>: ".concat(a,"<br/>");for(let r=1;r<t.entries.length;r++){const a=t.entries[r],s=a.dataSeries,o=a.dataPoint,i=s.color?s.color:s.options.color;e+='<strong style="color: '.concat(i,'">').concat(s.name,"</strong>: ").concat(o.y,"<br/>")}return e}},legend:{cursor:"pointer",verticalAlign:"top",fontSize:18,fontColor:"dimGrey",itemclick:this.toggleDataSeries},data:h,height:e.graph_height?e.graph_height:400};return s.a.createElement("div",null,l&&!i&&s.a.createElement("div",{style:{display:"flex"}},s.a.createElement("div",{style:{margin:"10px 10px 10px 2px"}},s.a.createElement("button",{className:"btn btn-warning",onClick:this.updateChart},"Refresh"))),s.a.createElement(g,{options:p,onRef:t=>this.chart=t}))}}var f=Object(d.b)(x);i.a.render(s.a.createElement(s.a.StrictMode,null,s.a.createElement(f,null)),document.getElementById("root"))}},[[14,1,2]]]);
//# sourceMappingURL=main.09c0b9bc.chunk.js.map