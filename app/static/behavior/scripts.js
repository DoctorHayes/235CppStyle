$(function() {
	"use strict";
	var spinnerEl = $("#spinner")[0];
	var spinner = new Spinner({radius: 30, length: 30});

	function updateForm() {
		if ($('#code-input').val() !== undefined && $('#code-input').val() !== '') {
			$('#upload-file-btn').removeAttr("disabled");
		} else {
			$('#upload-file-btn').attr("disabled", '');
		}

		$(':checkbox:checked').prop('checked',false);
	}

	$('.code-submission').click(function(){
		closeFeedback();
	});

	function showSpinner() {
		spinner.spin(spinnerEl);
	}

	function hideSpinner() {
		spinner.stop();
	}

	function closeFeedback() {
		var ul = document.getElementById("errorlist2");
		var items = ul.getElementsByTagName("li");
		var itemLength = items.length;
		// clearFileInput();

		while(items.length) {
			items[0].remove();
		}
	}

	function clearFileInput() {
		$('#code-input').fileinput('reset');
		$('#code-input').val('');
		$('#upload-file-btn').attr("disabled", "disabled");
		$('#errorlist2').empty();
	}

	$('input[type=file]').fileinput(
		{	showCaption: true,
			showPreview: false,
			showUpload: false,
			required: true,
			allowedFileExtensions: ['cpp', 'h', 'cc', 'c'],
			browseLabel: "Select files …"}
	);

	// hide navigation if not logged in
	if (window.location.href.indexOf('login') > -1) {
		$('.navigation').hide();
	}


	$('.closeBtn').on("click", function() {
		$debugButton = $(".debugButton");
		$debugButton.css('outline', 0);
		closeFeedback();

	});

	$('#agreementCheck').change(function() {
		if(this.checked) {
			$('#agreementDiv').removeClass('has-error has-danger');
		}
		else
		{
			$('#agreementDiv').addClass('has-error has-danger');
		}
	});

	$('#code-input').on("change", function(){
		updateForm();
	});

	$('#upload-file-btn').click(function() {
		var checkbox = $('#agreementCheck');
		if (!checkbox.is(':checked'))
		{
			//checkbox.addClass('is-invalid');
			$('#agreementDiv').addClass('has-error has-danger');
			return;
		}

		showSpinner();
		var form_data = new FormData($('#upload-file')[0]);

		$.ajax({
			type: 'POST',
			url: '/uploadajax',
			data: form_data,
			contentType: false,
			cache: false,
			processData: false,
			async: true,
			error: function() {
				console.log('Failure!');
			},
			success: function(data) {
				console.log('Success!');

				for(var i in data.files) {
					var file = data.files[i];
					var panelEl = $("<div>", {id: "card" + i, "class": "panel panel-default"});
					panelEl.append('<div class="panel-heading">Analyzing&nbsp; ' + file.filename + ' &hellip;</div>');
					if (file.errors.length === 0) {
						panelEl.addClass('panel-success');
						panelEl.append("<div class='panel-body'>No errors have been found! :)</div>");
					}
					else {
						panelEl.addClass('panel-danger');
						var tableCode = '<table class="table table-borderless"><thead></thead>';
						for (var errorIter in file.errors) {
							var error = file.errors[errorIter];
							tableCode += '<tr><td>' +
								error.location + '</td><td><code>' + error.message +
								"</code></td></tr>";
						}
						tableCode += '</table>';
						panelEl.append(tableCode);

					}
					$("#errorlist2").append(panelEl);
				}

				$('#errorblock').show();
				hideSpinner();
			},
		});
		clearFileInput();
	});
});


