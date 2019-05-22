var webroot=document.location.href;
webroot=webroot.substring(webroot.indexOf('//')+2,webroot.length);
webroot=webroot.substring(webroot.indexOf('/')+1,webroot.length);
webroot=webroot.substring(0,webroot.indexOf('/'));
var jsonUrl="/"+webroot;
$(function(){
    tablePostJson();
    ModalToggle();//摸态框显示|隐藏
    search();

    tableToolbar();
    //$('.table_box td').darkTooltip();
});

//模态框
function ModalToggle(){
    //增加企业信息
    $('#see').click(function(){
        $('#ePrisename').removeAttr('data-inputid');
        $('.pop-up input[type = text]').val('');
        $('.pop-up').show();
        $('.mask').show();
    });
    //点击关闭
    $('#del').click(function () {
        $('.pop-up').hide();
        $('.mask').hide();
    });

    //重置
    $('#reset').click(function(){
        $('.pop-up input').val('')
    });

    //保存
    $('#save').click(function(){
    	var accout = localStorage.getItem("username");
        if($('.pop-up input[data-inputId]').length <= 0){
            var url = jsonUrl+'/company/add';
            var data = $.param({'password': hex_md5($('#pwd').val())}) + '&' +$('#form_1').serialize() + "&" + $.param({'username':accout});
            var type1;
            for(var i = 0 ; i < $('.pop-up input[type = text]').length;i++){
                if(!Boolean($('.pop-up input[type = text]').eq(i).val())){
                	console.log($('.pop-up input[type = text]').eq(i).val())
                    type1 = false
                }
            }
            if(type1 == false){
                alert('请检查表单内信息是否输入完整')
            }else{
                initAjax(url,successSeeFun,data,'post');
            }
            //点击查看成功回调
            function successSeeFun(data){
                if(data.status == 0){
                    alert(data.msg);
                    $('.pop-up').hide();
                    $('.mask').hide();
                    tablePostJson();
                }else{
                    alert(data.msg);
                    $('.pop-up').hide();
                    $('.mask').hide();
                }
            }
        }else{
        	var accout = localStorage.getItem("username");
            var editUrl = jsonUrl+'/company/edit';
            var editData = {
                companyId:$('#ePrisename').attr('data-inputId'),
                userNightId:$('#corporation').attr('data-nameId'),
                conMobile:$('#contactway').val(),
//                password:hex_md5($('#pwd').val()),
                password:$('#pwd').val(),
                contect:$('#contacts').val(),
                orgCode:$('#organization').val(),
                companyName:$('#ePrisename').val(),
                asccout:$('#user').val(),
                tel:$('#contact').val(),
                corName:$('#corporation').val(),
                username:accout
            };
            var type2;
            for(var j = 0 ; j < $('.pop-up input[type = text]').length;j++){
                if(!Boolean($('.pop-up input[type = text]').eq(j).val())){
                    type2 = false
                }
            }
            if(type2 == false){
                alert('请检查表单内信息是否输入完整')
            }else{
                initAjax(editUrl,successEditFun,editData,'post');
            }


            function successEditFun(data){
                if(data.status == 0){
                    alert('更新成功');
                    $('.pop-up').hide();
                    $('.mask').hide();
                    tablePostJson()
                }
            }
        }
    });
}

//点击查询
function search(){
    $('#find_btn').click(function(){
        var start = 1;
        var data ={
            companyName:$('#ss').val().trim(),
            start:start,
        };
        var accout = localStorage.getItem("username");
        initAjax(jsonUrl+'/company/list?username=' + accout + "&" +new Date().getTime(),tableSearch,data,'post');

        function tableSearch(data){
            tableInitJson(data);
            pagingInit(data);
        }

    })
}





//表格查看、删除按钮
function tableToolbar(){

    var tableBox = $('#table_box');
    //查看
    tableBox.on('click','#see',function(){
        var comId =$(this).parents('tr').find($('td[data-comId]')).attr('data-comId');
        var accout = localStorage.getItem("username");
        var see_data ={
            companyId:comId,
            username:accout
        };
        $('.pop-up').show();
        $('.mask').show();
        initAjax(jsonUrl+'/company/before_edit?'+new Date().getTime(),seeSuccess,see_data,'get')
    });

    function seeSuccess(data){
    	if(data.type == 'S'){
    		//$('.pop-up input').attr('readonly',false);
    		//$('#save').show();
    		//$('#reset').show();
    		//$('#del').css('margin','47px');
    	}else{
    		$('.pop-up input').attr('readonly',true);
    		$('#save').hide();
    		$('#reset').hide();
    		$('#del').css('margin','0');
    		$('.clickbtn').css('text-align','center')
    	}

        $('#ePrisename').attr('data-inputId',data.companyId).val(data.companyName);
        $('#contact').val(data.tel);
        $('#corporation').attr('data-nameId',data.userNightId).val(data.corName);
        $('#contacts').val(data.contect);
        $('#contactway').val(data.conMobile);
        $('#organization').val(data.orgCode);
        $('#user').val(data.asccout);
        $('#pwd').val(data.password);
    }


    //删除
    tableBox.on('click','#remove',function(){
        if(confirm('确定要删除此行')){
            var delId =$(this).parents('tr').find($('td[data-comId]')).attr('data-comId');
            //console.log(delId)
            initAjax(jsonUrl+'/company/'+delId,delSuccess,'','delete');
            function delSuccess(data){
            	if(data.status == 0){
            		tablePostJson();
            	}
            }
        }
    })
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

//初始化表格分页数据
function tablePostJson(){
	var accout = localStorage.getItem("username");
    var url = jsonUrl+'/company/list';
    var data = {
        companyName:$('#ss').val(),
        start: $('.focus').text(),
        username:accout
    };
    initAjax(url,tableSuccess,data,'post',tableError);
    //成功回调
    function tableSuccess(data){
        if(data.status == 0){
            $('#pageNum').val(data.start);
            tableInitJson(data);
            pagingInit(data)
        }
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
    $.each(data.companyNights,function(index,item){
        str += '<tr>';
        str +=' <td>'+(index+1)+'</td>';
        str +=' <td data-comId='+item.id+' title='+item.companyName+'>'+item.companyName+'</td>';
        str +=' <td title='+item.name+'>'+item.name+'</td>';
        str +=' <td title='+item.orgCode+'>'+item.orgCode+'</td>';
        if(data.type == 'S'){
            str +=' <td><span class="see" id="see" style="margin-right: 5px;">查看</span><span class="td_btn remove" id="remove">删除</span></td>';
        }else{
        	$('.add_company').hide();// TODO
        	 str +=' <td><span class="see" id="see" style="margin-right: 5px;">查看</span></td>';
        }

        str +='</tr>';
    });

    if(data.companyNights == ''){
    	if(data.type != 'S'){
        	$('.add_company').hide();
        }
    }

    tableWrpper.append(str)
}

//分页初始化
function pagingInit(data){

    var page =$('#pageToolbar');
    page.empty();
    page.Paging({
        current:data.start,
        count:data.totalRecords == '0' ? '1' : data.totalRecords,
        pagesize:data.limit,
        callback:function(page,size,count){
        	var accout = localStorage.getItem("username");
            var data = {
            		start:page,
            		username:accout,
                    companyName:$('#ss').val(),
            		username:accout
            		};
            initAjax(jsonUrl+'/company/list',tableInitJson,data,'post')
        }
    });
}

