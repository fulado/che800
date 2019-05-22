var webroot=document.location.href;
webroot=webroot.substring(webroot.indexOf('//')+2,webroot.length);
webroot=webroot.substring(webroot.indexOf('/')+1,webroot.length);
webroot=webroot.substring(0,webroot.indexOf('/'));
var jsonUrl="/"+webroot ;

$(function(){
	toggleImg();
    num();
    // toggleClick();
    initWh();//初始化宽高
    resizeInitWh();//窗口改变宽高
    frameClick();//iframe切换
    closeBtn();
    userSetting();
    modalBtn();
});
//更换图片
function toggleImg(){
	var username = localStorage.getItem("username");
	var imgData = {
			username:username,
	}
	$.ajax({
		url:jsonUrl+'/nigth_user/header',
		type : 'get',
		data : imgData,
		dataType:'json',
		success:function(data){
			$('.text_icon_2').css({
				'background':'url("'+data.imgUrl+'") no-repeat',
				'background-size':'100%'
			})
		}
	});
}



function toggleClick(){

    $('.nav_bar').on('click','.main',function(){
        //箭头切换
        var type = $(this).find('.JT').hasClass('JT_active');
        if(!type){
            $(this).parents('.first').find('.JT').addClass('JT_active')
        }else{
            $(this).parents('.first').find('.JT').removeClass('JT_active')
        }
        //下拉菜单
        $(this).parent().find('.down_menu').stop().removeClass('active').slideToggle(300);
    });
    //子菜单切换样式
    $('.nav_bar').on('click','.down_menu',function(){
	    $(this).addClass('active').siblings('.down_menu').removeClass('active');
        $(this).addClass('active').parents('.first').siblings().children('.down_menu').removeClass('active');

    })
}

function initWh(){
    var content_W =document.body.clientWidth-200;
    var content_H =document.body.clientHeight-80;
    $('.content').width(content_W).height(content_H);
    $('.nav_bar').height(content_H)
}
function resizeInitWh(){
    $(window).resize(function(){
        initWh()
    })
}
function closeBtn(){
	$("#close_btn").click(function(){
		//window.location.href=jsonUrl + "/nigth_user/login_out";
		var username = localStorage.getItem("username");
		var data = {accout:username};
		$.ajax({
			url:jsonUrl+'/nigth_user/login_out',
			type : 'get',
			data : data,
			dataType:'json',
			success:function(data){
				localStorage.removeItem("username");
				window.location.href= data.url;
			}
		});
	})
}

//个人设置
function userSetting(){
	$('#user_setting').click(function(){

		var username = localStorage.getItem("username");
		$.ajax({
			url:jsonUrl+'/night_permission/before_edit',
			type : 'post',
			data : {username:username},
			dataType:'json',
			success:function(data){
				if(data.status == '0'){
					$('.mask').show();
					$('.pop-up').show();
					if(data.type == 'S'){
						$('.corporation').show()
						$('.pop-up').css('height','410')
						$('#wbjName').val(data.wbjName)
						$('#name').val(data.name);
						$('#password').val(data.password);
						$('#ucontect').val(data.ucontect);
						$('#utel').val(data.utel);
						$('#accout').val(data.accout);
					}else{
						$('.corporation').hide()
						$('.pop-up').css('height','370')
						$('#name').val(data.name);
						$('#password').val(data.password);
						$('#ucontect').val(data.ucontect);
						$('#utel').val(data.utel);
						$('#accout').val(data.accout);
					}

				}else{
					alert('设置失败')
				}
			}
		});



	})
}

function modalBtn(){
	$('#save').click(function(){
		var username = localStorage.getItem("username");
		if(!Boolean($('#accout').val()) || !Boolean($('#password').val())){
			alert('请输入账号密码')
		}
		else{
			$.ajax({
				url:jsonUrl+'/night_permission/edit',
				type : 'post',
				data : $.param({'username': username}) + '&' +$('#form_1').serialize(),
				dataType:'json',
				success:function(data){
					if(data.status == '0'){
						console.log(data)
						$('.mask').hide();
						$('.pop-up').hide();

					}else{
						alert(data.msg)
					}
				}
			});
		}
	})

	$('#del').click(function(){
		$('.mask').hide();
		$('.pop-up').hide();
	})

}





// 点击导航栏按钮, 打开相应页面
function frameClick(){
    $('.nav_bar').on('click','.down_menu',function () {
        var liUrl =$(this).attr('data-url');
        $('#content_iframe').attr('src',liUrl)
    });
}

//查询记录数
function num(){
	var username = localStorage.getItem("username");
	$.ajax({
		url:jsonUrl+'/nigth_auto/num?' + new Date().getTime(),
		type : 'get',
		data : {username:username},
		dataType:'json',
		success:function(data){
			if(data.type != 'COM'){

				$(".tooltip_text span").eq(1).text(data.coms);
				$(".tooltip_text span").eq(3).text(data.subCars);
				$('#user_setting').show();
			} else {
				$("span").remove(".number_word");
				$("span").remove(".number");
				$('#user_setting').hide();

			}
		}
	});
}

//初始化导航
function initNav(){
    var str='';
    var username = localStorage.getItem("username");
    $.ajax({
        url:jsonUrl+'/nigth_user/navigation?'+new Date().getTime(),
        type:'get',
        data : {username:username},
        dataType:'json',
        success:function(data){
            var evaldata = eval('('+data.navitions+')');
            $.each(evaldata,function(index,item){
                str +='<ul class="first">';
                str +='<li class="main" >'+item.text+'<span class="JT"></span></li>';
                if(item.isParent == 'Y'){
                    $.each(item.navigations,function(index,item1){
                        str += '<li class="down_menu" id="company_number'+item1.id+'" data-url=' +item1.url+'>'+item1.text+'</li>'
                    });
                }
                str += '</ul>'
            });
            $('.nav_bar').append(str);
            $('.down_menu').eq(0).trigger('click');
        }
    })
}


