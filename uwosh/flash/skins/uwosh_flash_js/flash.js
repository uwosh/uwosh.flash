var OLD_FLASH_IMAGE = "++resource++flash.png";
var FLASH_IMAGE = "flashimage";
var FLOWPLAYER_SWF = 'flowplayer-3.2.1.swf';
var FLOWPLAYER_CONTROLS_SWF = 'flowplayer.controls-3.2.0.swf';
var FLOWPLAYER_RTMP_SWF = 'flowplayer.rtmp-3.2.0.swf';
var FLOWPLAYER_AUDIO_SWF = 'flowplayer.audio-3.2.0.swf';

function URLDecode(url){
    if(url.indexOf("?") > -1){
        url = url.split("?")[1];
    }
    
    var HEXCHARS = "0123456789ABCDEFabcdef";
    var encoded = url;
    var plaintext = "";
    var i = 0;
    while (i < encoded.length) {
        var ch = encoded.charAt(i);
        if (ch == "+") {
            plaintext += " ";
            i++;
        } else if (ch == "%") {
            if (i < (encoded.length-2) && HEXCHARS.indexOf(encoded.charAt(i+1)) != -1 && HEXCHARS.indexOf(encoded.charAt(i+2)) != -1 ) {
                plaintext += unescape( encoded.substr(i,3) );
                i += 3;
            } else {
                //alert( 'Bad escape combination near ...' + encoded.substr(i) );
                plaintext += "%[ERROR]";
                i++;
            }
        } else {
            plaintext += ch;
            i++;
        }
    }
    try{
        var res = {};
        var items = plaintext.split("&");
    
        for(var i = 0; i < items.length; i++){
            var temp = items[i].split("=");
            var key = temp[0];
            var value = temp[1];
            res[key] = value;
        }
    
        return res;
    }catch(err){
        return {};
    }
};

function join(url, path){
    /*
    joins a base url and a path together.
    http://www.test.com/blah, 'somethingelse.swf' -> http://www.test.com/blah/somethingelse.swf
    http://www.test.com/test, test/something.swf -> http://www.test.com/test/something.swf
    */
    
    var spliturl = url.split('/');
    var splitpath = path.split('/');
    if(spliturl[spliturl.length-1] == splitpath[0]){
        spliturl.pop();
    }
    
    url = spliturl.join('/');
    path = splitpath.join('/');
    
    if(url.substring(url.length-1) == '/'){
        url = url.substring(0, url.length-1);
    }
    if(path.substring(0, 1) == '/'){
        path = path.substring(1, path.length);
    }
    return url + '/' + path;
}

function replace_ele(ele, other){
    if(ele.parent()[0].tagName == 'P'){
        ele.parent().after(other);
        ele.remove();
    }else{
        ele.replaceWith(other);
    }
}

jq(document).ready(function(){
    
    var image_button = jq("#toolbar #kupu-tb-buttons .kupu-tb-buttongroup #kupu-imagelibdrawer-button");
    var base_url = jq('base').attr('href');
    
    FLOWPLAYER_SWF = join(base_url, FLOWPLAYER_SWF);
    FLOWPLAYER_CONTROLS_SWF = join(base_url, FLOWPLAYER_CONTROLS_SWF);
    FLOWPLAYER_RTMP_SWF = join(base_url, FLOWPLAYER_RTMP_SWF);
    FLOWPLAYER_AUDIO_SWF = join(base_url, FLOWPLAYER_AUDIO_SWF);
    
    if(image_button.size() > 0){
        image_button.attr('title', 'Insert an image or flash content (flv or swf)');
    }
    
    jq('img.flashElement').each(function(){
        var imgele = jq(this);
        
        var flash_image = imgele.attr('src');
        var flash_url = '';
        
        //provide backward compat for this
        //since there might be old images in kupu yet
        if(flash_image.indexOf(OLD_FLASH_IMAGE) > -1){
            flash_url = flash_image.substring(0, flash_image.indexOf(OLD_FLASH_IMAGE));
        }else{
            flash_url = flash_image.substring(0, flash_image.indexOf(FLASH_IMAGE));
        }
        
        var options = URLDecode(flash_image);
        var width = imgele.width();
        var height = imgele.height();
        
        if(width < 50){
            if(options.width == undefined){
                width = 400;
            }else{
                width = options.width;
            }
        }
        if(height < 50){
            if(options.height == undefined){
                height = 300;
            }else{
                height = options.height;
            }
        }
        
        imgele.removeClass('flashElement');
        var extra_classes = imgele[0].className;
        
        var new_id = "flash" + options.id.replace(".", "-");
        while(jq("#" + new_id).size() > 0){//in case id already exists.
            new_id = new_id + "1";
        }
        var flowoptions = {
            plugins: {
                controls:{
                    url : FLOWPLAYER_CONTROLS_SWF
                }
            },
            clip: { 
                autoPlay : false
            }
        }
        
        if(options.flv_url != undefined){
            options.media_url = options.flv_url;
        }
        if(options.file_type == undefined){
            if(options.filename != undefined){
                fi = options.filename;
                options.file_type = fi.substring(fi.lastIndexOf('.')+1, fi.length+1);
            }else{
                options.file_type = 'flv';
            }
        }
        
        if(options.show_splash_frame == undefined || options.show_splash_frame == 'false'){
            options.show_splash_frame = false;
        }else{
            options.show_splash_frame = true;
        }
        
        if(options.media_url != undefined){
            
            if(!flashembed.isSupported([6,65])){
                //check if flash is supported and just show the image if it is not
                imgele.show();
            }else if(options.media_url != '0' && options.media_url != 0){
                //check if it is a streaming flv
                var flv = jq('<div class="player ' + extra_classes + '" id="' + new_id +
                             '" style="width:' + width + 'px; height:' + height + 'px" ></div>');
                             
                replace_ele(imgele, flv);
                            
                flowoptions['plugins']['rtmp'] = {
                    url : FLOWPLAYER_RTMP_SWF,
                    netConnectionUrl : options.streaming_url
                };
                flowoptions['clip']['url'] = options.media_url;
                flowoptions['clip']['provider'] = 'rtmp';
                
                if(options.file_type == 'mp3'){
                    flowoptions['plugins']['rtmp']['durationFunc'] = 'getStreamLength';
                    flowoptions['plugins']['controls'] = { fullscreen: false, height: 30 };
                    flv.css('height', '30px');
                }else if(options.show_splash_frame){
                    //This is so the first frame of the video shows up...
                    flowoptions.clip.autoPlay = true;
                    flowoptions.clip.start = 0.75;
                    flowoptions.clip.onCuepoint = [[1], function() { this.pause(); this.seek(1)}];
                    flowoptions.clip.autoBuffering = true;
                }
                
                flv.flowplayer(FLOWPLAYER_SWF, flowoptions);
            
            //insert flash element
            }else if(options.file_type == 'swf'){
                imgele.wrap("<div class='" + extra_classes + "' id='" + new_id + 
                            "' style='width:" + width + "px;height:" + height + "px' ></div>");
                imgele = imgele.parent();

                var swf_full_url = join(flash_url, "download.swf");
            
                var html = 
                	'<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" ' + 
    					'codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=6,0,40,0" ' +
    					'width="' + width + '" height="' + height + '" ' + 
     					'id="' + options.id + '"> ' +
    					'<param name="movie" value="' + swf_full_url + '" /> ' +
    					'<param name="quality" value="high" /> ' +
    					'<param name="bgcolor" value="#ffffff" /> ' +
    					'<param name="wmode" value="opaque" />' +
    					'<embed src="' + swf_full_url + '" quality="high" bgcolor="#ffffff" ' + 
    						'width="' + width + '" height="' + height + '" wmode="opaque"' +
    						'name="' + options.id + '" align="" type="application/x-shockwave-flash" ' + 
    						'pluginspage="http://www.macromedia.com/go/getflashplayer"> ' +
    					'</embed> ' +
    				'</object> ';
            
            	imgele.html(html);
            	
            // add flv normal way without streaming....
            // keep check on '.flv' for legacy support
            }else if(options.file_type == 'flv'){
                var swf_full_url = join(flash_url, "download.swf");
                var flv = jq("<div class='player " + extra_classes + "' id='" + new_id + 
                    "' style='width:" + width + "px; height:" + height + "px' href='" + swf_full_url + "'></div>");
                replace_ele(imgele, flv);
                flv.flowplayer(FLOWPLAYER_SWF, { clip: { autoPlay : false } });
            }else if(options.file_type == 'mp3'){
                var mp3_full_url = join(flash_url, "download.mp3");
                var mp3 = jq('<div class="player ' + extra_classes + '" id="' + new_id + 
                            '" style="width:' + width + 'px; height: 30px"></div>');
                            
                replace_ele(imgele, mp3);
            
                mp3.flowplayer(new_id, FLOWPLAYER_SWF, {
                    clip: {
                        autoPlay : false
                    },
                    plugins : {
                        controls : {
                            url : FLOWPLAYER_CONTROLS_SWF,
                            height : 30,
                            fullscreen : false
                        },
                        audio : {
                            url : FLOWPLAYER_AUDIO_SWF
                        }
                    },
                    playlist : [
                        mp3_full_url
                    ]
                });
            }
        }
    });
});
