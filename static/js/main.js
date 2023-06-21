function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');


$('.object-eval-btn').on('click', function (ev) {
    console.log(this.dataset.objectType, this.dataset.id, this.dataset.evalValue);

    if (this.dataset.objectType === 'question') {
        $.ajax({
            url: '/question_eval/',
            method: 'post',
            dataType: 'json',
            headers: {
                "X-CSRFToken": csrftoken,
            },
            data: {
                question_id: this.dataset.id,
                eval_value: this.dataset.evalValue,
            },
            success: function (response) {
                console.log('eval')
                $("#question-rating-" + response['question_id']).text(response['new_rating'])
            }
        });
    } else {
        $.ajax({
            url: '/answer_eval/',
            method: 'post',
            dataType: 'json',
            headers: {
                "X-CSRFToken": csrftoken,
            },
            data: {
                answer_id: this.dataset.id,
                eval_value: this.dataset.evalValue,
            },
            success: function (response) {
                console.log('eval')
                $("#answer-rating-" + response['answer_id']).text(response['new_rating'])
            }
        });
    }
})

$(".answer-mark-input").on("click", function (ev) {
    $.ajax({
        url: '/answer_is_right/',
        method: 'post',
        dataType: 'json',
        headers: {
            "X-CSRFToken": csrftoken,
        },
        data: {
            answer_id: this.dataset.id,
            is_checked: this.checked,
        },
        success: function (response) {
            if (response["is_checked"]) {
                $("#answer-" + response["answer_id"]).addClass("correct-answer")
            }
            else {
                $("#answer-" + response["answer_id"]).removeClass("correct-answer")
            }
        }
    });
})


