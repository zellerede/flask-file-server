function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return undefined;
}
$(document).ready(function(){
    const path = location.pathname;

    $("#login").submit(function( event ) {
      var username = $( "#username" ).val();
      var auth = username && username+":"+$( "#password" ).val();
      var hash = $.base64.encode(auth);
      document.cookie = "username="+$("#username").val()+";path=/";
      document.cookie = "auth_cookie="+hash+";path=/";
      $("#userlogin").text($( "#username" ).val())
      $('#login-modal').modal('toggle');
      event.preventDefault();
    });
    $("#userlogin").text(getCookie("username") || "Login");
    $('#uploader-modal').on('hidden.bs.modal', function () {
        location.reload();
    })
    $('#filer_input').filer({
        showThumbs: true,
        addMore: true,
        templates: {
            box: '<ul class="jFiler-items-list jFiler-items-default"></ul>',
            item: '<li class="jFiler-item"><div class="jFiler-item-container"><div class="jFiler-item-inner"><div class="jFiler-item-icon pull-left">{{fi-icon}}</div><div class="jFiler-item-info pull-left"><div class="jFiler-item-title" title="{{fi-name}}">{{fi-name | limitTo:30}}</div><div class="jFiler-item-others"><span>size: {{fi-size2}}</span><span>type: {{fi-extension}}</span><span class="jFiler-item-status">{{fi-progressBar}}</span></div></div></div></div></li>',
            itemAppend: '<li class="jFiler-item"><div class="jFiler-item-container"><div class="jFiler-item-inner"><div class="jFiler-item-icon pull-left">{{fi-icon}}</div><div class="jFiler-item-info pull-left"><div class="jFiler-item-title">{{fi-name | limitTo:35}}</div><div class="jFiler-item-others"><span>size: {{fi-size2}}</span><span>type: {{fi-extension}}</span><span class="jFiler-item-status"></span></div></div></div></div></li>',
            progressBar: '<div class="bar"></div>',
            itemAppendToEnd: false,
            removeConfirmation: true,
            canvasImage: true,
            _selectors: {
                list: '.jFiler-items-list',
                item: '.jFiler-item',
                progressBar: '.bar',
                remove: '.jFiler-item-trash-action'
            }
        },
        uploadFile: {
            url: "#",  //  TODO: customize url
            data: {},
            type: 'POST',
            enctype: 'multipart/form-data',
            beforeSend: function(){},
            success: function(data, el){
                var parent = el.find(".jFiler-jProgressBar").parent();
                data = JSON.parse(data)
                if (data.status == 'success') {
                    el.find(".jFiler-jProgressBar").fadeOut("slow", function(){
                        $("<div class=\"jFiler-item-others text-success\"><i class=\"icon-jfi-check-circle\"></i> Success</div>").hide().appendTo(parent).fadeIn("slow");
                    });
                } else {
                    el.find(".jFiler-jProgressBar").fadeOut("slow", function(){
                        $("<div class=\"jFiler-item-others text-error\"><i class=\"icon-jfi-minus-circle\"></i> Error: " + data.msg + "</div>").hide().appendTo(parent).fadeIn("slow");
                    });
                }
            },
            error: function(el,i,g,h,e,d,jqxhr,c,f){
                data = JSON.parse(jqxhr.responseText)
                var parent = el.find(".jFiler-jProgressBar").parent();
                el.find(".jFiler-jProgressBar").fadeOut("slow", function(){
                    $("<div class=\"jFiler-item-others text-error\"><i class=\"icon-jfi-minus-circle\"></i> Error: " + data.msg + "</div>").hide().appendTo(parent).fadeIn("slow");
                });
            },
            statusCode: null,
            onProgress: null,
            onComplete: null
        },
        captions: {
            button: "Add Files",
            feedback: "Choose files To Upload",
            feedback2: "files were chosen",
            drop: "Drop file here to Upload",
            removeConfirmation: "Are you sure you want to remove this file?",
            errors: {
                filesLimit: "Only {{fi-limit}} files are allowed to be uploaded.",
                filesType: "Only Images are allowed to be uploaded.",
                filesSize: "{{fi-name}} is too large! Please upload file up to {{fi-fileMaxSize}} MB.",
                filesSizeAll: "Files you've choosed are too large! Please upload files up to {{fi-maxSize}} MB.",
                folderUpload: "You are not allowed to upload folders."
            }
        }
    });
    $('#close-uploader').click(function() {
        $('#filer_input').prop("jFiler").reset();
    });
    
    // Generic modal for asking a path
    var modal = {main: $('#askpath-modal'), form: $('#modal-form')};
    var onSubmitModal = function(event) {
        event.preventDefault();
        modal.input = $('#modal-input').val();
        modal.main.modal('hide'); // .removeClass('show')
        modal.submit(event);
    }
    modal.form.submit(onSubmitModal);
    $('#submit-modal').on('click', onSubmitModal);

    var submitCreateFolder = function() {
        var newUrl = modal.input;
        $.post(newUrl, '', function() {
            location.replace(newUrl);
        });
    };
    $('#createfolder-button').on('click', function() {
        $('#modal-text').html('Enter name of folder to be created:');
        var placeholder = 'Type ' + ((path && path!=='/') ? 'relative or ' : '') + 'full folder path to create';
        $('#modal-input').attr('name', 'folderName').attr('value', '')
            .attr('placeholder', placeholder);
        $('#submit-modal').html('Create');
        modal.submit = submitCreateFolder;
    });

    var chosenRow = null;
    var contextMenu = $("#context-menu");
    $('.jumbotron').on('contextmenu', function(e) {
        var top = e.pageY - 10;
        var left = e.pageX - 90;
        contextMenu.css({
            display: "block",
            top: top,
            left: left
        }).addClass("show");
        chosenRow = $(this).attr('name');
        return false; // blocks default Webbrowser right click menu
    });
    
    $("#context-menu a").on("click", function() {
        contextMenu.removeClass("show").hide();
    });

    var submitCopy = function() {
        $.post('/api/v1/copy' + path + chosenRow + '?to=' + modal.input, '',
            function() { location.reload(); });
    };
    $("#copy").on("click", function() {
        $('#modal-text').html('Enter full target path:');
        $('#modal-input').attr('name', 'target').attr('value', path + chosenRow);
        $('#submit-modal').html('Copy');
        modal.submit = submitCopy;
    });

    var submitMove = function() {
        $.post('/api/v1/move' + path + chosenRow + '?to=' + modal.input, '',
            function() { location.reload(); });
    };
    $("#move").on("click", function() {
        $('#modal-text').html('Enter full target path:');
        $('#modal-input').attr('name', 'target').attr('value', path + chosenRow);
        $('#submit-modal').html('Move');
        modal.submit = submitMove;
    });

    $("#delete").on("click", function() {
        // TODO: modal for 'are you sure?'
        $.ajax({
            url: chosenRow,
            type: 'DELETE',
            success: function() {
                location.reload();
            }
        });
    });

    document.body.addEventListener('click', function(event) {
        if (contextMenu.attr('class').split(/\s+/).includes('show')) {
            contextMenu.removeClass("show").hide();
            event.preventDefault();
        }
    }, false);
});
