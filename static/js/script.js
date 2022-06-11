$(document).ready(function(){

// Tweet delete AJAX with button
var deleteBtn = $('.tweet-delete-btn', "[data-index='{{tweet.id}}']")
deleteBtn.click(function(e){
  var tweetId = $(this).data('index');
  $.ajax({
    url: "{% url 'tweets:delete' id=tweet.id %}",
    type: "POST",
    data: {
      'id': '{{tweet.id}}',
      'csrfmiddlewaretoken': '{{csrf_token}}'
    },
    success: function(json){
      $(".tweet-item[data-index='" + tweetId + "']").remove();
      var tweetCount = $("#tweet_count");
      tweetCount.text(json.tweet_count + 'tweets');
    },
    error: function(err){}
  })
})

// LIKE AJAX ATTEMPT WITH BUTTON ONCLICK
var likeBtn = $('.like-btn', "[data-index='{{tweet.id}}']")
likeBtn.click(function(){
var tweetId = $(this).data('index');
$.ajax({
  url: "{% url 'tweets:like-unlike' id=tweet.id %}",
  type: "POST",
  data: {
    'id': '{{tweet.id}}',
    'csrfmiddlewaretoken': "{{csrf_token}}"
  },
  dataType: 'json',
  success: function(json){
    document.getElementById('likeCounter{{tweet.id}}').innerHTML = json.likes_count;
    if (json.liked){
      document.getElementById('heart-box{{tweet.id}}').innerHTML = "<i class='fa fa-heart'></i>"
    }else if(json.unliked){
      document.getElementById('heart-box{{tweet.id}}').innerHTML = "<i class='fa fa-heart-o'></i>"
    }
  },
  error: function(errmsg){
    console.log(errmsg)
  }
})
})

// retweet AJAX
var retweetBtn = $('.retweet-btn', "[data-index='{{tweet.id}}']")
retweetBtn.click(function(){
var tweetId = $(this).data('index');
$.ajax({
  url: "{% url 'tweets:retweet' id=tweet.id %}",
  type: "POST",
  data: {
    'id': '{{tweet.id}}',
    'csrfmiddlewaretoken': "{{csrf_token}}"
  },
  success: function(json){
    document.getElementById('retweet-count{{tweet.id}}').innerHTML = json.retweet_count;
    if(json.created){
      document.getElementById('retweet-check{{tweet.id}}').innerHTML = "<i class='fa fa-check'></i>"
    }else{
      document.getElementById('retweet-check{{tweet.id}}').innerHTML = " "
    }
  },
  error: function(err){

  }
})
})

// function for counting remaining characters in the form
function countChar(val){
  var len = val.value.length;
  var textInput = document.getElementById('bio-input')
  if(len >= 200){
    val.value = val.value.substring(0, 200);
    textInput.setAttribute('readonly', 'true');
  }else{
    $('#charCount').text(200-len)
  };
}

// follow-unfollow ajax functionality
var interactForm = $('.interact-form');
// console.log(interactForm.serialize())
interactForm.submit(function(e){
  e.preventDefault();
  var thisForm = $(this);
  var formData = thisForm.serialize();
  var actionButton = thisForm.find("[type='submit']");
  var myProfileTab = $('.my-profile');
  $.ajax({
    url: "{% url 'profiles:interact' %}",
    type: "POST",
    data: formData,
    success: function(json){
      $('.followers-count').text(json.follower_count);
      if(json.followed){
        actionButton.text("Unfollow");
      }else if (json.unfollowed) {
        actionButton.text("Follow");
        myProfileTab.remove();
      }
    },
    error: function(err) {}
  })
})
// search results page follow-unfollow AJAX
var interactForm = $("[data-index='{{item.slug}}']");
interactForm.submit(function(e){
  e.preventDefault();
  var $this = $(this);
  var $data = $this.serialize();
  var $btn = $this.find("[type='submit']");
  $.ajax({
    url: "{% url 'profiles:interact' %}",
    type: "POST",
    data: $data,
    success: function(json){
      $(".{{item.nickname}}-followers").text(json.follower_count);
      if (json.followed) {
        $btn.text('Unfollow');
      }else if (json.unfollowed) {
        $btn.text('Follow');
      }
    },
    error: function(err){
      console.log(err)
    }
  })
})
// scrollable search list js
var resultsBox = $('.results-box');
var boxHeight = resultsBox.height();
// console.log(boxHeight)
var maxHeight = 534;
if (boxHeight > maxHeight) {
  resultsBox.css('overflow-x', 'hidden');
  resultsBox.css('overflow-y', 'scroll');
  resultsBox.css('height', maxHeight)
}
})
