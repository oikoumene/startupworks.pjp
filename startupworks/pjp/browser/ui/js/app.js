// Foundation JavaScript
// Documentation can be found at: http://foundation.zurb.com/docs
$(document).foundation();

// var menu = jQuery('.left-off-canvas-menu');
// var navList = jQuery('.side-nav-list');
// var docHeight = jQuery(document).height();
// var winHeight = jQuery(window).height();

// jQuery(document).on('resize', function() {
//   menu.height(jQuery(this).height());
//   //navList.height(winHeight);
// });

// // Initialize height
// jQuery(document).trigger('resize');

jQuery(function($){

	// cookie for nav notice
	if(!$.cookie('navtip')){
		var navnotice = $('.nav-notice');
		var socmednotice = $('.socmed-notice');

		navnotice.removeClass('nn-hidden');
		navnotice.addClass('animated fadeInLeft');
		setTimeout(function(){navnotice.toggleClass('fadeInLeft fadeOut');}, 4000);

		socmednotice.removeClass('nn-hidden');
		socmednotice.addClass('animated fadeInLeft');
		setTimeout(function(){socmednotice.toggleClass('fadeInLeft fadeOut');}, 4000);

		// set the cookie - uncomment below if want to use cookie
		// $.cookie('navtip', true);
	}

	//lightbox script
	$('.video-links').fancybox({});

});

jQuery(window).load(function(){

	ROOT_API_URL = $('[data-root-api-url]').attr('data-root-api-url');

	function prepareVotables() {
		$('[data-votable]').each(function(index, element) {
			var votable = $(this);
			var votableId = votable.attr('data-votable');

			votable.unbind('click');
			votable.click(function() {
				var votableCountElement = $('[data-votes-count="' + votableId + '"]');
				votableCountElement.fadeOut(function() {
					$(this).html((parseInt($(this).html()) + 1) + '').fadeIn();
				})
				var request = $.ajax({
					url: ROOT_API_URL + 'api+upvote/',
					type: 'POST',
					dataType: 'json',
					data: {
						id: votableId
					}
				});
			});
		});
	}

	prepareVotables();

	$('.link-top').click(function(){
		$('html, body').animate({scrollTop : 0},800);
		return false;
	});

	$('.see-more-videos').on('click', function(e){
		e.preventDefault();
		var thisList = $(this);
		var nextPage = thisList.attr('data-videos-pagination-next-page');
		var id = thisList.attr('data-id');

		$.ajax({
			url: ROOT_API_URL + 'api+resources+videos/',
			type: 'POST',
			dataType: 'json',
			data: {
				id: id,
				page: nextPage
			}
		})
		.done(function(result) {
			thisList.parent().children('ul').append(result.html);
			if (result.next_page == '') {
				thisList.remove();
			} else {
				thisList.attr('data-videos-pagination-next-page', result.next_page);
			}
			prepareVotables();
		})
		.fail(function() {
			console.log('error');
		})
		.always(function() {
			console.log('complete');
		});
	});

	$('.see-more-sounds').on('click', function(e){
		e.preventDefault();
		var thisList = $(this);
		var nextPage = thisList.attr('data-sounds-pagination-next-page');
		var id = thisList.attr('data-id');

		$.ajax({
			url: ROOT_API_URL + 'api+resources+sounds/',
			type: 'POST',
			dataType: 'json',
			data: {
				id: id,
				page: nextPage
			}
		})
		.done(function(result) {
			thisList.parent().children('ul').append(result.html);
			if (result.next_page == '') {
				thisList.remove();
			} else {
				thisList.attr('data-sounds-pagination-next-page', result.next_page);
			}
			prepareVotables();
		})
		.fail(function() {
			console.log("error");
		})
		.always(function() {
			console.log("complete");
		});
	});

	$('.see-more-documents').on('click', function(e){
		e.preventDefault();
		var thisList = $(this);
		var nextPage = thisList.attr('data-documents-pagination-next-page');
		var id = thisList.attr('data-id');

		$.ajax({
			url: ROOT_API_URL + 'api+resources+documents/',
			type: 'POST',
			dataType: 'json',
			data: {
				id: id,
				page: nextPage
			}
		})
		.done(function(result) {
			thisList.parent().children('ul').append(result.html);
			if (result.next_page == '') {
				thisList.remove();
			} else {
				thisList.attr('data-documents-pagination-next-page', result.next_page);
			}
			prepareVotables();
		})
		.fail(function() {
			console.log("error");
		})
		.always(function() {
			console.log("complete");
		});
	});

	function readResource(input) {
		if (input.files && input.files[0]) {
			var fr = new FileReader();
			fr.onload = function(e) {
				 var binaryString = e.target.result;
				 alert(binaryString);
			};
			fr.readAsDataURL(input.files[0]);
		}
	}

	var addResourceForm = $('.add-resource-form');
	var docFile = {};
	var docField = addResourceForm.find('[data-id="document"]');
	docField.val('');
	docField.change(function(e) {
		if (this.files && this.files[0]) {
			var f = this.files[0];
			var fr = new FileReader();
			fr.onload = function(e) {
				docFile.filename = f.name;
				docFile.data = e.target.result;
			};
			fr.readAsDataURL(f);
		}
	});

	var addResourceFormButton = addResourceForm.find('.button');
	addResourceFormButton.on('click', function(e){
		var id = addResourceForm.attr('data-id');
		var name = addResourceForm.find('[data-id="name"]').val();
		var email = addResourceForm.find('[data-id="email"]').val();
		var church = addResourceForm.find('[data-id="church"]').val();
		var video = addResourceForm.find('[data-id="video"]').val();
		var audio = addResourceForm.find('[data-id="audio"]').val();
		var message = addResourceForm.find('[data-id="message"]').val();

		var warning = addResourceForm.find('[data-warning]');
		warning.html('');
		warning.removeClass('data-warning-active');
		var successMessage = $('[data-success-message]');
		successMessage.html('');
		successMessage.removeClass('data-success-message-active');

		addResourceFormButton.html('Uploading...');

		$.ajax({
			url: ROOT_API_URL + 'api+resources+add/',
			type: 'POST',
			dataType: 'json',
			data: {
				id: id,
				name: name,
				email: email,
				church: church,
				video: video,
				sound: audio,
				docName: docFile.filename,
				docData: docFile.data,
				message: message
			}
		})
		.done(function(result) {
			addResourceFormButton.html('Done!');
			successMessage.addClass('data-success-message-active');
			successMessage.html(result.mssg);
			addResourceFormButton.unbind('click');
			addResourceFormButton.css({'cursor': 'default'});
			addResourceForm.slideUp();
			$('html, body').animate({
				scrollTop: $('.add-resource-strip').offset().top
			}, 1000);
		})
		.fail(function(xhr) {
			var result = xhr.responseJSON;
			warning.addClass('data-warning-active');
			warning.html(result.mssg);
			addResourceFormButton.html('Submit');
		})
		.always(function() {
			console.log("complete");
		});
	});

	$('.load-more-comments').on('click', function(e){
		e.preventDefault();
		var thisList = $(this);
		var nextPage = thisList.attr('data-comments-pagination-next-page');
		var id = thisList.attr('data-id');

		$.ajax({
			url: ROOT_API_URL + 'api+comments/',
			type: 'POST',
			dataType: 'json',
			data: {
				id: id,
				page: nextPage
			}
		})
		.done(function(result) {
			thisList.parent().children('ul').append(result.html);
			if (result.next_page == '') {
				thisList.remove();
			} else {
				thisList.attr('data-comments-pagination-next-page', result.next_page);
			}
			prepareVotables();
		})
		.fail(function() {
			console.log("error");
		})
		.always(function() {
			console.log("complete");
		});
	});

	var addCommentButton = $('.action-button.add-comment');
	var addCommentForm = $('.add-comment-form');
	var imageFile = {};
	var imageField = addCommentForm.find('[data-id="image"]');
	imageField.val('');
	imageField.change(function(e) {
		if (this.files && this.files[0]) {
			var f = this.files[0];
			var fr = new FileReader();
			fr.onload = function(e) {
				imageFile.filename = f.name;
				imageFile.data = e.target.result;
			};
			fr.readAsDataURL(f);
		}
	});

	addCommentForm.hide();
	addCommentButton.on('click', function(e){
		e.preventDefault();
		addCommentForm.addClass('show-comment-form');
		addCommentForm.show();
	});

	var addCommentFormButton = addCommentForm.find('.button');
	addCommentFormButton.on('click', function(e){
		var id = addCommentForm.attr('data-id');
		var name = addCommentForm.find('[data-id="name"]').val();
		var email = addCommentForm.find('[data-id="email"]').val();
		var message = addCommentForm.find('[data-id="message"]').val();

		var warning = addCommentForm.find('[data-warning]');
		warning.html('');
		warning.removeClass('data-warning-active');
		var successMessage = addCommentForm.find('[data-success-message]');
		successMessage.html('');
		successMessage.removeClass('data-success-message-active');

		addCommentFormButton.html('Saving...');

		$.ajax({
			url: ROOT_API_URL + 'api+comments+add/',
			type: 'POST',
			dataType: 'json',
			data: {
				id: id,
				name: name,
				email: email,
				imageName: imageFile.filename,
				imageData: imageFile.data,
				message: message
			}
		})
		.done(function(result) {
			addCommentFormButton.html('Done');
			successMessage.addClass('data-success-message-active');
			successMessage.html(result.mssg);
			addCommentFormButton.unbind('click');
			addCommentFormButton.css({'cursor': 'default'});
			addCommentForm.find('form').slideUp();
			$('html, body').animate({
				scrollTop: $('.add-comment-form').offset().top
			}, 1000);
		})
		.fail(function(xhr) {
			var result = xhr.responseJSON;
			warning.addClass('data-warning-active');
			warning.html(result.mssg);
			addCommentFormButton.html('Submit');
		})
		.always(function() {
			console.log("complete");
		});
	});


	$('.big-circle-slider').slick({
		dots: false,
		infinite: true,
		centerMode: true,
		slidesToShow: 3,
		asNavFor: '.little-circle-slider',
		responsive: [
			{
				breakpoint: 640,
				settings: {
					slidesToShow: 1,
					centerMode: false
				}
			}
		]
	});

	$('.little-circle-slider').slick({
		dots: false,
		infinite: true,
		slidesToShow: 6,
		asNavFor: '.big-circle-slider'
	});

	$('.sound-link').fancybox({
		helpers : {
			media : {}
		}
	});


	// Show and hide extra slider
	var cover = $('.small-slider-cover');
	var coverButton = $('.more-circles');

	coverButton.on('click', function(e){
		e.preventDefault();
		if(cover.hasClass('open-cover')) {
			cover.removeClass('open-cover');
			coverButton.text("Show More");
		} else {
			cover.addClass('open-cover');
			coverButton.text("Show Less");
		}
	});

});

Pace.on('hide', function(){
	var loader = $('.loading-overlay');
	if($('html').hasClass('cssanimations')){
		loader.addClass('animated fadeOut');
		setTimeout(function(){loader.hide();}, 1000);
	} else {
		loader.hide();
	}
});