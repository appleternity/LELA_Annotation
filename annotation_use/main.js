$(document).ready(function() {
    var update_num = function(panel_id) {
        console.log("#"+panel_id+" .selected");
        var length = $("#"+panel_id+" .selected").length;
        $("#"+panel_id+" .num").text( "( "+length+" )" );
    };

    $(document).on("click", ".not_selected", function(evt) {
        var target;
        if (!$(evt.target).hasClass("sentence")) {
            target = $(evt.target).parents(".sentence");
        } else {
            target = $(evt.target);
        }

        target.removeClass("not_selected").addClass("selected");
        update_num(target.parents(".sentence_panel").attr("id"));
    });
    $(document).on("click", ".selected", function(evt) {
        var target;
        if (!$(evt.target).hasClass("sentence")) {
            target = $(evt.target).parents(".sentence");
        } else {
            target = $(evt.target);
        }
        target.removeClass("selected").addClass("not_selected");
        update_num(target.parents(".sentence_panel").attr("id"));
    });

    $(document).on("click", "#reason_table .dropdown-item", function(evt) {
        var target = $(evt.target);
        var button = target.parents(".btn-group").children("button").text(target.text());
        button.removeClass("btn-danger").addClass("btn-info");
    });

    $(document).on("change", "#reason_table input[type='checkbox']", function(evt) {
        var target = $(evt.target);
        if (this.checked) {
            target.parents("tr").find("button").removeClass("btn-danger btn-info").addClass("btn-secondary").attr("disabled", true).text("Select a Condition");
            
            // Add information to the stage 3
            var sent_id = target.parents("tr").attr("sent_id");
            $("#"+sent_id).addClass("accept");

        } else { 
            target.parents("tr").find("button").removeClass("btn-secondary").addClass("btn-danger").attr("disabled", false);
            
            // Add information to the stage 3
            var sent_id = target.parents("tr").attr("sent_id");
            $("#"+sent_id).removeClass("accept");
        }
    });

    $(document).on("click", "#submit_btn", function(evt) {
        $("#warning").text("");

        // check number of "selected" answers
        var w1_answers = $("#sentence_panel_1 .selected");
        var w2_answers = $("#sentence_panel_2 .selected");

        if (w1_answers.length < 3 || w2_answers.length < 3) {
            $("#warning").text("Please select at least 3 sentences.");
            return false;
        }

        var answer = {
            "w1": $.map(w1_answers, function(e, index) {return $(e).attr("id")}),
            "w2": $.map(w2_answers, function(e, index) {return $(e).attr("id")}),
        };

        $("#answer").val(JSON.stringify(answer));

        $("#mturk_form").submit();
    });

    $(document).on("click", "#go_guideline_btn", function(evt) {
        $("#second_stage").hide();
        $("#second_instruction").show();
        $("#next_btn").attr("stage", "2");
        $(document).scrollTop(0);
    });

    $(document).on("click", "#next_btn", function(evt) {
        var stage = parseInt($(evt.target).attr("stage"));
        $("#warning").text("");

        // Stage 1
        if (stage == 1) {
            // check number of answers
            var answers = $("#question_table .form-radio:checked");
            if (answers.length != 20) {
                $("#warning").text("Please finish all the questions! ("+ (20 - answers.length) +" left)");
                return;
            }

            // change to stage 2
            var text_answer = JSON.stringify($.map(answers, function(e) { e = $(e); return {"id":e.attr("name"), "ans":e.val()} }));
            $("#fib_answer").val(text_answer);
            $("#first_stage").hide();
            $("#second_instruction").show();
            $("#next_btn").attr("stage", "2");
            $(document).scrollTop(0);

        // Stage 2 - instruction (guideline)
        } else if (stage == 2) {
            // TODO: Time Lock?
            $("#second_instruction").hide();
            $("#second_stage").show();
            $("#next_btn").attr("stage", "3");
            $(document).scrollTop(0);

        // Stage 2 (3)
        } else if (stage == 3) {
            // check number of answers
            var id_list = $.map($("#reason_table tbody tr"), function(e, index) {return $(e).attr("sent_id");});
            var check_list = $.map($("#reason_table input[type='checkbox']"), function(e, index) {return e.checked;});
            var reason_list = $.map($("#reason_table button"), function(e, index) {return $(e).text().trim();});
            console.log(id_list, check_list, reason_list);

            var answer = [];
            for (var i = 0; i < id_list.length; i++) {
                if (check_list[i] == false && reason_list[i] == "Select a Condition") {
                    $("#warning").text("Please finish all the questions!");
                    return;
                }
                answer.push({
                    "id": id_list[i],
                    "accept": check_list[i],
                    "reason": reason_list[i],
                });
            }

            // change to stage 3
            $("#reason_answer").val(JSON.stringify(answer));
            $("#second_stage").hide();
            $("#third_stage").css("display", "flex");
            $("#next_btn").hide();
            $("#submit_btn").show();
            $(document).scrollTop(0);
        }
    });


});

var temp;
