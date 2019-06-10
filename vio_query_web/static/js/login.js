var webroot=document.location.href;
webroot=webroot.substring(webroot.indexOf('//')+2,webroot.length);
webroot=webroot.substring(webroot.indexOf('/')+1,webroot.length);
webroot=webroot.substring(0,webroot.indexOf('/'));
var jsonUrl="/"+webroot;
$(function(){
	// var username = localStorage.getItem("username");
	// if(username != null){
	// 	window.location = '../nigth_user/login_success';
	// }
    //    Yz_Click();
   $('#login_button').click(function () {
       alert(1);
//	   localStorage.setItem("username",  $('#username').val());
       login();
   });

    $("body").bind('keyup',function(event) {
        if(event.keyCode==13){
            $('#login_button').click()
        }
    });

    $('#link_button').click(function(){

    	window.location = jsonUrl+'/nigth_user/download'

    });

    // 申请流程下载
    $('#operation').click(function(){
    	window.location.href = jsonUrl + '/nigth_user/operationDownload';
    });

});

function Yz_Click(){
    var type = true;
    $('#yz').focus(function(){
        if(type){
            type = false;
            var nameVal = $('#username').val();
            if(!Boolean(nameVal)){

            }else{
                $('.YZ_img').empty();
                $('.YZ_img').append('<img src="'+jsonUrl+'/nigth_user/captcha?username='+nameVal+'&r='+Math.random()+'' + '" alt="" width="100%" height="100%"/>')
            }
        }

    });

    $('.form_group').on('click','img',function(){
        var nameVal = $('#username').val();
        if(!Boolean(nameVal)){

        }else{
            $(this).attr('src','../nigth_user/captcha?username='+nameVal+'&r='+Math.random()+'')
        }

    })

}




function login(){
    var type ;
    for(var i = 0 ; i <$('#form_box input').length;i++){
        if(!Boolean($('#form_box input').eq(i).val().trim())){
            type = false
        }
    }
    if(type == false){
        alert('请检查内容是否输入完整')
    }else{
        $('#form_box').submit();

        /*
        var data ={
            yzm:$('#yz').val().trim(),
            accout:$('#username').val().trim(),
            password:hex_md5($('#psw').val().trim())
        };
        $.ajax({
            url:jsonUrl+'/nigth_user/login',
            type:'post',
            dataType:'json',
            data:data,
            success:function(data){
                //$('#yz').val('');
                //$('#username').val('');
                //$('#psw').val('');
                if(data.status ==0){
                    window.location = '../nigth_user/login_success';
                }else{
                    alert(data.msg);
                    localStorage.removeItem("username")
                    $('.YZ_img img').attr('src',''+jsonUrl+'/nigth_user/captcha?username='+$('#username').val()+'&r='+Math.random()+'')
                }

            }
        })*/
    }

}

