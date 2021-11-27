/**
 * 页面加载完毕
 * 发送countBrand.gsp请求,获取所有类别 03 乾元 01 利得盈 02 建行财富 04 汇得盈 05 其他
 * 成功后发送queryFinanceProdList.gsp请求,默认拿03型数据
 */
$(function () {
    $.ajax({
        type: "get",
        url: "http://finance.ccb.com/cc_webtran/countBrand.gsp",
        success: function (data) {
            var tabcontent = "";
            var listcontent = "";
            var list = eval(data)[0].split(',');
            var newdata = "";
            for (var i = 0; i < list.length; i++) {
                if (list[i] == "03") {
                    listcontent = "乾元";
                    tabcontent += '<a class="tab5" dbvalue="' + list[i] + '" >' + listcontent + '</a>';
                } else {
                    newdata += list[i] + ',';
                }
            }

            list = newdata.substr(0, newdata.length - 1).split(',');

            for (var i = 0; i < list.length; i++) {
                if (list[i] == "01") {
                    listcontent = "利得盈";
                } else if (list[i] == "02") {
                    listcontent = "建行财富";
                } else if (list[i] == "03") {
                    listcontent = "乾元";
                } else if (list[i] == "04") {
                    listcontent = "汇得盈";
                } else if (list[i] == "05") {
                    listcontent = "其他";
                }
                tabcontent += '<a class="tab5" dbvalue="' + list[i] + '" >' + listcontent + '</a>';
            }
            ;
            $('.life_tab').prepend(tabcontent);
            $(".tab5:eq(0)").addClass("life_tab_hover");
            $("#selProductName").html($(".life_tab_hover").html());
            var pisition = {乾元: 0, 利得盈: 1, 建行财富: 2, 汇得盈: 3, 其他: 4};
            var pisit = pisition[$(".tab5:eq(0)").text()];
            $(".insurance_tab_detail").hide();
            $(".insurance_tab_detail").eq(pisit).show();
            addlist($('.life_tab_hover').attr('dbvalue'), 1, -1);
            $('.tab5').click(function () {
                datavalue["orderBys"] = undefined;
                datavalue['ascOrDescs'] = undefined;
                addlist($(this).attr('dbvalue'), 1);
                var pisition = {"乾元": 0, "利得盈": 1, "建行财富": 2, "汇得盈": 3, "其他": 4};
                var id = pisition[$(this).text()];
                $(".tab5").removeClass("life_tab_hover");
                $(this).addClass("life_tab_hover");
                $(".insurance_tab_detail").hide();
                $(".insurance_tab_detail").eq(id).show();
                $("#selProductName").html($(this).text());
            })
        }
    });

    //条件选择栏
    $('.tiaojian-select-text').click(function () {
        $('#saleCitys li a').css('color', '#333');
        $('#saleCitys li a').each(function () {
            if ($(this).text() == $('.sc_lei li:eq(0) a').text()) {
                $(this).css('color', '#0066b3');
            }
        })//$('.dingwei #provinceName').text()
    })

})

var name;
var datavalue = {};
datavalue["queryForm.isNetvalPro"] = 1; //默认非净值型
var brand = '03';
var pageNo = 1; 	//页码
var pageSize = 12;  //每页展示数据量
var maxPage = 0;   //最大分页数
var viewType = 1; //展示类型
//var initSaleStatus = -1; //初始化销售状态 -1 在售

/*
 * 分页控制
*/
function pageSizeCount(total, loadMethod) {
    $("#page").val("");
    pageNo = parseInt(pageNo);
    if (total <= pageSize) {
        for (var s = 1; total === 0 && s <= 5; s++) {
            $("#tab" + s).html("");
            $("#list" + s).html("");
        }
        $("#pageDiv").css("display", "none");
        return;
    }

    var maxBlock = 7;
    var maxPage = Math.ceil(total / pageSize);
    pageNo = pageNo > maxPage ? maxPage : pageNo;
    $("#pageNum").html(pageNo + "/" + maxPage);
    $("#total").html(total);
    $("#pageDiv").show();
    pageNo > 1 ? ($("#up_span").html('<a id="up" style="cursor:pointer;background:#0066b3" onclick="' + loadMethod + '(null,\'' + (pageNo - 1) + '\')" class="page_btn">上一页</a>'), $("#up_span").show(), maxBlock--) : ($("#up_span").hide());
    pageNo < maxPage ? ($("#next_span").html('<a id="next" style="cursor:pointer;background:#0066b3" onclick="' + loadMethod + '(null,\'' + (pageNo + 1) + '\')" class="page_btn">下一页</a>'), $("#next_span").show(), maxBlock--) : ($("#next_span").hide());
    var pageStart = pageNo < maxBlock ? 1 : pageNo > (maxPage - maxBlock) ? (maxPage - maxBlock + 1) : (pageNo - Math.floor(maxBlock / 2)),
        spanHtml = "";
    for (; maxBlock-- && pageStart <= maxPage;) {
        var hover = (pageStart === pageNo) ? 'class="hover"' : '';
        spanHtml += '<span style="margin:0 2px;"><a ' + hover + '  id="pageNo' + pageStart + '" onclick="addlist(null,' + pageStart + ')">&nbsp;' + pageStart + '&nbsp;</a></span>';
        pageStart++;
    }
    $("#pageNoSpan").html(spanHtml);
    $("#page").keyup(function () { //兼容IE7 输入框 键盘输入事件
        keyMaxNum(this, maxPage);
    });
    $("#page").click(function () { //兼容IE7
        keyMaxNum(this, maxPage);
    });
    $("#go").click(function () { //兼容IE7
        goLoad("#page", maxPage);
    });
}

/*是否数字判断*/
function isDigit(object, maxNum) {
    var s = $(object).val();
    var reg = new RegExp("^[0-9]+$");
    if (s != "") {
        s = $.trim(s);
        if (!s.match(reg)) {
            return false;
        }
        return true;
    }
    return true;
}

/* 控制输入的页码 */
function keyMaxNum(obj, maxPage) {
    var s = $(obj).val();
    if (!isDigit(obj) || s <= 0) {
        $(obj).val("");
    }
    if (s > maxPage) {
        $(obj).val("");
    }
}

/* 转到指定页数 */
function goLoad(obj, maxPage) {
    var s = $(obj).val();
    if (s > 0 && s <= maxPage) {
        var pageNo = s;
        addlist(null, pageNo);
    }
}

//获取数据
/**
 *
 * @param brandParam  查询哪一类型数据 03 乾元 01 利得盈 02 建行财富 04 汇得盈 05 其他
 * @param pageNoParam 页数
 * @param saleStatus 销售状态 -1 在售 03 可预约 04 待售 05 已售完
 */

function addlist(brandParam, pageNoParam, saleStatus) {
    if (viewType == 1) {
        $(".no1").click();
    } else if (viewType == 2) {
        $(".no2").click();
    }
    if (brandParam != null && brandParam != "") {
        brand = brandParam;
    }
    if (pageNoParam != null && pageNoParam != "") {
        pageNo = pageNoParam;
    } else {
        pageNo = 1;
    }
    if (saleStatus != null && saleStatus != "") {
        datavalue["queryForm.saleStatus"] = saleStatus;	//销售状态
    }
    var isNetvalPro = datavalue["queryForm.isNetvalPro"];
    var orderBys = datavalue['orderBys'];
    var ascOrDescs = datavalue['ascOrDescs'];
    if (isNetvalPro == 0) {
        $(".mo_rank_lei").each(function () {
            var last_a = $(this).find("a:last");
            $(last_a).find("span").html("业绩比较基准");
            $(last_a).attr("onclick", "javascript:orderByClick(this,'yield_rate')");
            if (orderBys == "yield_rate") {
                if (ascOrDescs == "desc") {
                    $(last_a).attr("state", "2");
                } else {
                    $(last_a).attr("state", "1");
                }
            } else {
                $(last_a).find("span").attr("class", "");
                $(last_a).find("s").attr("class", "");
            }
        })
    } else if (isNetvalPro == 1) {
        $(".mo_rank_lei").each(function () {
            var last_a = $(this).find("a:last");
            $(last_a).find("span").html("七日年化收益率");
            $(last_a).attr("onclick", "javascript:orderByClick(this,'yield_rate')");
            if (orderBys == "yield_rate") {
                if (ascOrDescs == "desc") {
                    $(last_a).attr("state", "2");
                } else {
                    $(last_a).attr("state", "1");
                }
            } else {
                $(last_a).find("span").attr("class", "");
                $(last_a).find("s").attr("class", "");
            }
        })
    }

    //默认查询参数
    datavalue['queryForm.brand'] = brand; //数据类型
    //datavalue["queryForm.saleStatus"] = initSaleStatus; //销售状态
    datavalue['pageNo'] = pageNo; //页码
    datavalue['pageSize'] = pageSize; //每页展示数量

    //搜索框
    var productName = $.trim($("#productName").val());
    if (productName != null && productName != '' && productName != '#none') {
        if (productName != "请输入产品名称/编号") {
            productName = encodeURI(productName);
            datavalue['queryForm.name'] = productName;
            datavalue['queryForm.code'] = productName;
        } else {
            datavalue['queryForm.name'] = undefined;
            datavalue['queryForm.code'] = undefined;
        }
    } else {
        datavalue['queryForm.name'] = undefined;
        datavalue['queryForm.code'] = undefined;
    }

    $.ajax({
        type: "post",
        cache: false,
        url: "/cc_webtran/queryFinanceProdList.gsp?jsoncallback=?",
        data: datavalue,
        dataType: "jsonp",
        success: function (data) {
            var list = data;
            var valelist = list.ProdList;
            $(".dingwei a").text(list.totalCount);
            pageSizeCount(list.totalCount, "addlist");
            //$("#selProductName").html($(".life_tab_hover").html());
            if (valelist != null && valelist != "" && valelist.length > 0) {
                var pbrand = valelist[0].brand;
                var tab, list;
                if (pbrand == "01") {
                    tab = "tab2";
                    list = "list2";
                    //$("#selProductName").html("利得盈");
                } else if (pbrand == "02") {
                    tab = "tab3";
                    list = "list3";
                    //$("#selProductName").html("建行财富");
                } else if (pbrand == "03") {
                    tab = "tab1";
                    list = "list1";
                    //$("#selProductName").html("乾元");
                } else if (pbrand == "04") {
                    tab = "tab4";
                    list = "list4";
                    //$("#selProductName").html("汇得盈");
                } else if (pbrand == "05") {
                    tab = "tab5";
                    list = "list5";
                    //$("#selProductName").html("其它");
                }
                formatable(list, valelist, datavalue["queryForm.isNetvalPro"]);
                formatData(tab, valelist, datavalue["queryForm.isNetvalPro"]);
            } else {
                var tab, list, str;
                if (brand == "01") {
                    tab = "tab2";
                    list = "list2";
                    str = "利得盈";
                } else if (brand == "02") {
                    tab = "tab3";
                    list = "list3";
                    str = "建行财富";
                } else if (brand == "03") {
                    tab = "tab1";
                    list = "list1";
                    str = "乾元";
                } else if (brand == "04") {
                    tab = "tab4";
                    list = "list4";
                    str = "汇得盈";
                } else if (brand == "05") {
                    tab = "tab5";
                    list = "list5";
                    str = "其它";
                }
                var html = '<div  style="color:#666;font-size:14px;margin-left:28px;" >';
                html += "很抱歉，没有找到您需要的" + str + "类产品。建议您重新选择筛选条件或产品类别。</div>";
                $("#" + tab).html(html);
                $("#" + list).html(html);
            }
        }
    });
}

//列表模式
function formatable(id, data, isNetvalPro) {
    var html = '<table width="100%" border="0" cellspacing="0" cellpadding="0">';
    html += '<colgroup><col width="45%" /><col width="11%" /><col width="11%" />';
    html += '<col width="11%" /><col width="11%" /></colgroup><tr>';
    html += '<th scope="col">基本信息</th><th scope="col">起购金额</th>';
    html += '<th scope="col">投资期限</th><th scope="col">发行日期</th>';
    if (isNetvalPro == 0) {
        //非净值型
        html += '<th scope="col">业绩比较<br/>基准</th>';
    } else if (isNetvalPro == 1) {
        //净值型
        html += '<th scope="col">七日年化<br/>收益率</th>';
    }
    html += '<th scope="col">操作</th></tr>';

    for (var i = 0; i < data.length; i++) {
        var saleStatus = data[i].saleStatus;     //销售状态 "01:申购 02:认购 03:可预约 04:预售 05:已售完"
        var purFloorAmt_is = datavalue['queryForm.purFloorAmt_is'];
        if (purFloorAmt_is == 1 &&
            (data[i].purFloorAmt == 50000 || data[i].purFloorAmt == 100000 || data[i].purFloorAmt == 500000)) { //起购金额选择“其他”时，过滤掉起购金额=5万 10万 50万的产品

        } else {
            html += siftTableDate(id, data[i]);
        }
    }

    html += '</table>';
    $("#" + id).html(html);
}

function siftTableDate(id, dataTr) {
    var html = "";
    var dcrindex = dataTr.dcrIndex;
    var pdId = dataTr.code;	             //产品编号
    var name = dataTr.name;
    html += '<tr><td class="list_title" style="line-height:28px;">';
    var channelSig = $.trim(dataTr.channel_sig);
    if (name == null || name == "") {
        html += '<a href=""></a>';
    } else {
        var tit = name;
        if (name != null && name.length > 18) {
            name = name.substring(0, 18) + "...";
        } else if (name.length > 25) {
            name = name.substring(0, 24) + "...";
        }
        html += '<div class="AcqProductList"><div class="AcqProductItem"><div class="AcqProductID" style="display:none">' + pdId + '</div><a class="AcqProductName AcqProductClick" onclick="LinkClickFunction(this)" target="_blank" title="' + tit + '" href="./ProductDetails.html?PRODUCT_ID=' + pdId + '">' + name;
        if (channelSig != null && channelSig != " " && channelSig.length > 0) {
            html += '<span class="zu">' + channelSig + '</span>';
        }
        html += '</a></h2>';
    }
    var proMode = "不可赎回";
    if (dataTr.proMode == "1" && pdId != "ZH070416012123D41") {
        proMode = "可赎回";
    }
    var yieldSpec = "非保本";
    if (dataTr.yieldSpec == "1") {
        yieldSpec = "保本";
    }
    var riskLevel = "无风险";
    if (dataTr.riskLevel == "02") {
        riskLevel = "较低风险";
    } else if (dataTr.riskLevel == "03") {
        riskLevel = "中等风险";
    } else if (dataTr.riskLevel == "04") {
        riskLevel = "较高风险";
    } else if (dataTr.riskLevel == "05") {
        riskLevel = "高风险";
    }
    var moneyType = "外币";
    var currencyType = dataTr.currencyType;
    if (currencyType == "01") {
        moneyType = "人民币";
    } else if (currencyType == "12") {
        moneyType = "英镑";
    } else if (currencyType == "13") {
        moneyType = "港币";
    } else if (currencyType == "14") {
        moneyType = "美元";
    } else if (currencyType == "15") {
        moneyType = "瑞士法郎";
    } else if (currencyType == "27") {
        moneyType = "日元";
    } else if (currencyType == "28") {
        moneyType = "加元";
    } else if (currencyType == "29") {
        moneyType = "澳元";
    } else if (currencyType == "33") {
        moneyType = "欧元";
    }
    var allOrgFlag = dataTr.allOrgFlag;
    var provinceId = dataTr.provinceId;
    var isSaleAll = "全国"; //销售区域
    if (allOrgFlag == "0") {
        isSaleAll = "";
        if (provinceId != null && provinceId != "") {
            var saleArray = provinceId.split(",");
            var s = saleArray.length;
            if (saleArray.length >= 2) {
                s = 2;
            }
            for (var j = 0; j <= s; j++) {
                for (var i = 0; i < citsy.length; i++) {
                    if (saleArray[j] == citsy[i].code) {
                        isSaleAll += citsy[i].name + " ";
                    }
                }
                if (j == s) {
                    if (saleArray.length > 2) {
                        isSaleAll += "等" + saleArray.length + "家分行";
                    }
                }
            }
        }
    }
    html += '<p><span>' + proMode + '</span>';
    html += '<span>' + yieldSpec + '</span>';
    html += '<span>' + riskLevel + '</span>';
    html += '<span>' + moneyType + '</span>';
    html += '<span>' + isSaleAll + '</span></p></td>';
    var purFloorAmt = dataTr.purFloorAmt;
    if (purFloorAmt != "null" && purFloorAmt > 0) {
        purFloorAmt = parseFloat(purFloorAmt) / 10000;
        if (currencyType != 1) {
            html += '<td>' + dataTr.purFloorAmt + '</td>';
        } else {
            if (dataTr.purFloorAmt < 10000) {
                html += '<td>' + dataTr.purFloorAmt + '</td>';
            } else {
                html += '<td>' + purFloorAmt + '万</td>';
            }
        }
    } else if (purFloorAmt != null && purFloorAmt == 0) {
        if (currencyType != 1) {
            html += '<td>0</td>';
        } else {
            html += '<td>0元</td>';
        }
    } else {
        html += '<td>暂无</td>';
    }
    if (dataTr.investPeriod != null && dataTr.investPeriod != "") {
        html += '<td>' + dataTr.investPeriod + '天</td>';
    } else {
        html += '<td>暂无</td>';
    }


    if (dataTr.collBgnDate != null && dataTr.collBgnDate != "") {
        var collBgnDate = Format(new Date(dataTr.collBgnDate));
        var collEndDate = Format(new Date(dataTr.collEndDate));
        if (dataTr.proMode == "1") { //可赎回
            html += '<td class="list_time">' + collBgnDate + '<br />-<br /></td>';
        } else {
            html += '<td class="list_time">' + collBgnDate + '<br />-<br />' + collEndDate + '</td>';
        }
    } else {
        html += '<td class="list_time">暂无</td>';
    }

    var UNIT_NETVAL = "";
    if (dataTr.isNetvalPro == 0) {
        //非净值型
        var yieldRate = dataTr.yieldRate;
        if (yieldRate == null) {
            html += '<td>暂无</td>';
        } else if (yieldRate == 0) {
            html += '<td style="font-size: 14px;">详见说明书</td>';
        } else {
            html += '<td>' + dataTr.yieldRate + '%</td>';
        }
    } else if (dataTr.isNetvalPro == 1) {
        //净值型
        var yieldRate = dataTr.yieldRate;
        if (yieldRate == null) {
            html += '<td>暂无</td>';
        } else if (yieldRate == 0) {
            html += '<td style="font-size: 14px;">详见说明书</td>';
        } else {
            html += '<td>' + dataTr.yieldRate + '%</td>';
        }
    }

    var saleStatus = dataTr.saleStatus;     //销售状态 "01:认购 02:申购 03:可预约 04:预售 05:已售完"
    var purFloorAmt2 = dataTr.purFloorAmt;  //起购金额
    var purStepAmt = dataTr.purStepAmt;     //递增金额
    var investPeriod = dataTr.investPeriod; //投资期限
    var pdType = dataTr.pdType.split('_')[0];            //产品类型
    var SURVIVING_FLAG = dataTr.pdType.split('_')[1];	//到期是否可自动再投资，add on 20170531
    var provinceId = dataTr.provinceId;     //一级分行号
    var currencyType = dataTr.currencyType; //币种代码

    var FUNC_NO = "";  //0-认购新增 2-申购
    if (saleStatus == "01") {
        FUNC_NO = "0"
    } else if (saleStatus == "02") {
        FUNC_NO = "2"
    }

    html += '<td><div class="btn">';
    var urlHtml = 'http://finance.ccb.com/cn/finance/jiaoyi/purchase.html?FUNC_NO=' + FUNC_NO + '&CURR_COD=' + currencyType + '&PRCT_CDE=' + pdId + '&SURVIVING_FLAG=' + SURVIVING_FLAG;
    urlHtml += '&PRCT_PRD=' + investPeriod + '&INDI_MIN_AMT=' + purFloorAmt2 + '&INDI_STEP_ATM=' + purStepAmt;
    if (allOrgFlag == 1) {
        urlHtml += '&PRCT_TYP=' + pdType + '&PROVINCE_ID=000';
        urlHtml += '&SEND_BRANCHID=';
    } else {
        urlHtml += '&PRCT_TYP=' + pdType + '&PROVINCE_ID=' + provinceId;
        if (provinceId.length > 3) {
            var province = provinceId.substr(0, 3);
            urlHtml += '&SEND_BRANCHID=' + province + '000000';
        } else {
            urlHtml += '&SEND_BRANCHID=' + provinceId + '000000';
        }
    }
    var isCcbcomPro = dataTr.isCcbcomPro;  //是否网站可购买 0-不可购买 1-可购买
    if (isCcbcomPro == "0") {
        if (saleStatus == "01" || saleStatus == "02" || saleStatus == "03") {
            var urlHtml1 = "./ProductDetails.html?PRODUCT_ID=" + pdId;
            html += '<span class="bl_btn" id="cut_color"><button onclick=\'window.open("' + urlHtml1 + '")\'>详情</button></span>';
        } else if (saleStatus == "04") {
            html += '<span style="background:none;padding-left:0px;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:2px;min-width:71px;">待售</button></span>';
        } else if (saleStatus == "05") {
            html += '<span style="background:none;padding-left:0px;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:2px;min-width:71px;">已抢光</button></span>';
        } else {
            html += '<span style="background:none;padding-left:0px;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:2px;min-width:71px;">已抢光</button></span>';
        }
    } else if (isCcbcomPro == "1") {
        if (saleStatus == "01" || saleStatus == "02") {
            urlHtml += "&UNIT_NETVAL=" + UNIT_NETVAL;
            html += '<span><button style="min-width:68px;" class="AcqProductClick" acqproductbtnname="购买" acqproductbtnid="buy"  onclick=\'LinkClickFunction(this);window.open("' + urlHtml + '")\'>购买</button></span>';
        } else if (saleStatus == "03") {
            var urlHtml2 = "http://finance.ccb.com/cn/finance/jiaoyi/reservation.html?PRODUCT_ID=" + pdId + "&PRODUCT_NAME=" + dataTr.name;
            html += '<span class="bl_btn" id="cut_color"><button onclick=\'window.open("' + urlHtml2 + '")\'>预约</button></span>';
        } else if (saleStatus == "04") {
            html += '<span style="background:none;padding-left:0px;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:2px;min-width:71px;">待售</button></span>';
        } else if (saleStatus == "05") {
            html += '<span style="background:none;padding-left:0px;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:2px;min-width:71px;">已抢光</button></span>';
        } else {
            html += '<span style="background:none;padding-left:0px;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:2px;min-width:71px;">已抢光</button></span>';
        }
    }

    html += "</div>";
    var hotStatus = dataTr.hotStatus; //新、热标志 "0：默认，无状态 1：新 2：热"
    if (hotStatus == "2") {
        html += '<img class="hot" src="./v3/images/hot.png"  />';
    } else if (hotStatus == "1") {
        html += '<img class="hot" src="./v3/images/new_list.png"  />';
    }
    html += '</td></tr>';
    return html;
}

//图像模式
function formatData(id, data) {
    var html = '<ul class="pro_list">';
    for (var i = 0; i < data.length; i++) {
        var saleStatus = data[i].saleStatus;     //销售状态 "01:申购 02:认购 03:可预约 04:预售 05:已售完"
        var purFloorAmt_is = datavalue['queryForm.purFloorAmt_is'];
        if (purFloorAmt_is == 1 &&
            (data[i].purFloorAmt == 50000 || data[i].purFloorAmt == 100000 || data[i].purFloorAmt == 500000)) { //起购金额选择“其他”时，过滤掉起购金额=5万 10万 50万的产品
        } else {
            html += siftDivDate(id, data[i]);
        }
    }
    html += '</ul>';
    $("#" + id).html(html);
}

function siftDivDate(id, dataTr) {
    var html = '<li>';
    var pdId = dataTr.code;	             //产品编号
    var name = dataTr.name;
    var currencyType = dataTr.currencyType;
    var channelSig = $.trim(dataTr.channel_sig);
    if (name == null || name == "") {
        html += '<h2 style="height:55px;">暂无</h2>';
    } else {
        var tit = name;
        if (name.length > 25) {
            name = name.substring(0, 25) + "...";
        }
        html += '<h2 style="height:55px;">';
        html += '<div class="AcqProductList"><div class="AcqProductItem"><div class="AcqProductID" style="display:none">' + pdId + '</div><a class="AcqProductName AcqProductClick" onclick="LinkClickFunction(this)" target="_blank" title="' + tit + '" href="./ProductDetails.html?PRODUCT_ID=' + pdId + '">' + name;
        if (channelSig != null && channelSig != " " && channelSig.length > 0) {
            html += '<span class="zu">' + channelSig + '</span>';
        }
        html += '</a></div></div></h2>';
    }
    var purFloorAmt = dataTr.purFloorAmt;
    if (purFloorAmt != null && purFloorAmt > 0) {
        purFloorAmt = parseFloat(purFloorAmt) / 10000;
        if (currencyType != 1) {
            html += '<p class="p_333">起购金额：' + dataTr.purFloorAmt + '</p>';
        } else {
            if (dataTr.purFloorAmt < 10000) {
                html += '<p class="p_333">起购金额：' + dataTr.purFloorAmt + '</p>';
            } else {
                html += '<p class="p_333">起购金额：' + purFloorAmt + ' 万</p>';
            }

        }
    } else if (purFloorAmt != null && purFloorAmt == 0) {
        if (currencyType != 1) {
            html += '<p class="p_333">起购金额：0 </p>';
        } else {
            html += '<p class="p_333">起购金额：0 </p>';
        }
    } else {
        html += '<p class="p_333">起购金额：暂无</p>';
    }
    html += '<p class="p_333">期限: ' + dataTr.investPeriod + ' 天</p>';
    var yieldSpec = "非保本";
    if (dataTr.yieldSpec == "1") {
        yieldSpec = "保本";
    }
    html += '<p class="p_333">是否保本：' + yieldSpec + '</p>';
    if (dataTr.collBgnDate != null && dataTr.collBgnDate != "") {
        var collBgnDate = Format(new Date(dataTr.collBgnDate));
        var collEndDate = Format(new Date(dataTr.collEndDate));
        if (dataTr.proMode == "1") { //可赎回
            html += '<p class="p_333">发行日期：' + collBgnDate + '-</p>';
        } else {
            html += '<p class="p_333">发行日期：' + collBgnDate + '-' + collEndDate.substr(5, collEndDate.length) + '</p>';
        }
    } else {
        html += '<p class="p_333">发行日期：暂无</p>';
    }

    var UNIT_NETVAL = "";
    if (dataTr.isNetvalPro == 0) {
        //非净值型
        var yieldRate = dataTr.yieldRate;
        if (yieldRate == null) {
            html += '<div class="income">业绩比较基准<p>暂无</p></div>';
        } else if (yieldRate == 0) {
            html += '<div class="income">业绩比较基准<p style="font-size:14px;margin-top:12px;">详见说明书</p></div>';
        } else {
            html += '<div class="income">业绩比较基准<p><b>' + dataTr.yieldRate + '</b><span>%</span></p></div>';
        }
    } else if (dataTr.isNetvalPro == 1) {
        //净值型
        var yieldRate = dataTr.yieldRate;
        if (yieldRate == null) {
            html += '<div class="income">七日年化收益率<p>暂无</p></div>';
        } else if (yieldRate == 0) {
            html += '<div class="income">七日年化收益率<p style="font-size:14px;margin-top:12px;">详见说明书</p></div>';
        } else {
            html += '<div class="income">七日年化收益率<p><b>' + dataTr.yieldRate + '</b><span>%</span></p></div>';
        }
    }


    html += '<div class="btn">';

    var pdId = dataTr.code;	                //产品编号
    var purFloorAmt2 = dataTr.purFloorAmt;  //起购金额
    var purStepAmt = dataTr.purStepAmt;     //递增金额
    var investPeriod = dataTr.investPeriod; //投资期限
    var pdType = dataTr.pdType;             //产品类型
    var provinceId = dataTr.provinceId;     //一级分行号
    var currencyType = dataTr.currencyType; //币种代码
    var saleStatus = dataTr.saleStatus;     //销售状态 "01:认购 02:申购 03:可预约 04:预售 05:已售完"
    var FUNC_NO = "";  //0-认购新增 2-申购
    if (saleStatus == "01") {
        FUNC_NO = "0"
    } else if (saleStatus == "02") {
        FUNC_NO = "2"
    }
    var urlHtml = 'http://finance.ccb.com/cn/finance/jiaoyi/purchase.html?FUNC_NO=' + FUNC_NO + '&CURR_COD=' + currencyType + '&PRCT_CDE=' + pdId;
    urlHtml += '&PRCT_PRD=' + investPeriod + '&INDI_MIN_AMT=' + purFloorAmt2 + '&INDI_STEP_ATM=' + purStepAmt;

    var allOrgFlag = dataTr.allOrgFlag;
    if (allOrgFlag == 1) {
        urlHtml += '&PRCT_TYP=' + pdType + '&PROVINCE_ID=000';
        urlHtml += '&SEND_BRANCHID=';
    } else {
        urlHtml += '&PRCT_TYP=' + pdType + '&PROVINCE_ID=' + provinceId;
        if (provinceId.length > 3) {
            var province = provinceId.substr(0, 3);
            urlHtml += '&SEND_BRANCHID=' + province + '000000';
        } else {
            urlHtml += '&SEND_BRANCHID=' + provinceId + '000000';
        }
    }
    var isCcbcomPro = dataTr.isCcbcomPro;  //是否网站可购买 0-不可购买 1-可购买
    if (isCcbcomPro == "0") {
        if (saleStatus == "01" || saleStatus == "02" || saleStatus == "03") {
            var urlHtml1 = "./ProductDetails.html?PRODUCT_ID=" + pdId;
            html += '<span class="bl_btn" id="cut_color"><button onclick=\'window.open("' + urlHtml1 + '")\'>详情</button></span>';
        } else if (saleStatus == "04") {
            html += '<a href="javascript:void();" class="annin fl" target="_blank">';
            html += '<input style="color:#fff;background:#ccc;cursor:text;border-radius:3px;" type="button" value="待售"></a>';
        } else if (saleStatus == "05") {
            html += '<a href="javascript:void();" class="annin fl" target="_blank">';
            html += '<input style="color:#fff;background:#ccc;cursor:text;border-radius:3px;" type="button" value="已抢光"></a>';
        } else {
            html += '<a href="javascript:void();" class="annin fl" target="_blank">';
            html += '<input style="color:#fff;background:#ccc;cursor:text;border-radius:3px;" type="button" value="已抢光"></a>';
        }
    } else if (isCcbcomPro == "1") {
        if (saleStatus == "01" || saleStatus == "02") {
            urlHtml += "UNIT_NETVAL=" + UNIT_NETVAL;
            html += '<span><button onclick=\'LinkClickFunction(this);window.open("' + urlHtml + '")\'>购买</button></span>';
        } else if (saleStatus == "03") {
            var urlHtml2 = "http://finance.ccb.com/cn/finance/jiaoyi/reservation.html?PRODUCT_ID=" + pdId + "&PRODUCT_NAME=" + dataTr.name;
            html += '<span class="bl_btn" id="cut_color"><button onclick=\'window.open("' + urlHtml2 + '")\'>预约</button></span>';
        } else if (saleStatus == "04") {
            html += '<span style="background:none;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:3px;">待售</button></span>';
        } else if (saleStatus == "05") {
            html += '<span style="background:none;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:3px;">已抢光</button></span>';
        } else {
            html += '<span style="background:none;"><button style="color:#fff;background:#ccc;cursor:text;border-radius:3px;">已抢光</button></span>';
        }
    }
    var proMode = "不可赎回";
    if (dataTr.proMode == "1") {
        proMode = "可赎回";
    }
    var riskLevel = "无风险";
    if (dataTr.riskLevel == "02") {
        riskLevel = "较低风险";
    } else if (dataTr.riskLevel == "03") {
        riskLevel = "中等风险";
    } else if (dataTr.riskLevel == "04") {
        riskLevel = "较高风险";
    } else if (dataTr.riskLevel == "05") {
        riskLevel = "高风险";
    }
    var moneyType = "外币";
    if (currencyType == "01") {
        moneyType = "人民币";
    } else if (currencyType == "12") {
        moneyType = "英镑";
    } else if (currencyType == "13") {
        moneyType = "港币";
    } else if (currencyType == "14") {
        moneyType = "美元";
    } else if (currencyType == "15") {
        moneyType = "瑞士法郎";
    } else if (currencyType == "27") {
        moneyType = "日元";
    } else if (currencyType == "28") {
        moneyType = "加元";
    } else if (currencyType == "29") {
        moneyType = "澳元";
    } else if (currencyType == "33") {
        moneyType = "欧元";
    }
    var allOrgFlag = dataTr.allOrgFlag;
    var provinceId = dataTr.provinceId;
    var isSaleAll = "全国";
    if (allOrgFlag == "0") {
        isSaleAll = "";
        if (provinceId != null && provinceId != "") {
            var saleArray = provinceId.split(",");
            var s = saleArray.length;
            if (saleArray.length >= 1) {
                s = 1;
            }
            for (var j = 0; j < s; j++) {
                for (var i = 0; i < citsy.length; i++) {
                    if (saleArray[j] == citsy[i].code) {
                        isSaleAll += citsy[i].name;
                    }
                }
                if (j == s - 1) {
                    isSaleAll += "等" + saleArray.length + "家分行";
                }
            }
        }
    }

    html += "</div>";
    html += "<dl class=\"pro_list_data\">"
        + "<dd>可否赎回：" + proMode + "</dd>"
        + "<dd>是否保本：" + yieldSpec + "</dd>"
        + "<dd>风险等级：" + riskLevel + "</dd>"
        + "<dd>投资币种：" + moneyType + "</dd>"
        + "<dd style='width:220px;'>发行区域：" + isSaleAll + "</dd>"
        + "</dl>"
    var hotStatus = dataTr.hotStatus; //新、热标志 "0：默认，无状态 1：新 2：热"
    if (hotStatus == "2") {
        html += '<img class="hot" src="./v3/images/hot.png"  />';
    } else if (hotStatus == "1") {
        html += '<img class="hot" src="./v3/images/new_list.png"  />';
    }
    html += '</li>';
    return html;
}

/*日期格式化*/
function Format(strTime) {
    var date = new Date(strTime);
    return date.getFullYear() + "." + (date.getMonth() + 1) + "." + date.getDate();
}

//排序操作方法
function orderByClick(obj, orderById) {
    $(".mo_rank_lei a").each(function () {
        //将其余的排序条件初始化
        if (this != obj) {
            $(this).attr("state", "1");
        }
    });
    if (orderById != null && orderById != "") {
        datavalue['orderBys'] = orderById; //排序参数
        if ($(obj).attr("state") == "1") { //默认降序排列
            datavalue['ascOrDescs'] = 'desc'; //排序参数 降序
            $(obj).attr("state", "2");
        } else if ($(obj).attr("state") == "2") {
            datavalue['ascOrDescs'] = 'asc'; //排序参数 升序
            $(obj).attr("state", "1");
        }
    } else {
        datavalue['orderBys'] = undefined;
        datavalue['ascOrDescs'] = undefined;
    }
    addlist(null, 1);
}

$(function () {

    /*搜索框 and*/
    jQuery.focusblurmenu = function (focusdom, focuswidthnew, animatetime) {
        var focusblurmenuid = $(focusdom);
        var defval = focusblurmenuid.val();
        //var defval = "请输入产品名称/编号";
        focusblurmenuid.focus(function () {
            var thisval = $(this).val();
            if (thisval == defval) {
                $(this).attr("style", "color:#333333;width:160px;");
                $(this).val("");
            }
        });
        focusblurmenuid.blur(function () {
            var thisval = $(this).val();
            if (thisval == "") {
                $(this).attr("style", "color:#bbbbbb;width:160px;");
                $(this).val(defval);
            }
        });
    };
    $.focusblurmenu("#productName", null, null);
    /*搜索框 end*/

    //横向大菜单选中样式
    $("#a_product").css("color", "#0066b3");

    $(".wealth_li input").keyup(function () {
        if ($(this).val() == '') {
            $(this).parent().parent().next().find("span").addClass("gray");
        } else {
            $(this).parent().parent().next().find("span").removeClass("gray");
        }
    });

    //搜索框回车键查询功能
    $("#productName").keyup(function () {
        if (event.keyCode == 13) {  //回车键查询
            addlist();
        }
    });

    //动态为元素绑定鼠标悬浮/离开事件
    $(document).on({
        mouseenter: function () {
            $(this).find(".pro_list_data").stop();
            $(this).find(".pro_list_data").slideDown(500, function () {
            });
        },
        mouseleave: function () {
            $(this).find(".pro_list_data").stop();
            $(this).find(".pro_list_data").slideUp(500, function () {
            });
        }
    }, ".pro_list li");

    //动态为元素绑定鼠标悬浮/离开事件
    $(document).on({
        mouseenter: function () {
            $(this).parent().find(".pro_list_data").stop();
            $(this).parent().find(".pro_list_data").slideUp(500, function () {
            });

        },
        mouseleave: function () {
            $(this).parent().find(".pro_list_data").stop();
            $(this).parent().find(".pro_list_data").slideDown(500, function () {
            });
        }
    }, ".pro_list li .btn");


    //选中可在线购买按钮
    $("input[name='isCcbcomProInput']").click(function () {
        if (this.checked) {
            //获取数据
            datavalue['queryForm.isCcbcomPro'] = 1;
            addlist(null, 1);
        } else {
            datavalue['queryForm.isCcbcomPro'] = undefined; //删除属性
            addlist(null, 1);
        }
    });

    /* 带参数链接处理 and */
    var url = location.search;
    if (url.indexOf("?") != -1) {

        //产品名称 productName
        if (url.indexOf("productName=") != -1) {
            var productName = decodeURI(requestParameter("productName"));
            if (productName != null && productName != '' && productName != '#none') {
                //datavalue['queryForm.name']=productName;
                $("#productName").attr("style", "color:#333333;width:160px;");
                $("#productName").val(productName);
            }
        }

        //销售状态 status
        if (url.indexOf("status=") != -1) {
            var status = decodeURI(requestParameter("status"));
            var statusText = "";
            if (status != null && status != "" && status != "undefined") {
                if (status == "-1" || status == "在售") {
                    status = "-1";
                    statusText = "在售";
                } else if (status == "04" || status == "待售") {
                    status = "04";
                    statusText = "待售";
                } else if (status == "05" || status == "已售完") {
                    status = "05";
                    statusText = "已售完";
                } else if (status == "03" || status == "可预约") {
                    status = "03";
                    statusText = "可预约";
                }
                datavalue['queryForm.saleStatus'] = status;
                $("#status").text(statusText);
                $("#status").attr("data-value", status);
                $(".sc_lei").find("li").eq(1).show();
                $(".sc_lei").find("li").eq(1).find("span").html(statusText);
            }
        }

        //净值型或非净值新 isNetvalPro 0 非净值型 1 净值型
        if (url.indexOf("isNetvalPro=") != -1) {
            var value = decodeURI(requestParameter("isNetvalPro"));
            var isNetvalPro = "";
            if (value != null && value != "") {
                if (value == '0') {
                    isNetvalPro = "非净值型";
                } else if (value == '1') {
                    isNetvalPro = "净值型";
                }
                datavalue['queryForm.isNetvalPro'] = value;
                $("#isNetvalPro").text(isNetvalPro);
                $("#isNetvalPro").attr("data-value", value);
                $(".sc_lei").find("li[id='queryForm\\.isNetvalPro']").show().find("span").html(isNetvalPro);
            }
        }

        //预期收益 expectProfit
        if (url.indexOf("expectProfit=") != -1) {
            var value = decodeURI(requestParameter("expectProfit"));
            var expectProfitText = "";
            if (value != null && value != "") {
                if (value == '03') {
                    var yieldRateEnd = 0.03 * 100;
                    datavalue['queryForm.yieldRateStart'] = undefined;
                    datavalue['queryForm.yieldRateEnd'] = yieldRateEnd;
                    expectProfitText = "3%以下";
                }
                if (value == '34') {
                    var yieldRateStart = 0.03 * 100;
                    var yieldRateEnd = 0.04 * 100;
                    datavalue['queryForm.yieldRateStart'] = yieldRateStart;
                    datavalue['queryForm.yieldRateEnd'] = yieldRateEnd;
                    expectProfitText = "3%-4%";
                }
                if (value == '45') {
                    var yieldRateStart = 0.04 * 100;
                    var yieldRateEnd = 0.05 * 100;
                    datavalue['queryForm.yieldRateStart'] = yieldRateStart;
                    datavalue['queryForm.yieldRateEnd'] = yieldRateEnd;
                    expectProfitText = "4%-5%";
                }
                if (value == '56') {
                    var yieldRateStart = 0.05 * 100;
                    var yieldRateEnd = 0.06 * 100;
                    datavalue['queryForm.yieldRateStart'] = yieldRateStart;
                    datavalue['queryForm.yieldRateEnd'] = yieldRateEnd;
                    expectProfitText = "5%-6%";
                }
                if (value == '60') {
                    var yieldRateStart = 0.06 * 100;
                    datavalue['queryForm.yieldRateStart'] = yieldRateStart;
                    datavalue['queryForm.yieldRateEnd'] = undefined;
                    expectProfitText = "6%以上";
                }
                $("#expectProfit").text(expectProfitText);
                $("#expectProfit").attr("data-value", value);
                $(".sc_lei").find("li[id='queryForm.expectProfit']").show().find("span").html(expectProfitText);
            }
        }

        //投资期限 limit
        if (url.indexOf("limit=") != -1) {
            var value = decodeURI(requestParameter("limit"));
            var textStr = "";
            if (value != null && value != "" && value != "undefined") {
                if (value == '13' || value == '3个月内') {
                    var investPeriodEnd = 3 * 30;
                    value = '13';
                    datavalue['queryForm.investPeriodStart'] = undefined;
                    datavalue['queryForm.investPeriodEnd'] = investPeriodEnd;
                    textStr = "3个月内";
                }
                if (value == '36' || value == '3-6个月') {
                    value = '36';
                    var investPeriodStart = 3 * 30;
                    var investPeriodEnd = 6 * 30;
                    datavalue['queryForm.investPeriodStart'] = investPeriodStart;
                    datavalue['queryForm.investPeriodEnd'] = investPeriodEnd;
                    textStr = "3-6个月";
                }
                if (value == '69' || value == '6-9个月') {
                    value = '69';
                    var investPeriodStart = 6 * 30;
                    var investPeriodEnd = 9 * 30;
                    datavalue['queryForm.investPeriodStart'] = investPeriodStart;
                    datavalue['queryForm.investPeriodEnd'] = investPeriodEnd;
                    textStr = "6-9个月";
                }
                if (value == '912' || value == '9-12个月') {
                    value = '912';
                    var investPeriodStart = 9 * 30;
                    var investPeriodEnd = 12 * 30;
                    datavalue['queryForm.investPeriodStart'] = investPeriodStart;
                    datavalue['queryForm.investPeriodEnd'] = investPeriodEnd;
                    textStr = "9-12个月";
                }
                if (value == '12' || value == "12个月以上") {
                    value = '12';
                    var investPeriodStart = 365;
                    datavalue['queryForm.investPeriodStart'] = investPeriodStart;
                    datavalue['queryForm.investPeriodEnd'] = undefined;
                    textStr = "12个月以上";
                }
                $("#limit").text(textStr);
                $("#limit").attr("data-value", value);
                $(".sc_lei").find("li[id='queryForm.investPeriodEnd']").show().find("span").html(textStr);
            }
        }

        //起购金额 startMoney
        if (url.indexOf("startMoney=") != -1) {
            var value = decodeURI(requestParameter("startMoney"));
            if (value != null && value != "") {
                if (value == '5' || value == '10' || value == '50') {
                    datavalue['queryForm.purFloorAmt'] = value * 10000;
                    $("#startMoney").text("其它");
                    $("#startMoney").attr("data-value", value);
                    $(".sc_lei").find("li[id='queryForm.purFloorAmt']").show().find("span").html("其它");
                } else {
                    datavalue['queryForm.purFloorAmt'] = value;
                    $("#startMoney").text(value + "万");
                    $("#startMoney").attr("data-value", value);
                    $(".sc_lei").find("li[id='queryForm.purFloorAmt']").show().find("span").html(value + "万");
                }
            }
        }

        //可否赎回 isRedeem
        if (url.indexOf("isRedeem=") != -1) {
            var value = decodeURI(requestParameter("isRedeem"));
            var textStr = "";
            if (value != null && value != "") {
                if (value == '0') {
                    textStr = "不可赎回";
                } else if (value == '1') {
                    textStr = "可赎回";
                }
                datavalue['queryForm.proMode'] = value;
                $("#isRedeem").text(textStr);
                $("#isRedeem").attr("data-value", value);
                $(".sc_lei").find("li[id='queryForm.proMode']").show().find("span").html(textStr);
            }
        }

        //是否保本 isLose
        if (url.indexOf("isLose=") != -1) {
            var value = decodeURI(requestParameter("isLose"));
            var textStr = "";
            if (value != null && value != "") {
                if (value == '0') {
                    textStr = "非保本";
                } else if (value == '1') {
                    textStr = "保本";
                }
                datavalue['queryForm.yieldSpec'] = value;
                $("#isLose").text(textStr);
                $("#isLose").attr("data-value", value);
                $(".sc_lei").find("li[id='queryForm.yieldSpec']").show().find("span").html(textStr);
            }
        }

        //风险等级 riskGrade
        if (url.indexOf("riskGrade=") != -1) {
            var value = decodeURI(requestParameter("riskGrade"));
            var textStr = "";
            if (value != null && value != "") {
                if (value == '01') {
                    textStr = "无风险";
                } else if (value == '02') {
                    textStr = "较低风险";
                } else if (value == '03') {
                    textStr = "中等风险";
                } else if (value == '04') {
                    textStr = "较高风险";
                } else if (value == '05') {
                    textStr = "高风险";
                }
                datavalue['queryForm.riskLevel'] = value;
                $("#riskGrade").text(textStr);
                $("#riskGrade").attr("data-value", value);
                $(".sc_lei").find("li[id='queryForm.riskLevel']").show().find("span").html(textStr);
            }
        }

        //投资币种 investCurrency
        // if (url.indexOf("investCurrency=") != -1) {
        //     var value = decodeURI(requestParameter("investCurrency"));
        //     var textStr = "";
        //     if (value != null && value != "") {
        //         if (value == '01') {
        //             textStr = "人民币";
        //         } else if (value == '02') {
        //             textStr = "外币";
        //         }
        //         datavalue['queryForm.currencyType'] = value;
        //         $("#investCurrency").text(textStr);
        //         $("#investCurrency").attr("data-value", value);
        //         $(".sc_lei").find("li").eq(8).show();
        //         $(".sc_lei").find("li").eq(8).find("span").html(textStr);
        //     }
        // }

        //产品类型 financeProduct
        if (url.indexOf("financeProduct=") != -1) {
            var value = decodeURI(requestParameter("financeProduct"));
            var textStr = "";
            var id;
            if (value != null && value != "") {
                if (value == '01') {
                    id = 1; //利得盈
                } else if (value == '02') {
                    id = 2; //建行财富
                } else if (value == '03') {
                    id = 0; //乾元
                } else if (value == '04') {
                    id = 3; //汇得盈
                } else if (value == '05') {
                    id = 4; //其它
                }
                brand = $(".product_tab .tab5").eq(id).attr("dbvalue");
                $(".product_tab .tab5").eq(id).click();
            }
        }

    }
    /* 带参数链接处理 end */

    $(".pro_infor_detail").each(function () {
        var txt = $(this).text();
        if (txt.length <= 75) {
            $(this).parent().find("a").hide();
        }
    });

    /* 加载销售区域列表 and*/
    if (citsy != null) {
        var html = '<li data-option="000" style="float:none;"><span class="" state="1"></span><a>全国</a></li>';
        for (var i = 0; i < citsy.length; i++) {
            html += '<li data-option="' + citsy[i].code + '"><span class=""  state="1"></span><a>' + citsy[i].name + '</a></li>';
        }
        $("#saleCitys").html(html);
    }
    /* 加载销售区域列表 end*/
    /* 初始化分行参数 and*/
    var bankCode = $.cookie("bankCode"); //取出定位分行号
    bankCode = bankCode.substring(0, 3); //截取前三位
    if (bankCode != null && bankCode != "" && bankCode != "null") {
        datavalue['queryForm.provinceId'] = bankCode;
        var bankName = decodeURI($.cookie("bankName")); //取出分行名称
        bankName = bankName.replace("分行", ""); //替换分行两字
        $("#provinceName").html(bankName);
    } else { //数据如异常 默认取北京
        datavalue['queryForm.provinceId'] = 110;
        $("#provinceName").html("北京");
    }
    //addlist();
    /* 初始化分行参数 end*/
});

