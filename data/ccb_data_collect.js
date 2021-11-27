// JavaScript Document
//封装变量,只对外提供LinkClickFunction方法
(function () {
    //计算并保存客户端与服务端的时间差
    var diffTime = getccbCookie("diffTime2") || 0;
    if (!diffTime) {
        if (typeof jQuery === 'undefined') {
            var script = document.createElement("script");
            script.src = "http://www.ccb.com/cn/v3/js/jquery_pc.js";
            document.head.appendChild(script);
            script.onload = function () {
                setDiffTime(jQuery);
            }
        } else {
            setDiffTime(jQuery);
        }
    } else {
        Main();
    }

    function setDiffTime($) {
        return $.ajax({
            url: "/tran/WCCMainPlatV5?CCB_IBSVersion=V5&isAjaxRequest=true&SERVLET_NAME=WCCMainPlatV5&TXCODE=ZX2005",
            dataType: 'json',
            success: function (res) {
                var serverTime = res.M_TIME;
                var clientTime = +new Date;
                diffTime = +serverTime - clientTime;
            }
        }).always(function () {
            addccbCookie("diffTime2", diffTime, 24, "/", ".ccb.com");
            Main();
        })
    }

    function getCurrentDate() {
        var currentDate = new Date;
        var currentTime = +currentDate + +diffTime;
        currentDate.setTime(currentTime);
        return currentDate;
    }

    function getccbCookie(cookieName) {
        var cookieValue = "";
        var cookie = ";" + document.cookie.replace(/;\s+/g, ";") + ";"
        var pos = cookie.indexOf(";" + cookieName + "=");
        if (pos > -1) {
            var start = cookie.indexOf("=", pos);
            var end = cookie.indexOf(";", start);
            cookieValue = unescape(cookie.substring(start + 1, end));
        }
        return cookieValue;
    }

    function addccbCookie(cookieName, cookieValue, cookieHours, path, domain) {
        var str = cookieName + "=" + escape(cookieValue);
        var date = new Date();
        if (0 != cookieHours) {
            var ms = cookieHours * 3600 * 1000;
            date.setTime(date.getTime() + ms);
            str += ";expires=" + date.toGMTString();
        }
        str += ";path=" + path;
        str += ";domain=" + domain;
        document.cookie = str;
    }

    function delccbCookie(cookieName) {
        var exp = new Date();
        exp.setTime(exp.getTime() - 1);
        var cval = getccbCookie(cookieName);
        if (cval != null) document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
    }

    function Main() {
        var url = ["http://job.ccb.com"];//排除域名
        for (var i = 0; i < url.length; i++) {
            if (~window.location.href.indexOf(url[i])) {
                return;
            }
        }

        if (typeof (AcqWebPageID) == 'undefined') {//PAGEID不存在则生成默认PAGEID
            AcqWebPageID = "PAGE:CCVCC";
            var currentPageUrl = window.location.href;
            currentPageUrl = currentPageUrl.substring(currentPageUrl.indexOf("//") + 2);
            if (currentPageUrl.indexOf("/") > -1) {
                var urlArr = currentPageUrl.split("/");
                for (var i = 0; i < urlArr.length; i++) {
                    AcqWebPageID += ":" + urlArr[i];
                }
            }

        }

        if (typeof (headergettime) == 'undefined') {
            headergettime = 0;
        }
        var domtime = 0;
        var onloadtime = 0;
        var errMsg = "";
        var webinfo_first = true;
        var arrContent = {
            user_id: "",
            user_name: "",
            user_age: "",
            user_sex: "",
            user_tel: "",
            session_id: "",
            ori_session_id: "",
            page_type: "",
            pageid: "",
            page_title: "",
            is_page_view: "",
            page_url: "",
            page_visit_time: "",
            source_url: "",
            source_pagetitle: "",
            source_pageid: "",
            page_loading_time: "",
            html_loading_time: "",
            dom_loading_time: "",
            transfer_bytes: "",
            page_return_status: "",
            external_search_keyword: "",
            internal_search_keyword: "",
            ad_info: "",
            err_msg: "",
            err_code: "",
            form_name: "",
            form_id: "",
            form_return_status: "",
            text_content: "",
            combox_content: "",
            check_box: "",
            button_id: "",
            button_name: "",
            anchor_name: "",
            anchor_href: "",
            target_href_name: "",
            //产品信息类
            product_id: "",
            product_name: "",
            prompt_id: "",
            is_prompt: "",
            goods_name: "",
            goods_type: "",
            goods_price: "",
            cookie_id: "",
            oper_type: "",
            ip: "",
            gps: "",
            dev_type: "",
            browse_type_version: "",
            os_type_version: "",
            screen_resolution: "",
            color: "",
            flash_version: "",
            javascript_version: "",
            java_support: "",
            cookie_support: "",
            client_plugin: "",
            client_lang: "",
            client_zone: "",
            mechine_type: "",
            app_version: "",
            app_source: "",
            net_type: "",
            ukey_type: "",
            certificate_en: ""
        }

        function ccbGetElementsByClassName(className, element) {
            var dom = element || document
            if (dom.getElementsByClassName) {
                return dom.getElementsByClassName(className)[0];
            } else {
                return null;
            }
        }

        function ccbGetElementsByClassNameMult(className, element) {
            var dom = element || document
            if (dom.getElementsByClassName) {
                return dom.getElementsByClassName(className);
            } else {
                return null;
            }
        }

        function clearContent() {
            for (var key in arrContent) {
                arrContent[key] = "";
            }
        }

        function getGuid() {
            return (((1 + Math.random()) * 0x10000) | 0).toString(16).substring(1);
        }

        function getRandStr(length) {
            var reTemp = "";
            var data = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v", "b", "n", "m", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "A", "S", "D", "F", "G", "H", "J", "K", "L", "Z", "X", "C", "V", "B", "N", "M"];
            for (var i = 0; i < length; i++) {
                var r = Math.floor(Math.random() * 62);
                reTemp += data[r];
            }
            return reTemp;
        }

        function getccbcustomid() {
            if ("" == getccbCookie("ccbcustomid") || null == getccbCookie("ccbcustomid")) {
                var OutCookieID = "";
                var timesTamp = getCurrentDate().getTime();
                var rsLeft = getRandStr(20);
                var rsRight = getRandStr(20);
                var userAgnt = "";//navigator.userAgent||navigator.vendor||window.opera;
                OutCookieID = getGuid() + getGuid() + getGuid() + getGuid() + rsLeft + timesTamp + rsRight + getGuid() + getGuid() + getGuid() + getGuid() + getGuid() + getGuid() + getGuid() + getGuid() + userAgnt;
                OutCookieID = encodeURIComponent(OutCookieID);
                addccbCookie("ccbcustomid", OutCookieID, 36000, "/", ".ccb.com");
            }
        }

        getccbcustomid();


        var getLinks = document.getElementsByTagName("a");
        var getLinksLen = getLinks.length;
        addFunForA(getLinks, getLinksLen);

        /**if(typeof(AcqWebPageID)!='undefined'){*/
        function addFunForA(getLinks, getLinksLen) {
            for (var k = 0; k < getLinksLen; k++) {
                var isclick = getLinks[k].getAttribute("onclick");
                if (isclick != null && isclick != "") {
                    var browserversion = navigator.appVersion;
                    if (document.documentMode != 7 && isclick.indexOf("LinkClickFunction") === -1) {
                        getLinks[k].setAttribute("onclick", "javascript:LinkClickFunction(this);" + getLinks[k].getAttribute("onclick"));
                    }
                } else {
                    getLinks[k].setAttribute("onclick", "LinkClickFunction(this)");
                }
            }
        }

        /**}*/
        var getinputLinks = document.getElementsByTagName("input");
        var getinputLinksLen = getinputLinks.length;
        /**if(typeof(AcqWebPageID)!='undefined'){*/
        for (var k = 0; k < getinputLinksLen; k++) {
            if ("button" == getinputLinks[k].getAttribute("type") || "submit" == getinputLinks[k].getAttribute("type")) {
                var isclick = getinputLinks[k].getAttribute("onclick");
                if (isclick != null && isclick != "") {
                    var browserversion = navigator.appVersion;
                    if (document.documentMode != 7 && isclick.indexOf("LinkClickFunction") === -1) {
                        getinputLinks[k].setAttribute("onclick", "javascript:LinkClickFunction(this);" + getinputLinks[k].getAttribute("onclick"));
                    }
                } else {
                    getinputLinks[k].setAttribute("onclick", "LinkClickFunction(this)");
                }
            }
        }

        /**}*/


        function a_data(a) {
            var getherf = a.getAttribute("href");
            var gettitle = a.getAttribute("title");
            var gethtml = a.innerHTML.replace(/\s+/g, "");
            var getacqlinktitle = a.getAttribute("acqlinktitle");
            var getname = a.getAttribute("name");
            var getscqcolumnid = a.getAttribute("acqcolumnid");
            var getacqhyperlinkbtnid = a.getAttribute("acqhyperlinkbtnid");
            var getacqhyperlinkbtnname = a.getAttribute("acqhyperlinkbtnname");
            if (getacqhyperlinkbtnid != "" && getacqhyperlinkbtnid != null) {
                arrContent["button_id"] = getacqhyperlinkbtnid;
            }
            if (getacqhyperlinkbtnname != "" && getacqhyperlinkbtnname != null) {
                arrContent["button_name"] = getacqhyperlinkbtnname;
            }
            if (getname != "" && getname != null) {
                arrContent["anchor_name"] = getname;
            }
            if (getherf != null) {
                if (getherf.match("#")) {
                    arrContent["anchor_href"] = getherf;
                } else {
                    var targetatitle = "";
                    if (getacqlinktitle != "" && getacqlinktitle != null) {
                        targetatitle = getacqlinktitle;
                    } else {
                        if (gettitle != "" && gettitle != null) {
                            targetatitle = gettitle;
                        } else {
                            if (gethtml != "" && gethtml != null) {
                                targetatitle = gethtml;
                            }
                        }
                    }
                    if (targetatitle != "") {
                        arrContent["target_href_name"] = targetatitle + "," + getherf;
                    } else {
                        arrContent["target_href_name"] = getherf;
                    }
                }
            }
            var adTab = ccbGetElementsByClassName("AcqOldAd");
            if (adTab != null && adTab != "") {
                arrContent["ad_info"] = getherf;
            }
            var acqAdId = a.getAttribute("AcqAdId");
            if (acqAdId != null && acqAdId != "") {
                arrContent["ad_info"] = dataAcquisition_xy.dataAcqFn_xy["webadinfo"](acqAdId);

            }
        }

        function form_data(a) {
            var acqstep = a.getAttribute("acqstep");
            var getparentform = getparentsform(a);
            if (getparentform != null && getparentform != "") {
                arrContent["form_name"] = getparentform.getAttribute("name");
                arrContent["form_id"] = getparentform.getAttribute("acqformmodel");
            }
            if (acqstep != null && acqstep != "") {
                //var classstep=document.getElementsByClassName(acqstep)[0];
                var classstep = ccbGetElementsByClassName(acqstep);
                if (classstep != null && classstep != "") {

                    var txtBox = "";
                    var selectBox = "";
                    var singleBox = "";
                    var checkBox = "";
                    var classstepinput = classstep.getElementsByTagName("input");
                    var inputlen = classstepinput.length;
                    for (var k = 0; k < inputlen; k++) {
                        var acqinputkey = "";
                        var acqinputvalue = "";
                        //获取隐藏域指定的input或span标签的文本
                        if ("hidden" == classstepinput[k].getAttribute("type") && classstepinput[k].getAttribute("acqSpecified") != undefined) {
                            var acqSpecifiedId = classstepinput[k].getAttribute("acqSpecified");
                            if (acqSpecifiedId != "") {
                                var acqSpecifiedItem = document.getElementById(acqSpecifiedId);
                                acqinputkey = acqSpecifiedItem.getAttribute("acqinputkey");
                                if (null == acqinputkey || "" == acqinputkey) {
                                    acqinputkey = acqSpecifiedItem.getAttribute("id");
                                }
                                if (null == acqinputkey || "" == acqinputkey) {
                                    acqinputkey = acqSpecifiedItem.getAttribute("name");
                                }
                                if (acqSpecifiedItem.nodeName.toLowerCase() === "input") {
                                    acqinputvalue = acqSpecifiedItem.value;
                                } else if (acqSpecifiedItem.nodeName.toLowerCase() === "span") {
                                    acqinputvalue = acqSpecifiedItem.getAttribute("value");
                                }
                                if (txtBox == "") {
                                    txtBox += '{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                                } else {
                                    txtBox += ',{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                                }
                            }
                        }
                        //获取文本
                        else if ("text" == classstepinput[k].getAttribute("type") || null == classstepinput[k].getAttribute("type")) {
                            //txtInput[txtInput.length] += classstepinput[k];
                            acqinputkey = classstepinput[k].getAttribute("acqinputkey");
                            if (null == acqinputkey || "" == acqinputkey) {
                                acqinputkey = classstepinput[k].getAttribute("id");
                            }
                            if (null == acqinputkey || "" == acqinputkey) {
                                acqinputkey = classstepinput[k].getAttribute("name");
                            }
                            var acqinputvalue = classstepinput[k].value;
                            if (txtBox == "") {
                                txtBox += '{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                            } else {
                                txtBox += ',{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                            }

                        }
                        //获取单选框、复选框
                        else if ("radio" == classstepinput[k].getAttribute("type") && classstepinput[k].checked) {
                            acqinputkey = classstepinput[k].getAttribute("acqinputkey");
                            if (null == acqinputkey || "" == acqinputkey) {
                                acqinputkey = classstepinput[k].getAttribute("id");
                            }
                            if (null == acqinputkey || "" == acqinputkey) {
                                acqinputkey = classstepinput[k].getAttribute("name");
                            }
                            var acqinputvalue = classstepinput[k].value;
                            if (singleBox == "") {
                                singleBox += '{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                            } else {
                                singleBox += ',{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                            }
                        } else if ("checkbox" == classstepinput[k].getAttribute("type") && classstepinput[k].checked) {
                            acqinputkey = classstepinput[k].getAttribute("acqinputkey");
                            if (null == acqinputkey || "" == acqinputkey) {
                                acqinputkey = classstepinput[k].getAttribute("id");
                            }
                            if (null == acqinputkey || "" == acqinputkey) {
                                acqinputkey = classstepinput[k].getAttribute("name");
                            }
                            var acqinputvalue = classstepinput[k].value;
                            if (checkBox == "") {
                                checkBox += '{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                            } else {
                                checkBox += ',{"key":"' + acqinputkey + '","value":"' + acqinputvalue + '"}';
                            }
                        }

                    }
                    if (txtBox != "") {
                        txtBox = '"txtBox":[' + txtBox + ']';
                    }
                    arrContent["text_content"] = txtBox;

                    if (singleBox != "") {
                        singleBox = '"singleBox":[' + singleBox + ']';
                    }
                    if (singleBox == "" && checkBox != "") {
                        singleBox = '"singleBox":""';
                    }
                    if (checkBox != "") {
                        checkBox = '"checkBox":[' + checkBox + ']';
                    }
                    if (checkBox == "" && singleBox != "") {
                        checkBox = '"checkBox":""';
                    }
                    arrContent["check_box"] = '{' + singleBox + ',' + checkBox + '}';

                    if (singleBox == "" && checkBox == "") {
                        arrContent["check_box"] = "";
                    }

                    //获取下拉框
                    var classstepselect = classstep.getElementsByTagName("select");
                    var selectlen = classstepselect.length;
                    for (var k = 0; k < selectlen; k++) {
                        if (classstepselect[k]) {
                            var acqselectkey = classstepselect[k].getAttribute("acqinputkey");
                            if (null == acqselectkey || "" == acqselectkey) {
                                acqselectkey = classstepselect[k].getAttribute("id");
                            }
                            if (null == acqselectkey || "" == acqselectkey) {
                                acqselectkey = classstepselect[k].getAttribute("name");
                            }
                            var acqselectvalue = "";
                            var optlen = classstepselect[k].options.length;
                            for (var s = 0; s < optlen; s++) {
                                if (classstepselect[k][s].selected == true) {
                                    acqselectvalue = classstepselect[k].options[s].innerHTML;
                                }
                            }
                            if (selectBox == "") {
                                selectBox += '{"key":"' + acqselectkey + '","value":"' + acqselectvalue + '"}';
                            } else {
                                selectBox += ',{"key":"' + acqselectkey + '","value":"' + acqselectvalue + '"}';
                            }
                        }
                    }
                    if (selectBox != "") {
                        selectBox = '"selectBox":[' + selectBox + ']';
                    }
                    arrContent["combox_content"] = selectBox;

                    //按钮id
                    var getacqhyperlinkbtnid = a.getAttribute("acqhyperlinkbtnid");
                    arrContent["button_id"] = getacqhyperlinkbtnid;
                    //按钮name
                    var getacqhyperlinkbtnname = a.getAttribute("acqhyperlinkbtnname");
                    arrContent["button_name"] = getacqhyperlinkbtnname;

                }
            }
        }

        function sale_data(a) {
            var acqProductBTNId = a.getAttribute("acqproductbtnid");
            if ("" == acqProductBTNId || null == acqProductBTNId) {
                var acqProductId = a.getAttribute("id");
                if (acqProductId != "" && acqProductId != null) {
                    arrContent["button_id"] = acqProductId;
                }
            } else {
                arrContent["button_id"] = acqProductBTNId;
            }

            var acqProductBTNName = a.getAttribute("acqproductbtnname");
            if (acqProductBTNName != "" && acqProductBTNName != null) {
                arrContent["button_name"] = acqProductBTNName;
            }

            var acqProductItem = getProductItem(a);
            if (acqProductItem != "") {
                var acqProductIDTag = ccbGetElementsByClassName('AcqProductID', acqProductItem[0]);
                if (acqProductIDTag != undefined) {
                    arrContent["product_id"] = acqProductIDTag.innerHTML;
                }
                var acqProductNameTag = ccbGetElementsByClassName('AcqProductName', acqProductItem[0]);
                if (acqProductNameTag != undefined) {
                    arrContent["product_name"] = acqProductNameTag.innerHTML;
                }
            }
        }

        function senddata() {//发送采集数据
            var icount = 0;
            var alldata = "";
            for (var key in arrContent) {
                if (icount == 0) {
                    alldata = arrContent[key];
                } else if (/[\u4e00-\u9fa5]$/.test(arrContent[key])) {
                    alldata += "|@|" + arrContent[key] + " ";
                } else {
                    alldata += "|@|" + arrContent[key];
                }
                icount++;
            }
            var geturl = window.location.href;
            if (lock(geturl)) {
                var img = new Image();
                img.src = "http://dcaa.ccb.com/images/zxc.gif?parm=" + encodeURIComponent(alldata);
            }
        }

        function lock(msg) {
            //var url=new Array("http://www.ccb.com/cn/home/index.html","http://finance.ccb.com","http://m.ccb.com/cn/mobile/index.html","http://creditcard.ccb.com","http://group.ccb.com");
            var result = true;
            // for(var i=0;i<url.length;i++){
            // if(msg.match(url[i])){
            // result=false;
            // }
            // }
            var isreturn = false;
            if (result) {
                var ccbdatard = getccbCookie("ccbdatard");
                if ("" != ccbdatard && null != ccbdatard) {
                    if (ccbdatard == 1) {
                        isreturn = true;
                    }
                } else {
                    setccbdatard(100, 7 * 24);
                    ccbdatard = getccbCookie("ccbdatard");
                    if (ccbdatard == 1) {
                        isreturn = true;
                    }
                }

            }
            return isreturn;
        }

        function setccbdatard(probability, cookieMinute) {
            var randomnum = parseInt(Math.random() * 100 + 1);
            if (randomnum <= probability) {
                addccbCookie("ccbdatard", 1, cookieMinute, "/", ".ccb.com");
            } else {
                addccbCookie("ccbdatard", 0, cookieMinute, "/", ".ccb.com");
            }
        }

        function getparentsform(a) {//逐层向上搜索FORM元素或带有AcqFormModel属性的父元素
            var getparentform = "";
            while (true) {
                if (a.nodeName.toLowerCase() != "body") {
                    if (a.parentNode.nodeName == "FORM" || a.parentNode.getAttribute("AcqFormModel") != null) {
                        getparentform = a.parentNode;
                        break;
                    } else {
                        a = a.parentNode;
                    }
                } else {
                    break;
                }
            }
            return getparentform;
        }

        function getProductItem(a) {//逐层向上搜索带有AcqProductItem类的子元素
            var productItem = "";
            for (var i = 1; i <= 5; i++) {
                if (a.nodeName.toLowerCase() != "body") {
                    if (ccbGetElementsByClassName('AcqProductItem', a.parentNode) != undefined) {
                        productItem = ccbGetElementsByClassNameMult('AcqProductItem', a.parentNode);
                        break;
                    } else {
                        a = a.parentNode;
                    }
                } else {
                    break;
                }
            }
            return productItem;
        }


        function basedata() {
            arrContent["user_id"] = dataAcquisition_xy.dataAcqFn_xy["userid"]();
            arrContent["user_name"] = dataAcquisition_xy.dataAcqFn_xy["username"]();
            arrContent["session_id"] = dataAcquisition_xy.dataAcqFn_xy["sessionid"]();
            arrContent["page_type"] = "CONTENT";
            if (typeof (AcqWebPageID) != 'undefined') {
                arrContent["pageid"] = AcqWebPageID;
            }
            arrContent["page_title"] = document.title;
            arrContent["page_url"] = dataAcquisition_xy.dataAcqFn_xy["nowURL"]();
            arrContent["page_visit_time"] = dataAcquisition_xy.dataAcqFn_xy["nowTime"]();
            arrContent["source_url"] = dataAcquisition_xy.dataAcqFn_xy["referURL"]();
            arrContent["source_pagetitle"] = "";
            arrContent["source_pageid"] = "";
            arrContent["page_loading_time"] = dataAcquisition_xy.dataAcqFn_xy["loadtime"]();
            arrContent["html_loading_time"] = dataAcquisition_xy.dataAcqFn_xy["domtime"]();
            arrContent["dom_loading_time"] = dataAcquisition_xy.dataAcqFn_xy["domtime"]();
            arrContent["external_search_keyword"] = dataAcquisition_xy.dataAcqFn_xy["turnkeyword"]();
            arrContent["internal_search_keyword"] = dataAcquisition_xy.dataAcqFn_xy["searchKeyWord"]();
            arrContent["err_msg"] = errMsg;
            arrContent["ad_info"] = dataAcquisition_xy.dataAcqFn_xy["webadinfo"]("default");
            arrContent["err_code"] = "";
            arrContent["cookie_id"] = dataAcquisition_xy.dataAcqFn_xy["getCookie"]();
            arrContent["oper_type"] = "";
            arrContent["ip"] = "";
            arrContent["gps"] = "";
            arrContent["dev_type"] = dataAcquisition_xy.dataAcqFn_xy["browseruseragent"]();
            arrContent["browse_type_version"] = dataAcquisition_xy.dataAcqFn_xy["browserInfo"]() + "_" + dataAcquisition_xy.dataAcqFn_xy["browserversion"]();
            arrContent["os_type_version"] = dataAcquisition_xy.dataAcqFn_xy["systemversion"]();
            arrContent["screen_resolution"] = dataAcquisition_xy.dataAcqFn_xy["getscreen"]();
            arrContent["color"] = dataAcquisition_xy.dataAcqFn_xy["colordepth"]();
            arrContent["flash_version"] = dataAcquisition_xy.dataAcqFn_xy["flash_version"]();
            arrContent["javascript_version"] = dataAcquisition_xy.dataAcqFn_xy["javascript_version"]();
            arrContent["java_support"] = dataAcquisition_xy.dataAcqFn_xy["isjava"]();
            arrContent["cookie_support"] = dataAcquisition_xy.dataAcqFn_xy["iscookie"]();
            arrContent["client_plugin"] = dataAcquisition_xy.dataAcqFn_xy["brpluginsname"]();
            arrContent["client_lang"] = dataAcquisition_xy.dataAcqFn_xy["currentlang"]();
            arrContent["client_zone"] = dataAcquisition_xy.dataAcqFn_xy["client_zone"]();
            arrContent["mechine_type"] = "";
            arrContent["app_version"] = "";
            arrContent["app_source"] = "";
            arrContent["net_type"] = "";
            arrContent["ukey_type"] = "";
            arrContent["certificate_en"] = "";
            arrContent["ori_session_id"] = dataAcquisition_xy.dataAcqFn_xy["getQueryString"]("ORI_SESSION_ID");
        }


        function dcaaismobile(a) {
            try {
                if (/android/i.test(a)) {
                    return "android";
                } else if (/ip(hone|od)/i.test(a)) {
                    return "iphone/ipad";
                } else if (/windows (ce|phone)/i.test(a)) {
                    return "windows phone7";
                } else {
                    return "pc";
                }
            } catch (e) {

            }
        }

        function setAdrecord(adValue) {
            onloadtime = (getCurrentDate()).getTime();
            basedata();
            senddata();
        }


        window.onerror = function (info, url, line) {
            errMsg = info;
        }

        function dataAcquisition_xy(options) {
            return this.returnVal;
        };

        dataAcquisition_xy.dataAcqFn_xy = {
            webadinfo: function (ad) {
                var adidTmp = "";
                if ("default" == ad && webinfo_first == true || typeof ad === "object") {
                    webinfo_first = false;
                    //var adDivclass = ccbGetElementsByClassNameMult("AcqAdContainer");
                    var adDivclass = document;
                    if (typeof (adDivclass) != 'undefined' && adDivclass != null) {
                        var links;
                        if (typeof ad === "object") {
                            links = ad;
                        } else {
                            links = adDivclass.getElementsByTagName("a");
                        }
                        for (var i = 0; i < links.length; i++) {
                            var tmp = links[i].getAttribute("acqadid");
                            if (tmp != "" && tmp != null) {
                                adidTmp += "{\"value\":\"" + links[i].getAttribute("acqadid") + "\"},";
                            }
                        }
                        if (adidTmp != "" && adidTmp != null) {
                            adidTmp = adidTmp.substring(0, adidTmp.length - 1);
                        }
                        adidTmp = "{\"adInfo\":[" + adidTmp + "]}";
                    }
                } else if (ad != "" && ad != null && ad != "default") {
                    adidTmp += "{\"adInfo\":[{\"value\":\"" + ad + "\"}]}";
                } else {
                    adidTmp = "";
                }
                return adidTmp;
            },
            userid: function () {
                var cid = "cs_cid";
                var userid = "";
                var cookie = ";" + document.cookie.replace(/;\s+/g, ";") + ";"
                var pos = cookie.indexOf(";" + cid + "=");
                if (pos > -1) {
                    var start = cookie.indexOf("=", pos);
                    var end = cookie.indexOf(";", start);
                    userid = unescape(cookie.substring(start + 1, end));
                }
                return userid;
            },
            username: function () {
                var name = "custName";
                var username = "";
                var cookie = ";" + document.cookie.replace(/;\s+/g, ";") + ";"
                var pos = cookie.indexOf(";" + name + "=");
                if (pos > -1) {
                    var start = cookie.indexOf("=", pos);
                    var end = cookie.indexOf(";", start);
                    username = unescape(cookie.substring(start + 1, end));
                }
                return username;
            },
            sessionid: function () {
                var getcookie = getRandStr(15);
                getcookie += getGuid() + getGuid() + getGuid();
                var getsession = "";
                var getsessionCookie = getccbCookie("ccbsessionid");
                var date = getCurrentDate()
                var getnowdatetime = date.getFullYear() + "" + ((date.getMonth() + 1) < 10 ? "0" + (date.getMonth() + 1) : (date.getMonth() + 1)) + (date.getDate() < 10 ? "0" + date.getDate() : date.getDate()) + (date.getHours() < 10 ? "0" + date.getHours() : date.getHours()) + (date.getMinutes() < 10 ? "0" + date.getMinutes() : date.getMinutes()) + (date.getSeconds() < 10 ? "0" + date.getSeconds() : date.getSeconds());
                if ("" == getsessionCookie || null == getsessionCookie) {
                    getsession = getcookie + "-" + getnowdatetime;
                    addccbCookie("ccbsessionid", getsession, 0, "/", ".ccb.com");
                } else {
                    if (getnowdatetime - getsessionCookie.split("-")[1] < 1000000) {
                        getsession = getsessionCookie;
                    } else {
                        getsession = getcookie + "-" + getnowdatetime;
                        addccbCookie("ccbsessionid", getsession, 0, "/", ".ccb.com");
                    }
                }
                return getsession;
            },
            nowTime: function () {
                return (getCurrentDate()).getTime();
            },
            nowURL: function () {
                return document.location.href;
            },	//注：在IE浏览器中,如果页面是通过location.href跳转过来的,那么使用document.referrer是无法获取到referrer 。
            referURL: function () {
                var referrer = document.referrer;
                if (!referrer) {
                    try {
                        if (window.opener) {
                            // IE下如果跨域则抛出权限异,Safari和Chrome下window.opener.location没有任何属性。
                            referrer = window.opener.location.href;
                        }
                    } catch (e) {
                    }
                }
                return referrer;
            },
            userLogo: function () {
                return "";
            },
            searchKeyWord: function () {
                return "";
            },
            browserInfo: function () {
                var brtype = "";
                if (navigator.userAgent) {
                    if (navigator.userAgent.indexOf("MSIE") > 0) {
                        brtype = "MSIE";
                    } else if (navigator.userAgent.indexOf("Firefox") > 0) {
                        brtype = "Firefox";
                    } else if (navigator.userAgent.indexOf("Chrome") > 0) {
                        brtype = "Chrome";
                    } else if (navigator.userAgent.indexOf("Safari") > 0 && navigator.userAgent.indexOf("Chrome") <= 0) {
                        brtype = "Safari";
                    } else if (navigator.userAgent.indexOf("Camino") > 0) {
                        brtype = "Camino";
                    } else if (navigator.userAgent.indexOf("Gecko/") > 0) {
                        brtype = "Gecko";
                    } else {
                        brtype = navigator.userAgent;
                    }
                }
                return brtype;
            },
            browserversion: function () {
                return navigator.appVersion;
            },
            brpluginsname: function () {
                var brpluginslength = "";
                var plugins = navigator.plugins;
                brpluginslength = plugins.length;
                var brpluginsname = "";
                if (plugins.length > 0) {
                    for (i = 0; i < navigator.plugins.length; i++) {
                        brpluginsname += navigator.plugins[i].name + ";";
                    }
                }
                return brpluginsname;
            },
            currentlang: function () {
                var browercurrentLang = navigator.language;   //判断除IE外其他浏览器使用语言
                if (!browercurrentLang) {//判断IE浏览器使用语言
                    browercurrentLang = navigator.browserLanguage;
                }
                return browercurrentLang;
            },
            client_zone: function () {
                return (getCurrentDate().getTimezoneOffset() / 60).toString();
            },
            systemversion: function () {
                var getsystemversion = navigator.platform;
                return getsystemversion;
            },
            getscreen: function () {
                var setscreen = window.screen.width + "," + window.screen.height
                return setscreen;
            },
            colordepth: function () {
                var getcolordepth = window.screen.colorDepth + decodeURIComponent("%E4%BD%8D") + " ";
                //var getcolordepth=window.screen.colorDepth;
                return getcolordepth;
            },
            browseruseragent: function () {
                var getbrowseruseragent = dcaaismobile(navigator.userAgent || navigator.vendor || window.opera);
                return getbrowseruseragent;
            },
            ipaddress: function () {
                return "";
            },
            browsererror: function () {
                return "";
            },
            getCookie: function () {
                var getcookie = getccbCookie("ccbcustomid");
                if ("" == getcookie || null == getcookie) {
                    getccbcustomid();
                    getcookie = getccbCookie("ccbcustomid");
                }
                return getcookie;
            },
            SetCookie: function () {
                var Days = 30;
                var exp = getCurrentDate();
                exp.setTime(exp.getTime() + Days * 24 * 60 * 60 * 1000);
                var name = "ccbcustomid";
                var value = "";
                var cookie = ";" + document.cookie.replace(/;\s+/g, ";") + ";"
                var pos = cookie.indexOf(";" + name + "=");
                if (pos > -1) {
                    var start = cookie.indexOf("=", pos);
                    var end = cookie.indexOf(";", start);
                    value = unescape(cookie.substring(start + 1, end));
                }
                if ("" == value) {
                    value = "ipaddress" + (getCurrentDate()).getTime();
                    document.cookie = name + "=" + escape(value) + ";expires=" + exp.toGMTString();
                }

            },
            delCookie: function (name) {
                var exp = getCurrentDate();
                exp.setTime(exp.getTime() - 1);
                var cval = getCookie(name);
                if (cval != null) document.cookie = name + "=" + cval + ";expires=" + exp.toGMTString();
            },
            loadtime: function () {
                var getloadtime = onloadtime - headergettime;
                if (getloadtime < 0) {
                    getloadtime = 0;
                }
                return getloadtime;
            },
            domtime: function () {
                var getdomtome = domtime - headergettime;
                if (getdomtome < 0) {
                    getdomtome = 0;
                }
                return getdomtome;
            },
            turnkeyword: function () {
                var getword = "";
                var getreferrer = document.referrer.toString();
                var p = getreferrer.indexOf('?');
                if (getreferrer.match('baidu.com')) {
                    var params = getreferrer.substr(p + 1).split('&');
                    for (var i = 0, l = params.length; i < l; i++) {
                        if (params[i].indexOf("wd=") + 1) {
                            getword = decodeURIComponent(params[i].split("=")[1]);
                        }
                    }
                } else if (getreferrer.match('google.com') || getreferrer.match('so.com')) {
                    var params = getreferrer.substr(p + 1).split('&');
                    for (var i = 0, l = params.length; i < l; i++) {
                        if (params[i].indexOf("q=") + 1) {
                            getword = decodeURIComponent(params[i].split("=")[1]);
                        }
                    }
                } else if (getreferrer.match('sogou.com')) {
                    var params = getreferrer.substr(p + 1).split('&');
                    for (var i = 0, l = params.length; i < l; i++) {
                        if (params[i].indexOf("query=") + 1) {
                            getword = decodeURIComponent(params[i].split("=")[1]);
                        }
                    }
                } else if (getreferrer.match('soso.com')) {
                    var params = getreferrer.substr(p + 1).split('&');
                    for (var i = 0, l = params.length; i < l; i++) {
                        if (params[i].indexOf("w=") + 1) {
                            getword = decodeURIComponent(params[i].split("=")[1]);
                        }
                    }
                } else if (getreferrer.match('so.com')) {
                    var params = getreferrer.substr(p + 1).split('&');
                    for (var i = 0, l = params.length; i < l; i++) {
                        if (params[i].indexOf("q=") + 1) {
                            getword = decodeURIComponent(params[i].split("=")[1]);
                        }
                    }
                } else if (getreferrer.match('yahoo.com')) {
                    var params = getreferrer.substr(p + 1).split('&');
                    for (var i = 0, l = params.length; i < l; i++) {
                        if (params[i].indexOf("p=") + 1) {
                            getword = decodeURIComponent(params[i].split("=")[1]);
                        }
                    }
                }
                return getword;
            },
            isflash: function () {
                var i_flash = false;
                for (i = 0; i < navigator.plugins.length; i++) {
                    if (navigator.plugins[i].name.toLowerCase().indexOf("shockwave flash") >= 0) {
                        i_flash = true;
                    }
                }
                return i_flash;
            },
            flash_version: function () {
                var v_flash = "";
                for (i = 0; i < navigator.plugins.length && v_flash == ""; i++) {
                    if (navigator.plugins[i].name.toLowerCase().indexOf("shockwave flash") >= 0) {
                        v_flash += " " + navigator.plugins[i].description.substring(navigator.plugins[i].description.toLowerCase().lastIndexOf("flash") + 6, navigator.plugins[i].description.length);
                    }
                }
                return v_flash;
            },
            javascript_version: function () {
                var v = navigator.appVersion;
                var ie = v.indexOf("MSIE");
                if (ie > 0) {
                    apv = parseInt(i = v.substring(ie + 5));
                    if (apv > 3) {
                        parseFloat(ie);
                    }
                } else {
                    apv = parseFloat(v);
                }
                var isie = (navigator.appName == "Microsoft Internet Explorer");
                var ismac = (navigator.userAgent ? navigator.userAgent.indexOf("Mac") > 0 : false);
                var jsVersion = "1.0";
                if (String && String.prototype) {
                    jsVersion = "1.1";
                    if (jsVersion.match) {
                        jsVersion = "1.2";
                        var tm = getCurrentDate();
                        if (tm.setUTCDate) {
                            jsVersion = "1.3";
                            if (isie && ismac && apv >= 5) jsVersion = "1.4";
                            var pn = 0;
                            if (pn.toPrecision) {
                                jsVersion = "1.5";
                                a = new Array();
                                if (a.forEach) {
                                    jsVersion = "1.6";
                                    i = 0;
                                    o = new Object();
                                    tcf = new Function('o', 'var e,i=0;try{i = new Iterator(o)}catch(e){} return i');
                                    i = tcf(o);
                                    if (i && i.next) {
                                        jsVersion = "1.7";
                                    }
                                }
                            }
                        }
                    }
                }
                return jsVersion;
            },
            iscookie: function () {
                return navigator.cookieEnabled;
            },
            isjava: function () {
                return navigator.javaEnabled();
            },
            getQueryString: function (name) {
                var reg = new RegExp("(^|&)" + name + "=([^&]*)(&|$)", "i");
                var r = window.location.search.substr(1).match(reg);
                if (r != null) {
                    var t = unescape(r[2]);
                    addccbCookie("ORI_SESSION_ID", t, 0, "/", ".ccb.com");
                    return unescape(r[2]);
                } else {
                    var n = getccbCookie("ORI_SESSION_ID")
                    if (n != null) {
                        return n;
                    }
                    return "";
                }
            }
        }

        function adMouseover_data(e) {
            e = e || window.event;
            var target = e.target || e.srcElement;
            //var adContainId=target.getAttribute("adContainer"); //取带标识元素
            //if(adContainId){
            setTimeout(function () {
                //var adContain=document.getElementById(adContainId); //取带标识元素
                var adContain = target.nextSibling; //固定取主页导航栏
                if (adContain.className != "mnavL") {
                    adContain = adContain.nextSibling;
                }
                var links = adContain.getElementsByTagName("a");
                clearContent();
                arrContent["is_page_view"] = "2";
                addFunForA(links, links.length);
                basedata();
                arrContent["ad_info"] = dataAcquisition_xy.dataAcqFn_xy["webadinfo"](links);
                senddata();
            }, 200);
            //}
            if (window.removeEventListener) {
                target.removeEventListener("mouseover", adMouseover_data);
            } else {
                target.detachEvent("onmouseover", adMouseover_data);
            }
            return false;
        }

        //var adMouseoverclass=ccbGetElementsByClassNameMult("AcqMouseOver"); //取带标识元素
        try {
            var adMouseoverItems = ccbGetElementsByClassName('nav').childNodes[0].childNodes;  //固定取主页导航栏
            var adMouseoverclass = (function () {
                if (adMouseoverItems) {
                    var items = [];
                    for (var i = 0; i < adMouseoverItems.length; i++) {
                        items.push(adMouseoverItems[i].firstChild);
                    }
                    return items;
                }
            })();
            var adMouseoverSize = adMouseoverclass && adMouseoverclass.length;
            if (window.addEventListener && adMouseoverSize > 0) {
                for (var i = 0; i < adMouseoverSize; i++) {
                    adMouseoverclass[i].addEventListener("mouseover", adMouseover_data);
                }
            } else if (window.addtachEvent && adMouseoverSize > 0) {
                for (var i = 0; i < adMouseoverSize; i++) {
                    adMouseoverclass[i].addtachEvent("mouseover", adMouseover_data);
                }
            }
        } catch (e) {
        }
        domtime = (getCurrentDate()).getTime();
        setAdrecord("");
        // window.onload=function(){
        // setAdrecord("");
        // }
        window.LinkClickFunction = function (a) {
            clearContent();
            arrContent["is_page_view"] = "0";
            basedata();
            var getclass = a.getAttribute("class");
            // 0:信息发布页面,1:表单提交页面,2:产品购买页面
            var getanalyse = 0;
            if (getclass) {
                if (getclass.indexOf("AcqStepClick") >= 0) {
                    getanalyse = 1;
                }
                if (getclass.indexOf("AcqProductClick") >= 0) {
                    getanalyse = 2;
                }
            }
            //CONTENT:内容类 APPLICATION:申请类 PRODUCTION:产品类 MARKET:营销类 TOOL:工具类
            if (getanalyse == 1) {
                //arrContent["page_type"]="APPLICATION";
                form_data(a);
            } else if (getanalyse == 2) {
                //arrContent["page_type"]="PRODUCTION";
                sale_data(a);
            } else {
                //arrContent["page_type"]="CONTENT";//getanalyse==0
                a_data(a);
            }
            senddata();
        }
        window.datacollect = {
            sendCardData: function (data) {
                var dataString = JSON.stringify(Object.keys(data).map(function (key) {
                        return {key: key, value: data[key]}
                    })),
                    txtBox = '"txtBox":' + dataString;
                clearContent();
                arrContent["is_page_view"] = "0";
                basedata();
                arrContent["text_content"] = txtBox
                senddata();
            }
        }
    }
})()