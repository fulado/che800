var webroot=document.location.href;
webroot=webroot.substring(webroot.indexOf('//')+2,webroot.length);
webroot=webroot.substring(webroot.indexOf('/')+1,webroot.length);
webroot=webroot.substring(0,webroot.indexOf('/'));
var jsonUrl="/"+webroot ;
var username = localStorage.getItem("username");

$(function () {
    clickUp();
    noThough();
    tablePostJson();
    search();
    exportExcel();
    exportXml();
});

function search(){
    $('.find_btn').click(function(){
        var start = 1;
        var data ={
        	username:localStorage.getItem("username"),
        	carNo:$('#ss').val().trim(),
            start:start
        };
        tablePostJson();

    })
}

function exportExcel(){
	$(".search_input .outexcel").click(function(){
		window.location.href = jsonUrl+'/nigth_auto/export_excel?username=' + localStorage.getItem("username")
			+ "&" + "companyName=" + $('#ss').val().trim();
	});
}

function exportXml(){
	$(".search_input .outxmls").click(function(){
		window.location.href = jsonUrl+'/nigth_auto/export_xml?username=' + localStorage.getItem("username")
		+ "&" + "companyName=" + $('#ss').val().trim();
	});
}


function inExcel(){
		var formData = new FormData($("#excelform")[0]);
		$.ajax({
			url : jsonUrl + "/nigth_auto/recive_excel?username=" + localStorage.getItem("username"),
			type : 'post',
			data : formData,
			async: false,		
			contentType : false,
			processData:false,
			success : function(data){
				var JsonStatus =eval('('+data+')').status;
				if(JsonStatus == '0'){
					alert("审核成功");
					 $('.pop-up1').hide();
				     $('.mask').hide();
					tablePostJson();
				} else {
					alert("审核失败");
				}
			}
		});
}


//点击不通过
var c_Id ;
function noThough(){
    var tableBox = $('#table_box');
    tableBox.on('click','[data-id="no_see"]',function(){
         c_Id = $(this).parents('tr').find('.com').attr('data-comId');
        $('.pop-up').show();
        $('.mask').show();
    });
    
    
    tableBox.on('click','[data-id="see"]',function(){
    	var comId = $(this).parents('tr').find('.com').attr('data-comId');
    		var data = {
        			username:username,
        			id:comId,
        			status:'P',
        			reason:$('#reason').val()
        	};
        	initAjax(jsonUrl + "/nigth_auto/audi",NoseeSuccess,data,'post');
        	function NoseeSuccess(){
        		if(status == 0){
        		
        			tablePostJson()
        		}else{
        			alert('更新失败')
        		}
        	}
    });
    
    
    $('#save').click(function(){
    	if(!Boolean($.trim($('#reason').val()))){
    		alert('请填写原因')
    	}else{
    	var data = {
    			username:username,
    			id:c_Id,
    			status:'F',
                reason:$.trim($('#reason').val())
    	};
    	initAjax(jsonUrl + "/nigth_auto/audi",seeSuccess,data,'post');
    	function seeSuccess(){
    		if(status == 0){
    			  $('.pop-up').hide();
    		        $('.mask').hide();
    			tablePostJson();
                $('.pop-up textarea').attr('value','')
    		}else{
    			alert('更新失败')
    		}
    	}
    	}
    });

    //点击删除
    $('#del').click(function () {
        $('.pop-up').hide();
        $('.mask').hide();
    });

}

function clickUp(){
	//上传excel
    $('.inexcel').click(function(){
        $('.pop-up1').show();
        $('.mask').show();
    });

    /*
    $('#out').click(function(){
        var fileVal = $('.pop-up1 input[type = file]').val();
        if (fileVal!= '') {
            var reg = /^.*\.(?:xls|xlsx)$/i;//文件名可以带空格
            if (!reg.test(fileVal)) {//校验不通过
                alert("请上传excel格式的文件!");
                return false;
            }
            else{
                inExcel();
            }
        }else if(!Boolean(fileVal)){
            alert('请选择要上传的类型')
        }
    });*/

    $('#close').click(function(){
        $('.pop-up1').hide();
        $('.mask').hide();
    })
    
    //上传xml
    $(".inxmls").click(function(){
    	$('.pop-up2').show();
        $('.mask').show();
    });
    
    $('#outxmls').click(function(){
        var fileVal = $('.pop-up2 input[type = file]').val();
        if (fileVal!= '') {
                inXml();
        }else if(!Boolean(fileVal)){
            alert('请选择要上传的类型')
        }
    });
    
    $('#closexml').click(function(){
        $('.pop-up2').hide();
        $('.mask').hide();
    })
}

function inXml(){
	var formData = new FormData($("#xmlform")[0]);
	$.ajax({
		url : jsonUrl + "/nigth_auto/recive_xml?username=" + localStorage.getItem("username"),
		type : 'post',
		data : formData,
		async: false,		
		contentType : false,
		processData:false,
		success : function(data){
			var JsonStatus =eval('('+data+')').status;
			if(JsonStatus == '0'){
				alert("审核成功");
				 $('.pop-up2').hide();
			     $('.mask').hide();
				tablePostJson();
			} else {
				alert("审核失败");
			}
		}
	});
}

//初始化表格分页数据
function tablePostJson(){

    var url = jsonUrl+'/nigth_auto/list';
    var data = {
        companyName:$('#ss').val(),
        start: $('.focus').text(),
        username:username
    };
    initAjax(url,tableSuccess,data,'post',tableError);
    //成功回调
    function tableSuccess(data){
    	 tableInitJson(data);
         pagingInit(data)
    }
    //失败回调
    function tableError(data){
    }
}

//表格内容初始化
function tableInitJson(data){
    var tableWrpper =$('.table_box tbody');
    tableWrpper.empty();
    var str = '';
    $.each(data.carNightVos,function(index,item){
    
        str += '<tr>';
        str +=' <td>'+(index+1)+'</td>';
        str +=' <td data-comId='+item.id+' class="com" title='+item.companyName+'>'+item.companyName+'</td>';
        str +=' <td title='+item.name+'>'+item.name+'</td>';
        str +=' <td title='+item.carNo+'>'+item.carNo+'</td>';
        str +=' <td title='+item.vin+'>'+item.vin+'</td>';
        str +=' <td title='+item.carTypeNo+'>'+item.carTypeNo+'</td>';
        str +=' <td title='+item.engineNo+'>'+item.engineNo+'</td>';
        str +=' <td title='+item.registTime+'>'+item.registTime.split(' ')[0]+'</td>';
        str +=' <td title='+item.activeArea+'>'+item.activeArea+'</td>';
        str +=' <td title='+item.activeAddr+'>'+item.activeAddr+'</td>';
        if(Boolean(item.reason)){
        	str +=' <td title='+item.reason+'>'+item.reason+'</td>';
        } else {
        	str +=' <td></td>';
        }
        
        if(item.status == 'P'){
        	  str +=' <td>通过</td>';
        }else if(item.status == 'F'){
        	  str +=' <td>不通过</td>';
        }else if(item.status == 'T'){
        	 str +=' <td><span class="see" data-id="see" style="margin-right: 8px">通过</span><span class="see no_see" data-id="no_see">不通过</span></td>';
        }
        
        str +='</tr>';
    });
    tableWrpper.append(str)
}

//分页初始化
function pagingInit(data){
    var page =$('#pagingToolBar');
    page.empty();
    page.Paging({
        current:data.start,
        count:data.totalRecords == '0' ? '1' : data.totalRecords,
        pagesize:data.limit,
        callback:function(page,size,count){
            var data = {
                start:page,
                companyName:$('#ss').val(),
                username:username
            };
            initAjax(jsonUrl+'/nigth_auto/list',tableInitJson,data,'post')
        }
    });
}



//ajax初始化
function initAjax(url,func,dataobj,type,fune){
    $.ajax({
        url:url,
        type:type,
        data:dataobj,
        dataType:'json',
        success:func,
        error:fune
    });
}