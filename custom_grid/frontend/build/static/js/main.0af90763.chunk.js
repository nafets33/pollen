(this.webpackJsonpstreamlit_custom_slider=this.webpackJsonpstreamlit_custom_slider||[]).push([[0],{117:function(e,t,a){},127:function(e,t,a){},132:function(e,t,a){"use strict";a.r(t);var r=a(2),l=a.n(r),o=a(13),s=a.n(o),n=a(20),c=(a(30),a(31),a(46)),m=a(8),i=a.n(m),u=(a(88),a(89),a(90),a(91),a(136)),d=(a(135),a(50)),p=a(29),f=(a(117),a(134)),b=a(48),g=a.n(b);a(127);g.a.setAppElement("#root");let y=!1;var h=e=>{let{isOpen:t,closeModal:a,modalData:o,promptText:s,setPromptText:n,toastr:c}=e;const{prompt_field:m,prompt_order_rules:i,selectedRow:u,selectedField:d}=o,p=Object(r.useRef)(),b=Object(r.useRef)();return Object(r.useEffect)(()=>{t&&setTimeout(()=>p.current.focus(),100)},[t]),Array.isArray(d)?l.a.createElement("div",{className:"my-modal",style:{display:t?"block":"none"}},l.a.createElement("div",{className:"my-modal-content"},l.a.createElement("div",{className:"modal-header px-4"},l.a.createElement("h4",null,o.prompt_message),l.a.createElement("span",{className:"close",onClick:a},"\xd7")),l.a.createElement("div",{className:"modal-body p-2"},l.a.createElement("label",{className:"px-1"},m," "),l.a.createElement("select",{name:"cars",id:"cars",defaultValue:d[0],ref:b},d.map(e=>l.a.createElement("option",{value:e},e)))),l.a.createElement("div",{className:"modal-footer"},l.a.createElement("button",{type:"button",className:"btn btn-primary",onClick:async()=>{if(console.log("selectRef.current.value :>> ",b.current.value),!y){y=!0;try{const e={username:o.username,prod:o.prod,selected_row:o.selectedRow,default_value:b.current.value,...o.kwargs};console.log("body :>> ",e);const{data:t}=await f.a.post(o.button_api,e),{status:r,data:l,description:s}=t;console.log("res :>> ",t),"success"==r?"fade"==l.message_type?c.success(s,"Success"):alert("Success!\nDescription: "+s):"fade"==l.message_type?c.error(s,"Error"):alert("Error!\nDescription: "+s),0!=(null===l||void 0===l?void 0:l.close_modal)&&a()}catch(e){console.log("error :>> ",e),c.error(e.message)}y=!1}},ref:p},"Ok"),l.a.createElement("button",{type:"button",className:"btn btn-secondary",onClick:a},"Cancel")))):i?l.a.createElement("div",{className:"my-modal",style:{display:t?"block":"none"}},l.a.createElement("div",{className:"my-modal-content"},l.a.createElement("div",{className:"modal-header px-4"},l.a.createElement("h4",null,o.prompt_message),l.a.createElement("span",{className:"close",onClick:a},"\xd7")),l.a.createElement("div",{className:"modal-body p-2"},i.map((e,t)=>"boolean"==typeof s[e]?l.a.createElement("div",{className:"d-flex flex-row justify-content-end",key:t},l.a.createElement("label",{className:"d-flex flex-row"},e+":  ",l.a.createElement("div",{className:"px-2",style:{width:"193px"}},l.a.createElement("input",{type:"checkbox",checked:s[e],onChange:t=>n({...s,[e]:t.target.checked})})))):Array.isArray(s[e])?l.a.createElement("div",{className:"d-flex flex-row justify-content-end",key:t},l.a.createElement("label",null,e+":  ",l.a.createElement("select",{value:s[e][0],onChange:t=>n({...s,[e]:[t.target.value]})},s[e].map((e,t)=>l.a.createElement("option",{key:t,value:e},e))))):l.a.createElement("div",{className:"d-flex flex-row justify-content-end",key:t},l.a.createElement("label",null,e+":  ",l.a.createElement("input",{type:"text",value:s[e],onChange:t=>n({...s,[e]:t.target.value})}))))),l.a.createElement("div",{className:"modal-footer"},l.a.createElement("button",{type:"button",className:"btn btn-primary",onClick:async()=>{if(!y){y=!0;try{const e={username:o.username,prod:o.prod,selected_row:o.selectedRow,default_value:s,...o.kwargs};console.log("body :>> ",e);const{data:t}=await f.a.post(o.button_api,e),{status:r,data:l,description:n}=t;"success"==r?"fade"==l.message_type?c.success(n,"Success"):alert("Success!\nDescription: "+n):"fade"==l.message_type?c.error(n,"Error"):alert("Error!\nDescription: "+n),0!=(null===l||void 0===l?void 0:l.close_modal)&&a()}catch(e){console.log("error :>> ",e),c.error(e.message)}y=!1}},ref:p},"Ok"),l.a.createElement("button",{type:"button",className:"btn btn-secondary",onClick:a},"Cancel")))):l.a.createElement("div",{className:"my-modal",style:{display:t?"block":"none"}},l.a.createElement("div",{className:"my-modal-content"},l.a.createElement("div",{className:"modal-header px-4"},l.a.createElement("h4",null,o.prompt_message),l.a.createElement("span",{className:"close",onClick:a},"\xd7")),l.a.createElement("div",{className:"modal-body p-2"},l.a.createElement("textarea",{className:"form-control",rows:4,cols:50,type:"text",value:s,placeholder:"Please input text",onChange:e=>n(e.target.value)})),l.a.createElement("div",{className:"modal-footer"},l.a.createElement("button",{type:"button",className:"btn btn-primary",onClick:async()=>{if(!y){y=!0;try{const{data:e}=await f.a.post(o.button_api,{username:o.username,prod:o.prod,selected_row:o.selectedRow,default_value:s,...o.kwargs}),{status:t,data:r,description:l}=e;console.log("res :>> ",e),"success"==t?"fade"==r.message_type?c.success(l,"Success"):alert("Success!\nDescription: "+l):"fade"==r.message_type?c.error(l,"Error"):alert("Error!\nDescription: "+l),0!=(null===r||void 0===r?void 0:r.close_modal)&&a()}catch(e){console.log("error :>> ",e),c.error(e.message)}y=!1}},ref:p},"Ok"),l.a.createElement("button",{type:"button",className:"btn btn-secondary",onClick:a},"Cancel"))))};let _=[],v=null;function E(e,t){try{let a=new Date(e);return Object(d.a)(a,t)}catch{return e}}function w(e,t){let a=Number.parseFloat(e);return Number.isNaN(a)?e:t+a.toFixed(2)}function N(e,t){let a=Number.parseFloat(e);return Number.isNaN(a)?e:a.toFixed(t)}const k=e=>l.a.createElement("a",{href:"".concat(e.column.colDef.baseURL,"/").concat(e.data[e.column.colDef.linkField]),target:"_blank"},e.value);i.a.options={positionClass:"toast-top-full-width",hideDuration:300,timeOut:3e3};var x=e=>{const t=e=>l.a.createElement("button",{onClick:()=>{e.clicked(e.node.id)},style:{background:"transparent",width:"100%",borderColor:e.borderColor?e.borderColor:"black"}},e.col_header?e.value:e.buttonName),a=Object(r.useRef)(null),{username:o,api:s,api_update:m,refresh_sec:d,refresh_cutoff_sec:b=0,prod:g=!0,index:y,kwargs:x}=e;let{grid_options:C={}}=e;const{buttons:F,toggle_views:O}=x,[j,D]=Object(r.useState)([]),[R,S]=Object(r.useState)(!1),[A,T]=Object(r.useState)({}),[P,M]=Object(r.useState)(""),[I,H]=Object(r.useState)(0);Object(r.useEffect)(()=>{n.a.setFrameHeight(),F.length&&F.map(e=>{const{prompt_field:a,prompt_message:r,button_api:l,prompt_order_rules:s}=e;C.columnDefs.push({field:e.col_header?e.col_header:y,headerName:e.col_headername,width:e.col_width,pinned:e.pinned,cellRenderer:t,cellRendererParams:{col_header:e.col_header,buttonName:e.button_name,borderColor:e.border_color,clicked:async function(e){try{const t=_.find(t=>t[y]==e);if(s){const e=t[a],n="string"===typeof e?JSON.parse(t[a].replace(/'/g,'"').replace(/\n/g,"").replace(/\s/g,"").replace(/False/g,"false").replace(/True/g,"true")):e;S(!0),T({prompt_message:r,button_api:l,username:o,prod:g,selectedRow:t,kwargs:x,prompt_field:a,prompt_order_rules:s,selectedField:n});const c={};s.map(e=>{c[e]=n[e]}),M(c)}else if(a&&r)S(!0),T({prompt_message:r,button_api:l,username:o,prod:g,selectedRow:t,kwargs:x}),M(t[a]);else{if(window.confirm(r)){await f.a.post(l,{username:o,prod:g,selected_row:t,...x})}i.a.success("Success!")}}catch(t){alert("".concat(t))}}}})})});const U=async()=>{const e=await z();if(!1===e)return!1;const t=a.current.api,r=e.map(e=>e[y]),l=_.map(e=>e[y]),o=e.filter(e=>r.includes(e[y])),s=_.filter(e=>!r.includes(e[y])),n=e.filter(e=>!l.includes(e[y]));return t.applyTransactionAsync({update:o,remove:s,add:n}),_=e,!0};Object(r.useEffect)(()=>{V()},[I]);const z=async()=>{try{const e=await f.a.post(s,{username:o,prod:g,...x,toggle_view_selection:O?O[I]:"none"}),t=JSON.parse(e.data);return console.log("toggle_views[viewId],viewId :>> ",O[I],I),console.log("table data :>> ",t),0==t.status?(i.a.error("Fetch Error: ".concat(t.message)),!1):t}catch(e){return i.a.error("Fetch Error: ".concat(e.message)),!1}};Object(r.useEffect)(()=>{if(d&&d>0){const t=setInterval(U,1e3*d);let a;return b>0&&(console.log(b),a=setTimeout(()=>{clearInterval(t),console.log("Fetching data ended, refresh rate:",d)},1e3*b)),console.error("rendered==========",e),()=>{clearInterval(t),a&&clearTimeout(a)}}},[e,I]);Object(r.useCallback)(e=>{const t=[];a.current.columnApi.getColumns().forEach(e=>{t.push(e.getId())}),a.current.columnApi.autoSizeColumns(t,e)},[]),Object(r.useCallback)(()=>{a.current.api.sizeColumnsToFit({defaultMinWidth:100})},[]);const G=Object(r.useCallback)(async e=>{setTimeout(async()=>{try{const e=await z();if(0==e)return;D(e),_=e}catch(e){i.a.error("Error: ".concat(e.message))}},100)},[]),J=Object(r.useMemo)(()=>({minWidth:200}),[]),K=Object(r.useMemo)(()=>e=>e.data[y],[y]),L=(Object(r.useMemo)(()=>({toolPanels:[{id:"columns",labelDefault:"Columns",labelKey:"columns",iconKey:"columns",toolPanel:"agColumnsToolPanel"},{id:"filters",labelDefault:"Filters",labelKey:"filters",iconKey:"filter",toolPanel:"agFiltersToolPanel"}],defaultToolPanel:"customStats"}),[]),Object(r.useCallback)(e=>{null==v&&(v={}),v[e.data[y]]=e.data,console.log("Data after change is",v)},[])),V=async()=>{try{await U()&&i.a.success("Refresh success!")}catch(e){i.a.error("Refresh Failed! ".concat(e.message))}},W=Object(r.useMemo)(()=>({dateColumnFilter:{filter:"agDateColumnFilter",filterParams:{comparator:(e,t)=>Object(u.a)(new Date(t),e)}},numberColumnFilter:{filter:"agNumberColumnFilter"},shortDateTimeFormat:{valueFormatter:e=>E(e.value,"dd/MM/yyyy HH:mm")},customDateTimeFormat:{valueFormatter:e=>E(e.value,e.column.colDef.custom_format_string)},customNumericFormat:{valueFormatter:e=>{var t;return N(e.value,null!==(t=e.column.colDef.precision)&&void 0!==t?t:2)}},customCurrencyFormat:{valueFormatter:e=>w(e.value,e.column.colDef.custom_currency_symbol)},timedeltaFormat:{valueFormatter:e=>Object(p.duration)(e.value).humanize(!0)},customNumberFormat:{valueFormatter:e=>Number(e.value).toLocaleString("en-US",{minimumFractionDigits:0})},customHyperlinkRenderer:{cellRenderer:k,cellRendererParams:{baseURL:"URLSearchParams.co"}}}),[]);return l.a.createElement(l.a.Fragment,null,l.a.createElement(h,{isOpen:R,closeModal:()=>S(!1),modalData:A,promptText:P,setPromptText:M,toastr:i.a}),l.a.createElement("div",{style:{flexDirection:"row",height:"100%",width:"100"},id:"myGrid"},l.a.createElement("div",{className:"d-flex justify-content-between align-items-center"},(void 0==d||0==d)&&l.a.createElement("div",{style:{display:"flex"}},l.a.createElement("div",{style:{margin:"10px 10px 10px 2px"}},l.a.createElement("button",{className:"btn btn-warning",onClick:V},"Refresh")),l.a.createElement("div",{style:{margin:"10px 10px 10px 2px"}},l.a.createElement("button",{className:"btn btn-success",onClick:async()=>{if(null!=v)try{const e=await f.a.post(m,{username:o,prod:g,new_data:v,...x});v=null,e.status?i.a.success("Successfully Updated! "):i.a.error("Failed! ".concat(e.message))}catch(e){i.a.error("Failed! ".concat(e))}else i.a.warning("No changes to update")}},"Update"))),l.a.createElement("div",{className:"d-flex flex-row gap-6"},null===O||void 0===O?void 0:O.map((e,t)=>l.a.createElement("span",{className:""},l.a.createElement("button",{className:"btn ".concat(I==t?"btn-danger":"btn-secondary"),onClick:()=>H(t)},e))))),l.a.createElement("div",{className:C.theme||"ag-theme-alpine-dark",style:{width:"100%",height:x.grid_height?x.grid_height:"100%"}},l.a.createElement(c.AgGridReact,{ref:a,rowData:j,getRowStyle:e=>({background:e.data.color_row,color:e.data.color_row_text}),rowStyle:{fontSize:12,padding:0},headerHeight:30,rowHeight:30,onGridReady:G,autoGroupColumnDef:J,animateRows:!0,suppressAggFuncInHeader:!0,getRowId:K,gridOptions:C,onCellValueChanged:L,columnTypes:W}))))};var C=Object(n.b)(e=>{const{username:t,api:a,api_update:r,refresh_sec:o,refresh_cutoff_sec:s,gridoption_build:n,prod:c}=e.args,{grid_options:m,kwargs:i={}}=e.args,{index:u,theme:d}=m;return console.log("AAAAAAAA",m),l.a.createElement("div",null,l.a.createElement(x,{username:t,api:a,api_update:r,refresh_sec:o,refresh_cutoff_sec:s,gridoption_build:n,prod:c,grid_options:m,index:u,kwargs:i}))});s.a.render(l.a.createElement(l.a.StrictMode,null,l.a.createElement(C,null)),document.getElementById("root"))},56:function(e,t,a){e.exports=a(132)}},[[56,1,2]]]);
//# sourceMappingURL=main.0af90763.chunk.js.map