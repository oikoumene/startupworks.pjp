// Foundation JavaScript
// Documentation can be found at: http://foundation.zurb.com/docs
$(document).foundation();

Pace.on('hide', function(){
	var loader = $('.loading-overlay');
	console.log('knickers');
	if($('html').hasClass('cssanimations')){
		loader.addClass('animated fadeOut');
		setTimeout(function(){loader.hide();}, 1000);
	} else {
		loader.hide();
	}
});

